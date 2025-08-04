# -*- coding: utf-8 -*-
#/src/helpers/CallApiProxy.py
"""
                        API Gateway
    ------------------------------------------------------------------------
                           HTTP API Proxy
    ------------------------------------------------------------------------
         Sends a request to an external API, acting as a proxy
"""
import logging
import httpx


class AiGptClient:
  def __init__(self, config):
    self.__endpoint_gpt = 'https://api.openai.com/v1/chat/completions'
    self.__headers = { 
      "Authorization": f"Bearer {config.AI_GPT_API_KEY}",
      "Content-Type": "application/json"
    }

  async def api_request(self, prompt: str) -> str:
    response = None
    data = {
      "model": "gpt-3.5-turbo",
      "messages": [{"role": "user", "content": prompt}]
    }
    url = self.__endpoint_gpt
    timeout = httpx.Timeout(5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
      try:
        api_response = await client.post(url, json=data, headers=self.__headers)
        response = api_response.json()["choices"][0]["message"]["content"]
      except httpx.HTTPStatusError as ex:
        logging.error(f"HTTP error: {ex}")
        return False
      except httpx.RequestError as ex:
        logging.error(f"Request error: {ex}")
        return False

    return response
