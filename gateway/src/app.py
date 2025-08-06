# -*- coding: utf-8 -*-
# src/app.py
"""
                    API RPC Gateway MicroServices
    ------------------------------------------------------------------------


"""
from flask import Flask, render_template
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

from .config import app_config, logger
from .services.SegmentationService import segmentation_api as segmentation_blueprint
from .services.ClassificationService import classification_api as classification_blueprint
from .services.IdeogramService import ideogram_api as ideogram_blueprint


def create_app(env_name):
    """
    DOC API USING SWAGGER UI  
    Create app with Prometheus metrics
    """
    app = Flask(__name__)

    app.config.from_object(app_config[env_name])

    CORS(app, resources={r"/v1/*": {"origins": "*"}})

    #metrics = PrometheusMetrics(app)
 
    #metrics.init_app(app)

    ### swagger specific ###
    SWAGGER_URL = '/v1/apidocs'
    API_URL = '/static/api/openapi.yml'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Gateway API Service",
            'layout': 'BaseLayout',
            'filter': True
        }
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
    ### end swagger specific ###
  
    app.register_blueprint(segmentation_blueprint, url_prefix='/v1/api/segmentation/')
    app.register_blueprint(classification_blueprint, url_prefix='/v1/api/classification/')
    app.register_blueprint(ideogram_blueprint, url_prefix='/v1/api/ideogram/')

    return app
