import inspect
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

DESKTOP_AND_LOCAL_ORIGINS = [
  "https://eloquent-monstera-5ebcf7.netlify.app",
  "http://localhost:3003",
  "http://localhost:3000",
  "http://127.0.0.1:3003",
  "http://127.0.0.1:3000",
]


def _parse_allowed_origins(raw):
  if not raw:
    return []
  cleaned = str(raw).strip().strip("'").strip('"')
  return [part.strip().strip("'\"") for part in cleaned.split() if part.strip()]

async def db_lifespan(app: FastAPI):
    # Startup
    app.database = db
    logger.info("Starting up")

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
  instrumentator.expose(app)

  # CORS must be added last so it is the outermost middleware. Otherwise
  # @app.middleware("http") can let OPTIONS hit POST routes (400/422).
  # Electron loads the Netlify SPA; Origin is that URL even when the API
  # is http://localhost:8005. ACAO must echo Origin, not the API host.
  allow_origins = list(dict.fromkeys(
    _parse_allowed_origins(allowed_ip_host) + DESKTOP_AND_LOCAL_ORIGINS
  ))
  cors_kwargs = {
    "allow_origins": allow_origins if env_name == "production" else ["*"],
    "allow_origin_regex": (
      r"https://.*\.netlify\.app|https?://(localhost|127\.0\.0\.1)(:\d+)?"
      if env_name == "production"
      else None
    ),
    "allow_credentials": False,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
  }
  if "allow_private_network" in inspect.signature(CORSMiddleware.__init__).parameters:
    # Public https Origin (Netlify) → private http://localhost (Chrome PNA)
    cors_kwargs["allow_private_network"] = True

  app.add_middleware(CORSMiddleware, **cors_kwargs)
  logger.error(f"CORS allow_origins={cors_kwargs['allow_origins']} env={env_name}")

  return app
