import logging
import os
import requests

class ClientGoogleAuth():
  def __init__(self, config):
    self.__client_id = config.GOOGLE_CLIENT_ID
    self.__google_token_info_url = "https://oauth2.googleapis.com/tokeninfo"

  def validate_google_token(self, token: str):
    try:
      response = requests.get(f"{self.__google_token_info_url}?id_token={token}")
      
      if response.status_code != 200:
          return False

      google_data = response.json()
      
      if google_data.get("aud") != self.__client_id:
          return False

      user_info = {
          "google_id": google_data.get("sub"),
          "email": google_data.get("email"),
          "name": google_data.get("name"),
          "picture": google_data.get("picture")
      }
      return user_info

    except Exception as e:
      logging.error(e)
      return False
