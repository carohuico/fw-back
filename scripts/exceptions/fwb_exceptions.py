from pydantic import BaseModel
from typing import Any, Optional

class FWBException(Exception):
    def __init__(self, message, errors):
        self.errors = errors
        self.message = message
        super().__init__(self.message)
        # self.errors = errors

class CustomException(BaseModel):
    status: str = "failed"
    message: Optional[str]
    data: Optional[Any]

class FWBHomeException(Exception):
    pass

class FWBPLMException(FWBException):
    pass

class FWBUserValidationException(FWBException):
    pass

