import logging
import pickle
import base64
import os
from functools import wraps
from typing import Optional, Callable, Any
from urllib.parse import urlparse, parse_qs
import redis  # trocado para redis síncrono
from cachetools import TTLCache
from dotenv import load_dotenv
load_dotenv()


LOCAL_CACHE = TTLCache(maxsize=1000, ttl=300)
REDIS_TIMEOUT = 2  # seconds
CACHE_EXPIRATION = 3600 # 1 hour
CIRCUIT_BREAKER_THRESHOLD = 3

class BaseRedisCache:
    def __init__(self):
        self.redis = None
        self.redis_url = os.getenv("REDIS_URL")
        self.redis_password = os.getenv("REDIS_PASSWORD")
        self.circuit_breaker = False
        self.failures = 0

    def initialize(self):
        try:
            if not self.redis and not self.circuit_breaker:
                self.redis = redis.from_url(
                    url=self.redis_url,
                    password=self.redis_password,
                    socket_timeout=REDIS_TIMEOUT,
                    socket_connect_timeout=REDIS_TIMEOUT,
                    health_check_interval=30,
                    decode_responses=False,
                )
                self.redis.ping()
                self.failures = 0
        except Exception as e:
            self.handle_redis_failure(e)
            raise

    def handle_redis_failure(self, error):
        self.failures += 1
        logging.warning(f"Redis failure #{self.failures}: {str(error)}")
        
        if self.failures >= CIRCUIT_BREAKER_THRESHOLD:
            self.circuit_breaker = True
            logging.error("Redis Circuit Breaker activated - falling back to local cache")
            
        if self.redis:
            self._safe_close()

    def _safe_close(self):
        try:
            self.redis.close()
        except Exception as e:
            logging.warning(f"Error closing Redis connection: {str(e)}")
        finally:
            self.redis = None

    def get(self, key: str) -> Any:
        if self.circuit_breaker or not self.redis:
            return LOCAL_CACHE.get(key)
            
        try:
            data = self.redis.get(key)
            if data:
                return pickle.loads(data)
        except Exception as e:
            self.handle_redis_failure(e)
            return LOCAL_CACHE.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        LOCAL_CACHE[key] = value
        
        if self.circuit_breaker or not self.redis:
            return
            
        try:
            serialized = pickle.dumps(value)
            self.redis.set(
                key, 
                serialized, 
                ex=ttl or CACHE_EXPIRATION
            )
        except Exception as e:
            self.handle_redis_failure(e)

    def delete(self, *keys: str) -> int:
        count = 0
        for key in keys:
            if key in LOCAL_CACHE:
                del LOCAL_CACHE[key]
                count += 1
                
        if self.circuit_breaker or not self.redis:
            return count
            
        try:
            deleted = self.redis.delete(*keys)
            return count + deleted
        except Exception as e:
            self.handle_redis_failure(e)
            return count

    def close(self):
        if self.redis:
            self._safe_close()

def with_cache(cache_key_fn: Callable[..., str]):
    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                if not hasattr(self, '_cache') or self._cache is None:
                    try:
                        self._cache = BaseRedisCache()
                        self._cache.initialize()
                    except Exception as cache_init_error:
                        logging.error(f"Cache initialization failed: {cache_init_error}")
                        return method(self, *args, **kwargs)
                
                cache_key = cache_key_fn(self, *args, **kwargs)
                try:
                    cached = self._cache.get(cache_key)
                    if cached is not None:
                        if isinstance(cached, str) and cached.startswith("data:'image/png';base64,"):
                            return cached
                        elif isinstance(cached, bytes):
                            binary = base64.b64encode(cached).decode('utf-8')
                            return f"data:'image/png';base64,{binary}"
                except Exception as cache_get_error:
                    logging.error(f"Cache get operation failed: {cache_get_error}")
                
                result = method(self, *args, **kwargs)
                
                if result:
                    try:
                        to_store = result
                        if isinstance(result, str) and result.startswith("data:image"):
                            to_store = base64.b64decode(result.split(",")[1])
                        self._cache.set(cache_key, to_store)
                    except Exception as cache_set_error:
                        logging.error(f"Cache set operation failed: {cache_set_error}")
                
                return result
                
            except Exception as main_error:
                logging.error(f"Error in cached method {method.__name__}: {main_error}")
                return method(self, *args, **kwargs)
                
        return wrapper
    return decorator
