# -*- coding: utf-8 -*-
"""

"""
import logging
import httpx
from ...helpers.mappers import RoutePathApiAiWithProxy, RoutePathApiAi, StatusCode


class ApiAiProxy:
    def __init__(self, config):
      self.__base_url = config.BASE_URL_API_AI
      self.__endpoints_map = {
        RoutePathApiAiWithProxy.CATEGORY_SUGESTION: RoutePathApiAi.CATEGORY_SUGESTION
      }
      self.__headers = { 'api-token': '' }

    def get_endpoints(self):
      return self.__endpoints_map

    async def api_proxy(self, subpath: str, data: dict):
      response = None

      url = f"{self.__base_url}{subpath}"
      timeout = httpx.Timeout(60.0)
      async with httpx.AsyncClient(timeout=timeout) as client:
        try:
          api_response = await client.post(url, json=data, headers=self.__headers)
          response = api_response.json()
          if response.get('status_code') != StatusCode.HTTP_OK:
            logging.error(f"HTTP response error: {response}")
        except httpx.HTTPStatusError as ex:
          logging.error(f"HTTP error: {ex}")
          raise ex
        except httpx.RequestError as ex:
          logging.error(f"Request error: {ex}")
          raise ex

      return response
