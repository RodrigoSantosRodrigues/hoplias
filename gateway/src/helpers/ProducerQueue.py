# -*- coding: utf-8 -*-
"""
    ------------------------------------------------------------------------
         Sends a message to a queue without waiting for a response (Publish-Subscribe)
    
"""
import logging
from kombu import Connection, Exchange, Queue, Producer 
from ..config import rabbit_config

RABBITMQ_URI = rabbit_config.get('AMQP_URI')
EXCHANGE_NAME = "classification"

def producer_queue(event, data):
  try:
      exchange = Exchange(EXCHANGE_NAME, type="direct")
      queue = Queue(event, exchange=exchange)

      with Connection(RABBITMQ_URI) as conn:
          producer = Producer(conn)
      
          producer.publish(
              data,
              exchange=exchange,
              routing_key=event,
              declare=[queue]
          )
      return {"status": "success", "message": f"Event {event} sent to the queue."}
  except Exception as e:
      logging.error(f"Error sending event: {e}")
      return {"status": "error", "message": str(e)}
