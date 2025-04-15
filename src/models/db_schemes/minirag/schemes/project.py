from sqlalchemy import Column, Integer, DateTime # Types
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .minirag_base import SQLAlchemyBase

class Project(SQLAlchemyBase):
    '''Project Schema.'''
    __tablename__ = "projects"  # To define the table name

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    # UUID: Universal Unique IDentifier for security and business purpose
    project_uuid = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    ) 

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(), # To put time directly when instance created
        nullable=False,
    ) 

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(), # To put time directly when instance upated
        nullable=True, # At creation it equal null
    )
    