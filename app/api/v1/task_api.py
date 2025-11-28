from fastapi import APIRouter, Depends, HTTPException
from app.schemas.api_response import APIResponse
from app.schemas.task_req import TaskReq
from  app.services.task_service_factory import get_prompt_service
import json

router = APIRouter(prefix="/task", tags=["task"])

@router.post("/start", response_model=APIResponse)
def start(data: TaskReq):
    prompt_service =get_prompt_service(data.type)
    result = prompt_service.start(data)
    if isinstance(result, str):
        result = json.loads(result)
    return APIResponse.success(result)


@router.post("/correct", response_model=APIResponse)
def start(data: TaskReq):
    prompt_service = get_prompt_service(data.type)
    result = prompt_service.correct(data)
    if isinstance(result, str):
        result = json.loads(result)
    return APIResponse.success(result)


