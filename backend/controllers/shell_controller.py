import os
import subprocess
import logging
from datetime import datetime

from models.shell import CommandRequest, CommandResponse, ShellStatus

logger = logging.getLogger(__name__)

BLOCKED_COMMANDS = {"shutdown", "reboot", "poweroff", "halt", "init", "telinit"}


def run_command(command: str, username: str, timeout: int = 10) -> tuple[str, int]:
    """
    Run a shell command safely inside an isolated per-user /tmp directory.
    - Hard timeout kills hung commands
    - Minimal environment prevents server secrets from leaking
    - Per-user working directory keeps sessions isolated from each other
    """
    cmd_name = command.strip().split()[0] if command.strip() else ""
    if cmd_name in BLOCKED_COMMANDS:
        return f"Error: '{cmd_name}' is not allowed.", 1

    work_dir = f"/tmp/tempshell_{username}"
    os.makedirs(work_dir, exist_ok=True)

    safe_env = {
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "HOME": work_dir,
        "TERM": "xterm-256color",
        "USER": username,
    }

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=work_dir,
            env=safe_env,
        )
        output = result.stdout
        if result.stderr:
            output += ("\n" if output else "") + result.stderr
        return output.strip() or "(no output)", result.returncode

    except subprocess.TimeoutExpired:
        logger.warning(f"Command timed out for user {username}")
        return f"Error: timed out after {timeout}s", 1
    except Exception as e:
        logger.error(f"Command error for {username}: {e}")
        return f"Error: {e}", 1


def execute(command: CommandRequest, username: str) -> CommandResponse:
    """Execute a command and return the result."""
    logger.info(f"[{username}] Running: {command.command!r}")
    output, exit_code = run_command(command.command, username)
    return CommandResponse(output=output, exit_code=exit_code, executed_at=datetime.utcnow())


def get_status(username: str) -> ShellStatus:
    """Return the current shell session status for a user."""
    work_dir = f"/tmp/tempshell_{username}"
    return ShellStatus(
        session_id=username,
        status="ready" if os.path.isdir(work_dir) else "not_started",
        created_at=None,
    )
