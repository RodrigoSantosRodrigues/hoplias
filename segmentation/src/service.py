# -*- coding: utf-8 -*-
import datetime
import json
import logging
from nameko.events import EventDispatcher
from nameko.rpc import rpc
from nameko_amqp_retry import entrypoint_retry

from .controllers.SegmentationController import SegmentationController
from .controllers.ConvertToJpgController import ConvertToJpgController

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Segmentation:
	name = 'segmentation'
	
	event_dispatcher = EventDispatcher()


	@rpc
	@entrypoint_retry(
        retry_for=(TypeError, ValueError),
        limit=5,
        schedule=(500, 600, 700, 800, 900),
    )
	def chromosomes_hoplias(self, data):
		"""
			This is an RPC call function. Receive a json Hoplias Karyotype.

			params:
				josn: 
					type: hoplias

			return:
				json: 
					type: hoplias
		"""
		image = SegmentationController(logger)
		image.load_image_hoplias(data)
		image.load_block_value(data)
		image.load_hard_process(data)
		payload = image.segmentation_hoplias()

		# self.event_dispatcher('segmented_hoplias', {
		# 		'segmented': payload,
		# })

		return payload

	@rpc
	@entrypoint_retry(
        retry_for=(TypeError, ValueError),
        limit=5,
        schedule=(500, 600, 700, 800, 900),
    )
	def convert_to_jpg(self, data):
		image = ConvertToJpgController()
		image.load_image_hoplias(data)
		payload = image.convert_to_jpg()

		# self.event_dispatcher('converted_to_jpg_hoplias', {
		# 		'segmented': payload,
		# })

		return payload
