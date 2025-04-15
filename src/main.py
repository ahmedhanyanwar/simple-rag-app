from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession # To connect postgres
from sqlalchemy.orm import sessionmaker # To connect postgres

from routes import base, data , nlp 
from helpers.config import get_settings
from stores.llm import LLMProviderFactory
from stores.vectordb import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser

app = FastAPI()

@app.on_event("startup")
async def startup_span():
    settings = get_settings()

    # postgrss_conn = f"postgresql+asyncpg://username:password@host:port/database_name"
    postgrss_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    
    app.db_engine = create_async_engine(url=postgrss_conn)
    app.db_client = sessionmaker(
        app.db_engine,
        class_=AsyncSession, # To work well with fastapi
        expire_on_commit=False, # Because If True it will closed after any commit
    )

    llm_provider_factory = LLMProviderFactory(config=settings)
    vectordb_provider_factory = VectorDBProviderFactory(config=settings)
    
    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE
    )

    # vector db client
    app.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
    app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG
    )
    
@app.on_event("shutdown")
async def shutdown_span():
    app.db_engine.dispose() # To close the engine
    app.vectordb_client.disconnect()

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)