# -*- coding: utf-8 -*-
import logging
from eventlet import monkey_patch
from nameko.events import EventDispatcher
from nameko_amqp_retry import entrypoint_retry
from nameko.rpc import rpc

from nameko.messaging import Publisher, consume
from kombu.messaging import Exchange, Queue

from .controllers.CentromereControllerv2Beta import CentromereControllerv2Beta
from .controllers.ClassificationControllerV2Beta import ClassificationControllerV2beta
from .controllers.ConsumerCentromereControllerv2Beta import ConsumerCentromereControllerv2Beta
from .controllers.ConsumerClassificationControllerV2Beta import ConsumerClassificationControllerV2beta
from .db.Conect import MongoDB

monkey_patch()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

monitoring_exchange = Exchange(name="classification")
monitoring_exchange_ideogram = Exchange(name="ideogram")
centromere_queue = Queue(name="centromere_queue", routing_key="centromere_queue", exchange="classification")
preclassification_queue = Queue(name="preclassification_queue", routing_key="preclassification_queue", exchange="classification")
classification_queue = Queue(name="classification_queue", routing_key="classification_queue", exchange="classification")


class Centromere:
	name = 'classification'
	event_dispatcher = EventDispatcher()
	publish = Publisher(exchange=monitoring_exchange)
	publish_ideogram = Publisher(exchange=monitoring_exchange_ideogram)
	db = MongoDB()

	@rpc
	@entrypoint_retry(
        limit=5,
        schedule=(500, 600, 700, 800, 900),
    )
	def centromere(self, data):
		"""
			This is an RPC call function. Receive a json hoplias.

			params:
				json: 
					type: hoplias

			return:
				json: 
					type: hoplias
		"""
		try:
			image = CentromereControllerv2Beta(logger, data)
			payload = image.centromere()
			# self.event_dispatcher('centromere', {
			# 		'centromere': payload,
			# })
			return payload
		except Exception as e:
			logger.error("Error: %s", str(e))
			raise e

	@rpc
	@entrypoint_retry(
        limit=5,
        schedule=(500, 600, 700, 800, 900),
    )
	def preclassification(self, data):
		"""
			This is an RPC call function. Receive a json hoplias.

			params:
				json: 
					type: hoplias

			return:
				json: 
					type: hoplias
		"""
		try:
			image = ClassificationControllerV2beta(self.db, self.publish, self.publish_ideogram, logger, data)
			payload = image.preclassify()
			return payload
		except Exception as e:
			logger.error("Error: %s", str(e))
			raise e

	@rpc
	@entrypoint_retry(
        limit=5,
        schedule=(500, 600, 700, 800, 900),
    )
	def classification(self, data):
		"""Queue classification"""
		try:
			process_images_batch = ClassificationControllerV2beta(self.db, self.publish, self.publish_ideogram, logger, data)
			payload = process_images_batch.process_chrom(data)

			return payload
		except Exception as e:
			logger.error("Error: %s", str(e))
			raise e

	def on_status(self, data):
		self.publish("centromere_queue", data)
		self.publish("preclassification_queue", data)

	@consume(queue=centromere_queue)
	@entrypoint_retry(
        limit=5,
        schedule=(500, 600, 700, 800, 900),
    )
	def handle_centromere_queue(self, payload):
		#logger.info("Received handle_centromere_queue event: %s", payload)
		try:
			process_background = ConsumerCentromereControllerv2Beta(self.db, self.publish, logger)
			process_background.process_chrom(payload)
		except Exception as e:
			logger.error("Error: %s", str(e))
			raise e

	@consume(queue=preclassification_queue)
	@entrypoint_retry(
        limit=5,
        schedule=(500, 600, 700, 800, 900),
    )
	def handle_preclassification_queue(self, payload):
		#logger.info("Received preclassification_queue event: %s", payload)
		try:
			process_background = ConsumerClassificationControllerV2beta(self.db, logger)
			process_background.process_chrom(payload)
		except Exception as e:
			logger.error("Error: %s", str(e))
			raise e

	@consume(queue=classification_queue)
	@entrypoint_retry(
        limit=5,
        schedule=(500, 600, 700, 800, 900),
    )
	def handle_classification_queue(self, payload):
		#logger.info("Received classification_queue event: %s", payload)
		try:
			mod_consumer = True
			process_background = ClassificationControllerV2beta(self.db, self.publish, self.publish_ideogram, logger, payload, mod_consumer)
			process_background.process_chrom(payload)
		except Exception as e:
			logger.error("Error: %s", str(e))
			raise e
