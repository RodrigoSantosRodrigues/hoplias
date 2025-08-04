import os
import logging
import uuid
import graypy

from fastapi.logger import logger
from typing import Any
from pydantic import BaseSettings
from dotenv import load_dotenv, find_dotenv
from pygelf import GelfUdpHandler

from ..helpers.mappers import Mapper

load_dotenv(find_dotenv(filename="../../.env"))

class ContextFilter(logging.Filter):
  def filter(self, record):
    record.request_id = str(uuid.uuid4())
    return True

class Development(BaseSettings):
  """
  Development environment configuration
  """
  ENV : str =  Mapper.ENV_DEVELOPMENT
  REDOC_URL: str = "/documentation"
  DOCS_URL: str = "/doc"
  APP_HOST: str = os.getenv("APP_HOST")
  APP_PORT: int = os.getenv("APP_PORT")
  JWT_SIGNATURE_TOKEN: str = os.getenv("JWT_SIGNATURE_TOKEN")
  DB_USER: str = os.getenv("DB_USER")
  DB_PW: str = os.getenv("DB_PW")
  DB_HOST: str = os.getenv("DB_HOST")
  DB_PORT: str = os.getenv("DB_PORT")
  DB_API: str = os.getenv("DB_API")
  AWS_REGION: str = os.getenv("AWS_REGION")
  AWS_ACCESS_KEY_ID: str =os.getenv("AWS_ACCESS_KEY_ID")
  AWS_SECRET_ACCESS_KEY: str =os.getenv("AWS_SECRET_ACCESS_KEY")
  MAIL_SERVER: str = os.getenv("MAIL_SERVER")
  MAIL_PORT: int = os.getenv("MAIL_PORT")
  MAIL_USERNAME: str =os.getenv("MAIL_USERNAME")
  MAIL_FROM: str =os.getenv("MAIL_FROM")
  MAIL_PASSWORD: str =os.getenv("MAIL_PASSWORD")
  RECOVER_CODE_EXPIRATION_DAYS: str =os.getenv("RECOVER_CODE_EXPIRATION_DAYS")
  APP_PLATFORM_HOST: str = os.getenv("APP_PLATFORM_HOST")
  BASE_URL_API_GATEWAY: str = os.getenv("BASE_URL_API_GATEWAY")
  GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
  BASE_URL_API_AI: str = os.getenv("BASE_URL_API_AI")
  GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID")
  GCP_PRIVATE_KEY_ID: str = os.getenv("GCP_PRIVATE_KEY_ID")
  GCP_PRIVATE_KEY: str = os.getenv("GCP_PRIVATE_KEY")
  GCP_CLIENT_EMAIL: str = os.getenv("GCP_CLIENT_EMAIL")
  GCP_CLIENT_ID: str = os.getenv("GCP_CLIENT_ID")
  GCP_CERT_URL: str = os.getenv("GCP_CERT_URL")
  MAX_CONCURRENT_IO_LOAD_IMAGES: int = os.getenv("MAX_CONCURRENT_IO_LOAD_IMAGES")
  REDIS_URL: str = os.getenv("REDIS_URL")
  REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD")
  ALLOWED_IP_HOST: str = os.getenv("ALLOWED_IP_HOST")
  DESKTOP_MODE_AUTH: str = os.getenv("DESKTOP_MODE_AUTH")
  HOST_DOCUMENTS_DIR: str = os.getenv("HOST_DOCUMENTS_DIR")
  CHATBOT_SECRET_KEY: str = os.getenv("CHATBOT_SECRET_KEY")

  class Config:
    env_file = ".env"


class Production(BaseSettings):
  """
  Production environment configurations
  """
  ENV : str = Mapper.ENV_PRODUCTION
  REDOC_URL: str = "/documentation-dev"
  DOCS_URL: str = "/doc-dev"
  APP_HOST: str = os.getenv("APP_HOST")
  APP_PORT: int = os.getenv("APP_PORT")
  JWT_SIGNATURE_TOKEN: str = os.getenv("JWT_SIGNATURE_TOKEN")
  DB_USER: str = os.getenv("DB_USER")
  DB_PW: str = os.getenv("DB_PW")
  DB_HOST: str = os.getenv("DB_HOST")
  DB_PORT: str = os.getenv("DB_PORT")
  DB_API: str = os.getenv("DB_API")
  AWS_REGION: str = os.getenv("AWS_REGION")
  AWS_ACCESS_KEY_ID: str =os.getenv("AWS_ACCESS_KEY_ID")
  AWS_SECRET_ACCESS_KEY: str =os.getenv("AWS_SECRET_ACCESS_KEY")
  MAIL_SERVER: str = os.getenv("MAIL_SERVER")
  MAIL_PORT: int = os.getenv("MAIL_PORT")
  MAIL_USERNAME: str =os.getenv("MAIL_USERNAME")
  MAIL_FROM: str =os.getenv("MAIL_FROM")
  MAIL_PASSWORD: str =os.getenv("MAIL_PASSWORD")
  RECOVER_CODE_EXPIRATION_DAYS: str =os.getenv("RECOVER_CODE_EXPIRATION_DAYS")
  APP_PLATFORM_HOST: str = os.getenv("APP_PLATFORM_HOST")
  BASE_URL_API_GATEWAY: str = os.getenv("BASE_URL_API_GATEWAY")
  GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
  BASE_URL_API_AI: str = os.getenv("BASE_URL_API_AI")
  GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID")
  GCP_PRIVATE_KEY_ID: str = os.getenv("GCP_PRIVATE_KEY_ID")
  GCP_PRIVATE_KEY: str = os.getenv("GCP_PRIVATE_KEY")
  GCP_CLIENT_EMAIL: str = os.getenv("GCP_CLIENT_EMAIL")
  GCP_CLIENT_ID: str = os.getenv("GCP_CLIENT_ID")
  GCP_CERT_URL: str = os.getenv("GCP_CERT_URL")
  MAX_CONCURRENT_IO_LOAD_IMAGES: int = os.getenv("MAX_CONCURRENT_IO_LOAD_IMAGES")
  REDIS_URL: str = os.getenv("REDIS_URL")
  REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD")
  ALLOWED_IP_HOST: str = os.getenv("ALLOWED_IP_HOST")
  DESKTOP_MODE_AUTH: str = os.getenv("DESKTOP_MODE_AUTH")
  HOST_DOCUMENTS_DIR: str = os.getenv("HOST_DOCUMENTS_DIR")
  CHATBOT_SECRET_KEY: str = os.getenv("CHATBOT_SECRET_KEY")

  class Config:
    env_file = ".env"


class Testing(BaseSettings):
  """
  Development environment configuration
  """
  ENV : str = Mapper.ENV_TESTING
  REDOC_URL: str = None
  DOCS_URL: str = None
  APP_HOST: str = os.getenv("APP_HOST")
  APP_PORT: int = os.getenv("APP_PORT")
  JWT_SIGNATURE_TOKEN: str = os.getenv("JWT_SIGNATURE_TOKEN")
  DB_USER: str = os.getenv("DB_USER")
  DB_PW: str = os.getenv("DB_PW")
  DB_HOST: str = os.getenv("DB_HOST")
  DB_PORT: str = os.getenv("DB_PORT")
  DB_API: str = os.getenv("DB_API")
  AWS_REGION: str = os.getenv("AWS_REGION")
  AWS_ACCESS_KEY_ID: str =os.getenv("AWS_ACCESS_KEY_ID")
  AWS_SECRET_ACCESS_KEY: str =os.getenv("AWS_SECRET_ACCESS_KEY")
  MAIL_SERVER: str = os.getenv("MAIL_SERVER")
  MAIL_PORT: int = os.getenv("MAIL_PORT")
  MAIL_USERNAME: str =os.getenv("MAIL_USERNAME")
  MAIL_FROM: str =os.getenv("MAIL_FROM")
  MAIL_PASSWORD: str =os.getenv("MAIL_PASSWORD")
  RECOVER_CODE_EXPIRATION_DAYS: str =os.getenv("RECOVER_CODE_EXPIRATION_DAYS")
  APP_PLATFORM_HOST: str = os.getenv("APP_PLATFORM_HOST")
  BASE_URL_API_GATEWAY: str = os.getenv("BASE_URL_API_GATEWAY")
  GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
  BASE_URL_API_AI: str = os.getenv("BASE_URL_API_AI")
  GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID")
  GCP_PRIVATE_KEY_ID: str = os.getenv("GCP_PRIVATE_KEY_ID")
  GCP_PRIVATE_KEY: str = os.getenv("GCP_PRIVATE_KEY")
  GCP_CLIENT_EMAIL: str = os.getenv("GCP_CLIENT_EMAIL")
  GCP_CLIENT_ID: str = os.getenv("GCP_CLIENT_ID")
  GCP_CERT_URL: str = os.getenv("GCP_CERT_URL")
  MAX_CONCURRENT_IO_LOAD_IMAGES: int = os.getenv("MAX_CONCURRENT_IO_LOAD_IMAGES")
  REDIS_URL: str = os.getenv("REDIS_URL")
  REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD")
  ALLOWED_IP_HOST: str = os.getenv("ALLOWED_IP_HOST")
  DESKTOP_MODE_AUTH: str = os.getenv("DESKTOP_MODE_AUTH")
  HOST_DOCUMENTS_DIR: str = os.getenv("HOST_DOCUMENTS_DIR")
  CHATBOT_SECRET_KEY: str = os.getenv("CHATBOT_SECRET_KEY")

  class Config:
    env_file = ".env"

host_app = 'http://{0}:{1}'.format(os.getenv("APP_HOST"), os.getenv("APP_PORT"))
app_config = {
  'development': Development(),
  'production': Production(),
  'testing': Testing()
}
token_expires_in = os.getenv("TOKEN_EXPIRES_IN")
env_name = os.getenv("ENV")
allowed_ip_host = os.getenv("ALLOWED_IP_HOST")
db_name= os.getenv("DB_API")
db_connection = 'mongodb://{0}:{1}@{2}:{3}/{4}?authSource=admin'.format(
  app_config[env_name].DB_USER,
  app_config[env_name].DB_PW,
  app_config[env_name].DB_HOST,
  app_config[env_name].DB_PORT,
  app_config[env_name].DB_API
)

logger.setLevel(logging.DEBUG)
graylog_host = os.getenv("GRAYLOG_HOST")
graylog_port_udp = os.getenv("GRAYLOG_PORT_UDP")
logger.info(graylog_host)
logger.info(graylog_port_udp)
handler = GelfUdpHandler(host=graylog_host, port=int(graylog_port_udp), include_extra_fields=True)
logger.addHandler(handler)
logger.addFilter(ContextFilter())
