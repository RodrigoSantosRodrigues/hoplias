import os
import uvicorn
from dotenv import load_dotenv, find_dotenv

from src.app import create_app

load_dotenv(find_dotenv(filename='.env'))

app = create_app(os.getenv('ENV'))

if __name__ == '__main__':
  port = os.getenv('APP_PORT')
  host = os.getenv('APP_HOST')
  # run app
  uvicorn.run('run:app', host=host, port=int(port), debug=True, reload=True)
