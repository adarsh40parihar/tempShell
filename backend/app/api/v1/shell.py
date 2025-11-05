from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import CommandExecute, CommandResponse, ShellStatus
from app.core.security import get_current_user
from app.services.k8s_service import K8sService
from app.db.database import Database
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
k8s_service = K8sService()

@router.post("/execute", response_model=CommandResponse)
async def execute_command(
    command: CommandExecute,
    current_user: dict = Depends(get_current_user)
):
    """
    Execute a command in the user's isolated shell environment
    
    - **command**: Shell command to execute (max 1000 characters)
    """
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        username = current_user["username"]
        
        # Get or create user pod
        cursor.execute(
            "SELECT shell_pod_id FROM users WHERE username = %s",
            (username,)
        )
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        pod_id = user_data.get('shell_pod_id')
        
        # Create pod if it doesn't exist
        if not pod_id:
            try:
                pod_id = k8s_service.create_user_pod(username)
                cursor.execute(
                    "UPDATE users SET shell_pod_id = %s WHERE username = %s",
                    (pod_id, username)
                )
                conn.commit()
                logger.info(f"Created new pod {pod_id} for user {username}")
            except Exception as e:
                logger.error(f"Failed to create pod for {username}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create shell environment"
                )
        
        # Execute command in pod
        try:
            output, exit_code = k8s_service.execute_command(pod_id, command.command)
        except Exception as e:
            logger.error(f"Command execution failed for {username}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Command execution failed"
            )
        
        logger.info(f"Command executed for {username} in pod {pod_id}: exit_code={exit_code}")
        
        return CommandResponse(
            output=output,
            exit_code=exit_code,
            executed_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in execute_command: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
    finally:
        cursor.close()
        conn.close()

@router.delete("/terminate")
async def terminate_shell(current_user: dict = Depends(get_current_user)):
    """
    Terminate the user's shell environment and delete the pod
    """
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        username = current_user["username"]
        
        # Get user's pod ID
        cursor.execute(
            "SELECT shell_pod_id FROM users WHERE username = %s",
            (username,)
        )
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        pod_id = user_data.get('shell_pod_id')
        
        if pod_id:
            try:
                k8s_service.delete_pod(pod_id)
                logger.info(f"Terminated pod {pod_id} for user {username}")
            except Exception as e:
                logger.error(f"Failed to delete pod {pod_id}: {e}")
                # Continue anyway to clean up database
        
        # Clear pod ID from database
        cursor.execute(
            "UPDATE users SET shell_pod_id = NULL WHERE username = %s",
            (username,)
        )
        conn.commit()
        
        return {
            "message": "Shell terminated successfully",
            "pod_id": pod_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error terminating shell for {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to terminate shell"
        )
    finally:
        cursor.close()
        conn.close()

@router.get("/status", response_model=ShellStatus)
async def get_shell_status(current_user: dict = Depends(get_current_user)):
    """
    Get the status of the user's shell environment
    """
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        username = current_user["username"]
        
        cursor.execute(
            "SELECT shell_pod_id FROM users WHERE username = %s",
            (username,)
        )
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        pod_id = user_data.get('shell_pod_id')
        
        if not pod_id:
            return ShellStatus(
                pod_id=None,
                status="not_created",
                created_at=None
            )
        
        # Get pod status from Kubernetes
        pod_status = k8s_service.get_pod_status(pod_id)
        
        return ShellStatus(
            pod_id=pod_id,
            status=pod_status["status"],
            created_at=pod_status["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting shell status for {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get shell status"
        )
    finally:
        cursor.close()
        conn.close()
