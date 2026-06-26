import subprocess
import logging
import time
import asyncio
from datetime import datetime

from models.shell import CommandRequest, CommandResponse, ShellStatus

logger = logging.getLogger(__name__)

# Commands always blocked before entering the container
BLOCKED_COMMANDS = {"shutdown", "reboot", "poweroff", "halt", "init", "telinit"}

CONTAINER_IMAGE = "alpine:latest"
IDLE_TIMEOUT_SECONDS = 10 * 60  # 10 minutes

# Tracks last activity time per username
container_last_active: dict[str, float] = {}

# Tracks current working directory per username inside their container
container_cwd: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Container helpers
# ---------------------------------------------------------------------------

def container_name(username: str) -> str:
    return f"tempshell_{username}"


def is_container_running(username: str) -> bool:
    """Returns True if the user's container is currently alive."""
    result = subprocess.run(
        ["docker", "inspect", "--format", "{{.State.Running}}", container_name(username)],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def start_container(username: str):
    """
    Create and start a long-running isolated container for the user.

    Isolation guarantees:
    - --network none       → no internet, no access to host DB or AWS metadata
    - --memory 128m        → hard memory cap per user
    - --cpus 0.5           → max half a CPU core
    - -v tempshell_vol_X   → user's own persistent disk at /workspace
    - sleep infinity        → keeps the container alive until we kill it
    """
    name = container_name(username)
    vol = f"tempshell_vol_{username}"

    subprocess.run(
        [
            "docker", "run", "-d",
            "--name", name,
            "--network", "none",
            "--memory", "128m",
            "--cpus", "0.5",
            "--tmpfs", "/tmp:rw,size=50m",   # writable /tmp inside container
            "-v", f"{vol}:/workspace",        # persistent user workspace
            "-w", "/workspace",               # default working directory
            CONTAINER_IMAGE,
            "sleep", "infinity",             # keep container alive
        ],
        capture_output=True,
        check=True,
    )
    logger.info(f"Started container for: {username}")


def ensure_container(username: str):
    """Start the user's container if it isn't already running."""
    if not is_container_running(username):
        # Remove any stopped/dead container with the same name first
        subprocess.run(["docker", "rm", "-f", container_name(username)], capture_output=True)
        start_container(username)


def stop_container(username: str):
    """Force-remove a user's container and clear their activity / CWD records."""
    subprocess.run(["docker", "rm", "-f", container_name(username)], capture_output=True)
    container_last_active.pop(username, None)
    container_cwd.pop(username, None)
    logger.info(f"Stopped idle container for: {username}")


# ---------------------------------------------------------------------------
# Background task — kills containers idle for more than 10 minutes
# ---------------------------------------------------------------------------

async def cleanup_idle_containers():
    """
    Runs forever in the background.
    Every 60 seconds it checks all tracked containers and removes any
    that haven't run a command in the last 10 minutes.
    """
    while True:
        await asyncio.sleep(60)  # check once per minute
        now = time.time()
        idle_users = [
            username
            for username, last_active in list(container_last_active.items())
            if now - last_active > IDLE_TIMEOUT_SECONDS
        ]
        for username in idle_users:
            logger.info(f"Container idle >10min — stopping: {username}")
            stop_container(username)


# ---------------------------------------------------------------------------
# Command execution
# ---------------------------------------------------------------------------

def run_command(command: str, username: str, timeout: int = 10) -> tuple[str, int]:
    """
    Execute a shell command inside the user's isolated Docker container.

    Flow:
    1. Block hardcoded dangerous commands
    2. Make sure the container is running (start it if not)
    3. Update last-activity timestamp
    4. Wrap the user command to run inside their last known CWD, and
       then append a delimiter + `pwd` so we can track directory changes.
    5. Run: docker exec <container> sh -c "<wrapped_command>"
    6. Extract user output and the new CWD, update tracking, and return.
    """
    # Step 1 — static blocklist
    cmd_name = command.strip().split()[0] if command.strip() else ""
    if cmd_name in BLOCKED_COMMANDS:
        return f"Error: '{cmd_name}' is not allowed.", 1

    # Step 2 — ensure container is running
    try:
        ensure_container(username)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start container for {username}: {e.stderr}")
        return "Error: could not start your shell environment.", 1

    # Step 3 — update activity timestamp
    container_last_active[username] = time.time()

    # Step 4 — Get last known CWD (default to /workspace) and wrap command
    cwd = container_cwd.get(username, "/workspace")
    delimiter = "---TEMPSHELL_CWD---"
    
    # We change directory to CWD (or fall back to /workspace if CWD doesn't exist).
    # Then execute the user command, print the delimiter, and print the resulting CWD.
    wrapped_command = (
        f"(cd {cwd} 2>/dev/null || cd /workspace) && {command} ; "
        f"echo -n '{delimiter}' ; pwd"
    )

    # Step 5 — execute inside the container
    try:
        result = subprocess.run(
            ["docker", "exec", container_name(username), "sh", "-c", wrapped_command],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        
        output = result.stdout
        if result.stderr:
            output += ("\n" if output else "") + result.stderr

        # Step 6 — parse output to separate user output from the new CWD
        if delimiter in output:
            user_output, new_cwd = output.rsplit(delimiter, 1)
            new_cwd = new_cwd.strip()
            if new_cwd:
                container_cwd[username] = new_cwd
            output = user_output
        
        return output.strip() or "(no output)", result.returncode

    except subprocess.TimeoutExpired:
        logger.warning(f"Command timed out for user {username}")
        return f"Error: timed out after {timeout}s", 1
    except Exception as e:
        logger.error(f"Command error for {username}: {e}")
        return f"Error: {e}", 1


# ---------------------------------------------------------------------------
# Controller functions called by the router
# ---------------------------------------------------------------------------

def execute(command: CommandRequest, username: str) -> CommandResponse:
    logger.info(f"[{username}] Running: {command.command!r}")
    output, exit_code = run_command(command.command, username)
    # Always return the current tracked CWD so the frontend prompt stays in sync
    current_cwd = container_cwd.get(username, "/workspace")
    return CommandResponse(
        output=output,
        exit_code=exit_code,
        executed_at=datetime.utcnow(),
        cwd=current_cwd,
    )


def get_status(username: str) -> ShellStatus:
    running = is_container_running(username)
    return ShellStatus(
        session_id=username,
        status="ready" if running else "not_started",
        created_at=None,
    )
