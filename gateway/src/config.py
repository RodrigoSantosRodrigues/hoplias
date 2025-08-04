# /src/config.py
"""
                        Configuring Gateway
    ------------------------------------------------------------------------
                        Flask Environment Configuration
    ------------------------------------------------------------------------
    
"""
import os
import logging
import uuid
from dotenv import load_dotenv, find_dotenv
from flask import Flask
from pygelf import GelfUdpHandler

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv(find_dotenv())

class ContextFilter(logging.Filter):
    """
    Filtra logs e adiciona um request_id único para rastreabilidade.
    """
    def filter(self, record):
        record.request_id = str(uuid.uuid4())
        return True


class Development:
    """
    Configuração para ambiente de desenvolvimento
    """
    DEBUG = True
    TESTING = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')


class Production:
    """
    Configuração para ambiente de produção
    """
    DEBUG = False
    TESTING = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')


class Testing:
    """
    Configuração para ambiente de testes
    """
    TESTING = True
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')


app_config = {
    'development': Development,
    'production': Production,
    'testing': Testing
}

rabbit_config = {
    'AMQP_URI': f"amqp://{os.getenv('USER_MQ')}:{os.getenv('PASSWORD_MQ')}@{os.getenv('HOST_MQ')}"
}

logger = logging.getLogger('flask')
logger.setLevel(logging.DEBUG)
graylog_host = os.getenv("GRAYLOG_HOST")
graylog_port_udp = os.getenv("GRAYLOG_PORT_UDP")

logger.info(graylog_host)
logger.info(graylog_port_udp)

handler = GelfUdpHandler(host=graylog_host, port=int(graylog_port_udp), include_extra_fields=True)
logger.addHandler(handler)
logger.addFilter(ContextFilter())
