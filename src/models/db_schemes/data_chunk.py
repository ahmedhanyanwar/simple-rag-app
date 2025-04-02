from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0) # gt --> Greater than
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId

    class Config:
        arbitrary_types_allowed = True
    
        # This is the shape of indicies
    @classmethod
    def get_indexes(cls):
        
        return [
            {
                "key": [
                    ("chunk_project_id", 1)  # 1 means ascending -1 means des
                ],
                "name": "chunk_project_id_index_1",
                "unique": False
            }
        ]
