# -*- coding: utf-8 -*-
#/src/helpers/CallRpc.py
"""
                        API gateway
    ------------------------------------------------------------------------
                           RPC
    ------------------------------------------------------------------------
         Sends a request RPC (Remote procedure call) 
    
"""
import logging
from nameko.standalone.rpc import ClusterRpcProxy
from ..config import rabbit_config

CONFIG = {'AMQP_URI': rabbit_config.get('AMQP_URI')}

def rpc_proxy(name, data):
  response = None
  with ClusterRpcProxy(CONFIG) as rpc:
    method= {
      'segmentation_create': rpc.segmentation.chromosomes,
      'segmentation_create_hoplias': rpc.segmentation.chromosomes_hoplias,
      'centromere': rpc.classification.centromere,
      'preclassification': rpc.classification.preclassification,
      'classification': rpc.classification.classification,
      'ideogram': rpc.ideogram.plot,
      'convert_to_jpg_hoplias': rpc.segmentation.convert_to_jpg
    }
    try:
      response= method[name](data)
    except Exception as ex:
      logging.error(f"Rpc error: {ex}")
    return response
