# -*- coding: utf-8 -*-
import logging
from nameko.events import EventDispatcher
from nameko.rpc import rpc
from nameko_amqp_retry import entrypoint_retry

from nameko.messaging import Publisher, consume
from kombu.messaging import Exchange, Queue
from .db.Conect import MongoDB

from .controllers.IdeogramController import IdeogramController

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

monitoring_exchange = Exchange(name="ideogram")
ideogram_queue = Queue(name="ideogram_queue", routing_key="ideogram_queue", exchange="ideogram")

class Ideogram:
	name = 'ideogram'
	event_dispatcher = EventDispatcher()
	publish = Publisher(exchange=monitoring_exchange)
	db = MongoDB()

	@rpc
	@entrypoint_retry(
        retry_for=(TypeError, ValueError),
        limit=5,
        schedule=(500, 600, 700, 800, 900),
    )
	def plot(self, data):
		"""
			This is an RPC call function. Receive a json hoplias.

			params:
				json: 
					type: hoplias

			return:
				json: 
					type: hoplias
		"""
		ideogram_controller = IdeogramController(self.db, data, logger)
		payload = ideogram_controller.create_plot_ideogram()
		
		# self.event_dispatcher('centromere', {
		# 		'centromere': payload,
		# })

		return payload

	def on_status(self, data):
		self.publish("ideogram_queue", data)

	@consume(queue=ideogram_queue)
	@entrypoint_retry(
        retry_for=(TypeError, ValueError),
        limit=5,
        schedule=(500, 600, 700, 800, 900),
    )
	def handle_classification_queue(self, payload):
		#logger.info("Received ideogram_queue event: %s", payload)

		process_background = IdeogramController(self.db, payload, logger)
		process_background.background_plot_ideogram_process()
