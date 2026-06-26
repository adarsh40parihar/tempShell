from fastapi import APIRouter, Depends

from models.shell import CommandRequest, CommandResponse, ShellStatus
from utils.security import get_current_user
import controllers.shell_controller as shell_controller

router = APIRouter(prefix="/shell", tags=["Shell"])


@router.post("/execute", response_model=CommandResponse)
async def execute(command: CommandRequest, current_user: dict = Depends(get_current_user)):
    return shell_controller.execute(command, current_user["username"])


@router.get("/status", response_model=ShellStatus)
async def status(current_user: dict = Depends(get_current_user)):
    return shell_controller.get_status(current_user["username"])
