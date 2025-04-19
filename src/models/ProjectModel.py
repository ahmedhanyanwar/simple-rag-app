from sqlalchemy.future import select
from sqlalchemy import func

from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.db_client = db_client
       
    # These because We can't call create_instance from __init__
    #  because we can't put await inside it so this is beauty sol
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance

    async def create_project(self, project: Project):
        
        # Begin an asynchronous context manager for handling the database session.
        # The `db_client` is a function that returns an active DB client/connection.
        async with self.db_client() as session:
            # Start a transaction block. `session.begin()` ensures that any changes made within this block are handled together.
            async with session.begin():
                # Add the `project` object to the session. This marks it for insertion into the database.
                session.add(project)
            
            # Commit the transaction, which will save all changes (in this case, adding the `project`) to the database.
            await session.commit()
            
            # Refresh the `project` object with the latest data from the database.
            # This is typically done after committing changes to ensure the object has up-to-date values.
            await session.refresh(project)

        return project
    
    async def get_or_create_project(self, project_id: int):
        async with self.db_client() as session:
            async with session.begin():
                stmt = select(Project).where(Project.project_id == project_id)
                query = await session.execute(stmt)
                project = query.scalar_one_or_none()
                if project is None:
                    project_rec = Project(project_id= project_id)
                    project = await self.create_project(project=project_rec)
                    return project
                else:
                    return project
                
    # This called pagination to avoid the overload
    async def get_all_projects(self, page: int=1, page_size: int=10):
        
        async with self.db_client() as session:
            async with session.begin():
                total_documents = await session.execute(
                    select(func.count( Project.project_id))
                )
                total_documents = total_documents.scalar_one()
                
                total_pages = total_documents // page_size
                if total_pages % page_size > 0:
                    total_pages += 1
                
                query = select(Project).offset((page - 1) * page_size).limit(page_size)
                projects = await session.execute(query).scalars().all()
        return projects , total_pages

