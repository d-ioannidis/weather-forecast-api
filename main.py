"""
This is the main module of the application.
It defines the FastAPI application and its routes.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db
from app.routers.forecast import router as forecast_router

@asynccontextmanager
async def app_lifespan(fastapi_app: FastAPI):
    """
    This is an async context manager that is called on application startup.
    It creates the database file and tables if they do not already exist.
    It also cleans up and releases the resources on application shutdown.

    Args:
        app: The FastAPI application.

    Yields:
        None
    """
    # Use the fastapi_app argument to access some attribute or method
    print(fastapi_app.title)
    init_db()
    yield
    # Clean up
    print("Cleaning up and release the resources")


app = FastAPI(
    title="FastAPI Weather Forecast",  # Set the title of the application
    description="This project is a FastAPI-based application",
    version="1.0.0",
    lifespan=app_lifespan)

origins = [
    "http://127.0.0.1:8000/",
    "http://127.0.0.1",
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    #exclude_methods=["DELETE"],
)

app.include_router(forecast_router, prefix="/forecast", tags=["forecast"])

@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "The API is healthy"}
