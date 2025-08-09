from fastapi.openapi.utils import get_openapi


def open_api(app):
  def custom_openapi():
    if app.openapi_schema:
      return app.openapi_schema
    openapi_schema = get_openapi(
      title="API Service hoplias",
      version="1.0.0-alpha",
      description="This is a very custom for hoplias",
      routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
      "url": 'https://eloquent-monstera-5ebcf7.netlify.app/static/media/logo-new.db3de9fe.png'
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

  return custom_openapi
