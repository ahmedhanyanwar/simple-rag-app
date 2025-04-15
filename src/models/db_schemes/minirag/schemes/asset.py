from sqlalchemy import Column, Integer, String, DateTime, ForeignKey # Types
from sqlalchemy import func
# JSONB == JSON Binary It better than JSON on reading but slow at writing 
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import uuid

from .minirag_base import SQLAlchemyBase

class Asset(SQLAlchemyBase):
    '''Asset Schema.'''
    __tablename__ = "assets"  # To define the table name
 
    asset_id = Column(Integer, primary_key=True, autoincrement=True)
    # UUID: Universal Unique IDentifier for security and business purpose
    asset_uuid = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    asset_type = Column(String, nullable=False)
    asset_name = Column(String, nullable=False) 
    asset_size = Column(Integer, nullable=False)

    asset_config = Column(JSONB, nullable=True)

    # ForeignKey has relationship with another table called projects
    asset_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True) 

    # This line says: "This model has a many-to-one relationship with the Project model."
    # The 'project' attribute will give you the Project instance this Asset belongs to.
    # The 'back_populates="assets"' tells SQLAlchemy that the Project model has an 'assets' relationship
    # that refers back to all Asset instances linked to it.
    project = relationship("Project", back_populates="assets")

    # Adding indexes to improve query performance:
    # - 'ix_assert_project_id': Indexes 'asset_project_id', which is a foreign key to 'projects.project_id'.
    #    This significantly speeds up queries that filter or join by project, such as:
    #    SELECT * FROM assets WHERE asset_project_id = ?
    #
    # - 'ix_asset_type': Indexes 'asset_type' to optimize queries that filter or group assets by type.
    __table_args__ = (
        Index('ix_assert_project_id', asset_project_id),
        Index('ix_asset_type', asset_type),
    )
