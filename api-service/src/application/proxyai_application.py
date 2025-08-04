from typing import Any
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Dict, Any
# from sklearn.feature_extraction.text import TfidfVectorizer
# import spacy
# from threading import Lock
#from functools import lru_cache

from ..domain.interfaces.request.tag_request import (
  CreateTag
)
from ..domain.enums.messages_enum import MessagesEnum
from ..infra.base.api_ai_proxy import ApiAiProxy
from ..usecase.ai_usecase import AiUseCase
from ..domain.enums.messages_enum import MessagesEnum


# class NLPModel:
#   _instance = None
#   _lock = Lock()

#   @classmethod
#   def get_instance(cls):
#     with cls._lock:
#       if cls._instance is None:
#         cls._instance = spacy.load("pt_core_news_lg")
#       return cls._instance

# def get_nlp():
#   return NLPModel.get_instance()

async def create_request_(
  data: CreateTag,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  subpath: str
) -> Dict:
  return {
    'success': False,
    'message': MessagesEnum.NOT_FOUND
  }

  # api_ai_proxy = ApiAiProxy(request.app.config)
  
  # endpoints_map = api_ai_proxy.get_endpoints()
  # endpoint_url = endpoints_map.get(subpath)
  # if not endpoint_url:
  #   return {
  #   'success': False,
  #   'message': MessagesEnum.NOT_FOUND
  # }

  # ai_usecase = AiUseCase(
  #   data=data,
  #   request=request, 
  #   db=db,
  #   auth=auth,
  #   endpoint_url=endpoint_url
  # )

  # response = await ai_usecase.orchestrator()

  # if not response:
  #   return {
  #   'success': False,
  #   'message': MessagesEnum.ERROR_IN_REQUEST_GATEWAY
  # }
 
  # return {
  #   'success': True,
  #   'message': MessagesEnum.CREATED,
  #   'data': response
  # }


# @lru_cache(maxsize=1)  # Cache
# def load_spacy_model():
#   return spacy.load("pt_core_news_lg")

async def create_request(
  data: CreateTag,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  subpath: str
) -> Any:
  return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  #nlp = spacy.load("pt_core_news_lg")
  #nlp = load_spacy_model()
  # nlp = get_nlp()
  # def preprocess_text(text):
  #   text = text.lower()

  #   doc = nlp(text)
  #   tokens = [token.text for token in doc if not token.is_stop]
  #   text = ' '.join(tokens)

  #   text = ''.join(e for e in text if e.isalnum() or e.isspace())

  #   doc = nlp(text)
  #   lemmas = [token.lemma_ for token in doc if not token.is_digit and not token.is_punct]
  #   text = ' '.join(lemmas)

  #   return text

  # name_preprocessada = preprocess_text(data.name)
  # descricao_preprocessada = preprocess_text(data.description)

  # vectorizer = TfidfVectorizer()
  # vectorizer.fit_transform([name_preprocessada, descricao_preprocessada])
 
  # sugestions =  list(vectorizer.get_feature_names_out())

  # return {
  #   'success': True,
  #   'message': MessagesEnum.CREATED,
  #   'data': sugestions
  # }
