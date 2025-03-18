from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv(".env")  #load in main so all modules can see

from routes import base

app = FastAPI()

app.include_router(base.base_router)
