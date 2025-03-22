# User will give me the name of the file so I want
#  to validate it's type
from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    file_id: str
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0 # do_var mean tha this var need to take action
    