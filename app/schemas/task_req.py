from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, List, Union, Dict, Any
from datetime import datetime
from enum import Enum
class TaskReq(BaseModel):
    type: str = Field(..., description="任务类型")
    subtype: str = Field(..., description="任务子类型:start:开始,correct：更正,hint：提示")
    language:str = Field(..., description="语言：en,zh")
    domain: Optional[str] = Field(None, description="主题")
    subdomain: Optional[str] = Field(None, description="子主题")
    question_type: Optional[str] = Field(None, description="大作文题目类型")
    original_article: Optional[str] = Field(None, description="原始文章")
    answers:  Optional[Dict] = Field(default=None,description="答案")
    class Config:
        from_attributes = True

