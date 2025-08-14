# -*- coding: utf-8 -*-
"""
                        API Gateway
    ------------------------------------------------------------------------
                           HTTP API Proxy
    ------------------------------------------------------------------------
         Sends a request to an external API, acting as a proxy
"""
import logging
import httpx
from ...helpers.mappers import RoutePathWithProxy, RoutePathGateway, StatusCode


class RpcProxy:
    def __init__(self, config):
      self.__base_url = config.BASE_URL_API_GATEWAY
      self.__endpoints_map = {
        RoutePathWithProxy.SEGMENTATION: RoutePathGateway.SEGMENTATION,
        RoutePathWithProxy.IDEOGRAM: RoutePathGateway.IDEOGRAM,
        RoutePathWithProxy.CLASSIFICATION_CENTROMERE: RoutePathGateway.CLASSIFICATION_CENTROMERE,
        RoutePathWithProxy.CLASSIFICATION: RoutePathGateway.CLASSIFICATION,
        RoutePathWithProxy.PRECLASSIFICATION: RoutePathGateway.PRECLASSIFICATION,
        RoutePathWithProxy.CONVERT_TO_JPG: RoutePathGateway.CONVERT_TO_JPG,
      }
      self.__headers = { 'api-token': config.RPC_GATEWAY_KEY }

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
        except httpx.HTTPStatusError as ex:
          logging.error(f"HTTP error: {ex}")
          return False
        except httpx.RequestError as ex:
          logging.error(f"Request error: {ex}")
          return False

      return response
