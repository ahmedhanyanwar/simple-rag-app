from .VectorDBEnums import VectorDBEnums
from .providers import QdrantDBProvider
from controllers import BaseController

class VectorDBProviderFactory:
    def __init__(self, config: dict):
        self.config = config
        self.base_controller = BaseController()

    def create(self, provider: str):
        if provider == VectorDBEnums.QDRANT.value:
            db_path = self.base_controller.get_database_path(db_name=self.config.VECTOR_DB_PATH)
            return QdrantDBProvider(
                db_path= db_path,
                distance_method=self.config.VECTOR_DB_DIATANCE_METHOD
            )
                
        return None
    