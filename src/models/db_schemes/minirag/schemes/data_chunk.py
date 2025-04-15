from sqlalchemy import Column, Integer, String, DateTime, ForeignKey # Types
from sqlalchemy import func
# JSONB == JSON Binary It better than JSON on reading but slow at writing 
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Index
from pydantic import BaseModel
import uuid

from .minirag_base import SQLAlchemyBase

class DataChunk(SQLAlchemyBase):
    '''Data chunk Schema.'''
   
    __tablename__ = "chunks"  # To define the table name

    chunk_id = Column(Integer, primary_key=True, autoincrement=True)
    # UUID: Universal Unique IDentifier for security and business purpose
    chunk_uuid = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
 
    chunk_text = Column(String, nullable=False)
    chunk_metadata = Column(JSONB, nullable=True)
    chunk_order = Column(Integer, nullable=False)
    Column()
    chunk_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    chunk_asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True) 

    # This line says: "This model has a many-to-one relationship with the Project model."
    # The 'project' attribute will give you the Project instance this Asset belongs to.
    # The 'back_populates="assets"' tells SQLAlchemy that the Project model has an 'assets' relationship
    # that refers back to all Asset instances linked to it.
    project = relationship("Project", back_populates="chunks")
    asset = relationship("Asset", back_populates="chunks")

    # Adding indexes to improve query performance on foreign key columns:
    # - 'ix_chunk_project_id': Indexes 'chunk_project_id', which links each chunk to a project.
    #    This improves the performance of queries like:
    #    SELECT * FROM chunks WHERE chunk_project_id = ?
    #
    # - 'ix_chunk_asset_id': Indexes 'chunk_asset_id', which links each chunk to an asset.
    #    This helps when fetching all chunks related to a specific asset efficiently.
    __table_args__ = (
        Index('ix_chunk_project_id', chunk_project_id),
        Index('ix_chunk_asset_id', chunk_asset_id),
    )


class RetrievedDocument(BaseModel):
    '''Used to have same types of retrieved document returned from any provider.'''
    text: str
    score: float
