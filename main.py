import sys
import uvicorn
import redis.asyncio as redis
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, Depends, APIRouter
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import str.routes.auth as auth
import str.routes.notes as notes
import str.routes.users as users
from str.conf.config import settings
from fastapi_limiter.depends import RateLimiter


app = FastAPI()


dependencies = []
if "pytest" not in sys.modules:
    dependencies.append(
        Depends(
            RateLimiter(...)
        )
    )
# api_router = APIRouter(prefix="/api", dependencies=dependencies)
# add your routes to `api_router`
# app.include_router(api_router)
app.include_router(notes.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
# async def startup():

@asynccontextmanager
async def lifespan(app):
    """Initialize the Redis connection and FastAPI limiter on startup.

    This function is executed during the startup event of the FastAPI application.
    It initializes a Redis connection using the host and port settings from the
    configuration, and then initializes the FastAPILimiter with this Redis instance.

    Raises:
        redis.ConnectionError: If the Redis server is unreachable.
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)

@app.get("/")
def read_root():
    """Read the root endpoint.

    This function handles GET requests to the root URL ("/") and returns a
    simple JSON message.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run('main:app', reload=True,  host="0.0.0.0", port=8000)
    """Run the FastAPI application.

    This block is executed when the script is run directly. It starts the
    Uvicorn server with the FastAPI application, enabling live reload and
    setting the host and port.

    Args:
        host (str): The hostname to listen on.
        port (int): The port number to listen on.
    """