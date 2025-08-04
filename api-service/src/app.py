import logging
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from .helpers.open_api import open_api
from .routes import api_router
from .infra.config import app_config, allowed_ip_host, logger
from .infra.base.db import db

async def db_lifespan(app: FastAPI):
    # Startup
    app.database = db

    yield
    # Shutdown
    app.mongodb_client.close()

def create_app(env_name):
  config = app_config[env_name]

  app = FastAPI(
    title='API Service Hoplias',
    redoc_url=config.REDOC_URL,
    docs_url=config.DOCS_URL,
    lifespan=db_lifespan
  )
  logger.error(f"Starting app in {env_name} environment")

  hosts = allowed_ip_host.strip().split()
  app.add_middleware(
    CORSMiddleware,
    allow_origins=hosts if env_name == 'production' else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
  )

  app.mount("/static", StaticFiles(directory="src/static"), name="static")

  app.config = config

  app.include_router(api_router, prefix='/api/v1')

  app.openapi = open_api(app)

  @app.get("/")
  def helth_check():
    return {"status_code": 200, "message": "Success"}

  @app.middleware("http")
  async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
      request.state.db = db
      response = await call_next(request)
    finally:
      pass
    return response

  add_pagination(app)

  @app.middleware("http")
  async def log_dispatch(request: Request, call_next):
    try:
      response = await call_next(request)
      logger.info(
          f"Request: {request.method} {request.url}",
          extra={
              "request": {"method": request.method, "url": str(request.url)},
              "response": {"status_code": response.status_code},
              "headers": dict(request.headers),
              "ip": request.client.host
          },
      )
      return response
    except Exception as e:
      logger.error(f"An error occurred: {e}", exc_info=True)
      raise

  instrumentator = Instrumentator().instrument(app)

  @app.on_event("startup")
  async def startup():
    instrumentator.expose(app)
    logger.info("Starting up")

  return app
