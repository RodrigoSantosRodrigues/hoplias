import uuid
import logging
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict
import asyncio

from ..domain.interfaces.request.kariotype_request import CreateKariotype
from ..infra.base.rpc_proxy import RpcProxy
from ..helpers.mappers import RoutePathGateway, Bucket
from ..helpers.utils import (
  get_payload_after_first_centromere_request, 
  get_payload_remine_queue,
  clean_base64
)
from ..infra.repository.category_repository import CategoryRepository
from ..domain.interfaces.dto.category_dto import CategoryData
from ..infra.repository.kariotype_repository import KariotypeRepository
from ..infra.repository.ideogram_repository import IdeogramRepository
from ..infra.base.client_s3 import ClientS3
from ..infra.base.client_google_drive import ClientGoogleDrive
from ..infra.base.client_google_cloud import ClientGoogleCloudStorage
from ..infra.base.client_local_storage import ClientLocalStorage
from ..domain.model.ideogram_model import IdeogramModel
from ..helpers.editor_kario import EditorKario
from ..domain.enums.messages_enum import MessagesEnum
from ..domain.enums.status_enum import StatusKariotypeEnum, StatusChromosomeEnum
from ..helpers.utils import slugify

class AnalyseChromosomes:
  def __init__(
      self,
      data: CreateKariotype,
      request: Request,
      db: AsyncIOMotorCollection,
      auth: str, 
      endpoint_url: str,
      account_gcp: bool = True
    ):
    self.chromosomes = data.chromosomes
    self.properties = data.properties
    self.team_id = data.properties.team_id if data.properties.team_id else None
    self.user_id = auth if not data.properties.team_id else None
    self.request = request
    self.__db = db
    self.__auth = auth
    self.__endpoint_url = endpoint_url
    self.__account_gcp = account_gcp
    self.__local_storage = self.request.app.config.HOST_DOCUMENTS_DIR is not None
    self.__client_s3 = ClientS3(self.request.app.config)
    self.__client_google_drive = ClientGoogleDrive(self.request.app.config)
    self.__client_google_cloud = ClientGoogleCloudStorage(self.request.app.config)
    self.__client_local_storage = ClientLocalStorage(self.request.app.config)
    self.rpc_proxy = RpcProxy(self.request.app.config)
    self.kariotype_repository = KariotypeRepository(self.__db)
    self.ideogram_repository = IdeogramRepository(self.__db)
    self.category_repository = CategoryRepository(self.__db)
    
    self.editor_kario = EditorKario()

  async def orchestrator(self) -> any:
    if self.__endpoint_url == RoutePathGateway.SEGMENTATION:
      return await self.segment_chromosomes()
    
    if self.__endpoint_url == RoutePathGateway.CLASSIFICATION_CENTROMERE:
      return await self.classification_centromere()
    
    if self.__endpoint_url == RoutePathGateway.PRECLASSIFICATION:
      return await self.preclassification()
    
    if self.__endpoint_url == RoutePathGateway.CLASSIFICATION:
      return await self.classification()
    
    if self.__endpoint_url == RoutePathGateway.IDEOGRAM:
      return await self.ideogram()
    if self.__endpoint_url == RoutePathGateway.CONVERT_TO_JPG:
      return await self.convert_to_jpg()

  async def segment_chromosomes(self) -> Dict:
    properties = None
    self.chromosomes['width'] = self.properties.width
    self.chromosomes['height'] = self.properties.height
    response = await self.rpc_proxy.api_proxy(self.__endpoint_url, self.chromosomes)
    if response and not self.properties.id:
      data = self.properties
      for category in data.categories_name:
        category_slug = await self.category_repository.get_by_slug_and_team_or_user(slugify(category), data.team_id, self.__auth)
        if category_slug:
            data.categories.append(category_slug.get('_id')) if category_slug.get('_id') not in data.categories else None
        else:
            await self.category_repository.create(
              CategoryData(
              name= category,
              slug= slugify(category),
              description= '',
              team_id= data.team_id if data.team_id else None,
              user_id=self.__auth if not data.team_id else None
              ))
            category_slug = await self.category_repository.get_by_slug_and_team_or_user(slugify(category), data.team_id, self.__auth)
            if category_slug:
              data.categories.append(category_slug.get('_id')) if category_slug.get('_id') not in data.categories else None
      del data.categories_name

      account_id = self.team_id if self.team_id else self.user_id
      file_id = str(uuid.uuid4())
      file_name = f"{file_id}.png"
 
      if not self.__account_gcp and not self.__local_storage:
        await self.__client_s3.upload_image(
          clean_base64(self.chromosomes['src']),
          Bucket.BUCKET,
          f"{account_id}/{file_id}/{file_name}"
        )
        data.file_s3 = file_name
        data.folder_s3 = file_id

      elif not self.__local_storage:
        await self.__client_google_cloud.upload_image(
          clean_base64(self.chromosomes['src']),
          f"{account_id}/{file_id}/{file_name}",
        )
        data.file_gcs = file_name
        data.folder_gcs = file_id

      elif self.__local_storage:
        await self.__client_local_storage.upload_image(
          clean_base64(self.chromosomes['src']),
          f"{Bucket.BUCKET}/{account_id}/{file_id}/{file_name}",
        )
        data.file_local = file_name
        data.folder_local = file_id
      
      data.status = StatusKariotypeEnum.SEGMENTED_CHROMOSOMES
      data.image_resolution = self.properties.image_resolution
      data.size = self.properties.size
      data.type_extension = self.properties.type_extension
      data.specie_type = self.properties.specie_type
      data.ordenation_type = self.properties.ordenation_type

      data.user_id = self.user_id if not self.team_id else None
      data.team_id = self.team_id if self.team_id else None
      data.created_by_user = self.user_id
      properties = await self.kariotype_repository.create(data)
      properties = {**properties, "id": str(properties.get('_id'))}

    if response and self.properties.id:
      kariotype = await self.kariotype_repository.get_by_id(self.properties.id)
      if not kariotype:
        return {
          'success': False,
          'message': MessagesEnum.NOT_FOUND
        }

      properties = {**kariotype, "id": str(kariotype.get('_id'))}

    return {
      'properties': properties,
      'chromosomes': response
    }

  async def classification_centromere(self) -> Dict:
    kariotype = await self.kariotype_repository.get_by_id(self.properties.id)
    account_id = kariotype.get('team_id') if kariotype.get('team_id') else kariotype.get('user_id')

    if not kariotype:
      return {
        'success': False,
        'message': MessagesEnum.NOT_FOUND
      }

    if len(kariotype.get('chromosomes', [])) > 0 and self.__account_gcp:
      if kariotype.get('folder_gcs'):
        await self.__client_google_cloud.remove_folder_by_name(
          kariotype.get('folder_gcs'),
          Bucket.FOLDER_BASE
        )

      if kariotype.get('folder_s3'):
        pass # TODO: Implement S3 folder removal
      
      if kariotype.get('folder_local'):
        await self.__client_local_storage.remove_folder_by_name(
          account_id,
          kariotype.get('folder_local')
        )

    base_objects, total_batches = get_payload_after_first_centromere_request(self.chromosomes.get('objects', []))

    all_objects = self.chromosomes.get('objects', [])
  
    image_objects = [obj for obj in all_objects if obj.get('type') == 'image']
  
    non_image_objects = [obj for obj in all_objects if obj.get('type') == 'polygon'][:6]

    first_batch = {
      'objects': non_image_objects + image_objects
    }

    remaining_objects = {
      'objects': [obj for obj in all_objects if obj not in first_batch['objects']]
    }

    response = await self.rpc_proxy.api_proxy(self.__endpoint_url, first_batch)

    if response:
      tasks = []
    
      for index, item in enumerate(response.get('objects')):
        file_rgb_name = f"{str(uuid.uuid4())}.png"
        file_gray_name = f"{str(uuid.uuid4())}.png"
        
        if not self.__account_gcp and not self.__local_storage:
          task = self.__client_s3.upload_image(
              clean_base64(item['base64_rgb']),
              Bucket.BUCKET,
              f"{account_id}/{kariotype.get('folder_s3')}{Bucket.CROPED_RGB_FOLDERS}{file_rgb_name}"
          )
          task_ = self.__client_s3.upload_image(
              clean_base64(item['base64_gray']),
              Bucket.BUCKET,
              f"{account_id}/{kariotype.get('folder_s3')}{Bucket.CROPED_GRAY_FOLDERS}{file_gray_name}"
          )
          tasks.append(task)
          tasks.append(task_)
          base_objects[index]['file_rgb_s3'] = file_rgb_name
          base_objects[index]['file_gray_s3'] = file_gray_name
          
        elif not self.__local_storage:
          await self.__client_google_cloud.upload_image(
            clean_base64(item['base64_rgb']),
            f"{account_id}/{kariotype.get('folder_gcs')}{Bucket.CROPED_RGB_FOLDERS}{file_rgb_name}"
          )
          await self.__client_google_cloud.upload_image(
            clean_base64(item['base64_gray']),
            f"{account_id}/{kariotype.get('folder_gcs')}{Bucket.CROPED_GRAY_FOLDERS}{file_gray_name}"
          )
          base_objects[index]['file_rgb_gcs'] = file_rgb_name
          base_objects[index]['file_gray_gcs'] = file_gray_name

        elif self.__local_storage:
          await self.__client_local_storage.upload_image(
            clean_base64(item['base64_rgb']),
            f"{Bucket.BUCKET}/{account_id}/{kariotype.get('folder_local')}{Bucket.CROPED_RGB_FOLDERS}{file_rgb_name}"
          )
          await self.__client_local_storage.upload_image(
            clean_base64(item['base64_gray']),
            f"{Bucket.BUCKET}/{account_id}/{kariotype.get('folder_local')}{Bucket.CROPED_GRAY_FOLDERS}{file_gray_name}"
          )
          base_objects[index]['file_rgb_local'] = file_rgb_name
          base_objects[index]['file_gray_local'] = file_gray_name
        
        base_objects[index]['id_chromosome'] = item['id']
        base_objects[index]['dimension'] = item['dimension']
        base_objects[index]['centromere_coord'] = item['centromere']

      if not self.__account_gcp:
        await asyncio.gather(*tasks)

      image_object = image_objects[0]

      data = {
        'chromosomes': base_objects,
        'top': image_object.get('top'),
        'left': image_object.get('left'),
        'width': image_object.get('width'),
        'height': image_object.get('height'),
        'block_threshold': self.properties.block_threshold,
        'batches_total': total_batches,
        'status': StatusKariotypeEnum.CENTROMERE_LOCALIZED
      }

      await self.kariotype_repository.update(
        kariotype, 
        data
      )

      if total_batches > 1:
        queue_data = {
          'kariotype_id': self.properties.id
        }
        await self.rpc_proxy.api_proxy(RoutePathGateway.CLASSIFICATION_CENTROMERE_QUEUE, queue_data)

    if len(remaining_objects.get('objects', [])) > 0:
      response['objects'] = response['objects'] + remaining_objects['objects']
    return response

  async def preclassification(self) -> Dict:
    kariotype = await self.kariotype_repository.get_by_id(self.properties.id)
    if not kariotype:
      return {
        'success': False,
        'message': MessagesEnum.NOT_FOUND
      }

    all_objects = self.chromosomes.get('objects', [])
  
    first_objects = all_objects[:6]

    chromosomes_has_centromered = [
      obj for obj in kariotype.get('chromosomes')
      if obj.get('batch_number') == 1 or obj.get('status_centromere') == StatusChromosomeEnum.PROCESSED
    ]

    if len(first_objects) == 1:
      chromosomes_has_centromered = [
        obj for obj in kariotype.get('chromosomes')
        if obj.get('id_chromosome') == first_objects[0].get('id')
      ]

    first_batch = {
      'objects': first_objects,
      'config_chromosome': { 
        **self.chromosomes.get('config_chromosome'),
        'kariotype_id': self.properties.id
      }
    }

    response = await self.rpc_proxy.api_proxy(self.__endpoint_url, first_batch)
  
    if response:
      data = []
      checked = True if len(response.get('data')) == 1 else None
      if checked:
        response['data'][0]['checked'] = checked

      for res_data, chromosome in zip(response.get('data'), chromosomes_has_centromered):
        if res_data.get('empty') == True:
          data.append({ 
            'id_chromosome': chromosome.get('id_chromosome'), 
            'empty': True,
            'status_preclassification': StatusChromosomeEnum.PROCESSED 
          })
          continue

        obj = {}
        times_recalculated = chromosome.get('times_recalculated') +1 if chromosome.get('times_recalculated') else 0
        
        who_rotation = res_data.get('rotation_by_user', None)
          
        obj['centromere_coord'] = res_data.get('centromere')
        obj['id_chromosome'] = chromosome.get('id_chromosome')
        obj['times_recalculated'] = times_recalculated
        obj['checked'] = checked
        obj['status_preclassification'] = StatusChromosomeEnum.PROCESSED
        obj['agent_who_identified_rotation'] = who_rotation if who_rotation else 'auto'
        obj['chromosomes_class_geodesic'] = res_data.get('chromosomes_class_geodesic')
        obj['chromosomes_class_point_to_point'] = res_data.get('chromosomes_class_point_to_point')
        obj['chromosomes_class_simple'] = res_data.get('chromosomes_class_simple')
        obj['rb_geodesic'] = res_data.get('rb_geodesic')
        obj['rb_point'] = res_data.get('rb_point')
        obj['rb_simple'] = res_data.get('rb_simple')
        obj['rb_mean'] = res_data.get('rb_mean')
        obj['size_geodesic'] = res_data.get('size_geodesic')
        obj['size_point_to_point'] = res_data.get('size_point_to_point')
        obj['size_simple'] = res_data.get('size_simple')
        obj['chromosomes_class'] = res_data.get('chromosomes_class')
        obj['size_chrom'] = res_data.get('size_chromosome')
        obj['obj_area'] = res_data.get('obj_area')
        obj['upper_chromatide_size'] = res_data.get('upper_chromatide')
        obj['lower_chromatide_size'] = res_data.get('lower_chromatide')
        obj['upper_measure_ruler'] = res_data.get('upper_measure_ruler')
        obj['lower_measure_ruler'] = res_data.get('lower_measure_ruler')
        obj['measure_width'] = res_data.get('measure_width')
        obj['measure_height'] =  res_data.get('measure_height')
        obj['centromere_start'] = res_data.get('centromere_chromosome')
        obj['base_pairs'] = res_data.get('base_pairs')
        obj['centromere_bp'] = res_data.get('centromere_bp')
        obj['rotation'] = res_data.get('rotation') if res_data.get('rotation') else None
        data.append(obj)

      await self.kariotype_repository.bulk_update(
        self.properties.id, 
        data
      )
  
    return response

  async def classification(self) -> Dict:
    kariotype = await self.kariotype_repository.get_by_id(self.properties.id)
    if not kariotype:
      return {
        'success': False,
        'message': MessagesEnum.NOT_FOUND
      }
    response = await self.rpc_proxy.api_proxy(self.__endpoint_url, { 'kariotype_id': self.properties.id })
  
    return response

  async def ideogram(self) -> Dict:
    ideogram_data = None
    response = {}
    if self.properties.id:
      ideogram_data = await self.ideogram_repository.get_by_id(self.properties.id)
      if not ideogram_data:
        return {
          'success': False,
          'message': MessagesEnum.NOT_FOUND
        }

    response = await self.rpc_proxy.api_proxy(self.__endpoint_url, self.chromosomes)
    if response:
      if not self.properties.id:
        created_ideogram = await self.ideogram_repository.create(
            IdeogramModel(
                kariotype_id=None,
                text_gff=self.chromosomes.get('text_file'),
                citogenetic_view=response.get('karioplot'),
                citogenomic_view=response.get('detail_plot'),
                user_id = self.user_id if not self.team_id else None,
                team_id = self.team_id if self.team_id else None
            )
        )
        response['ideogram'] = {**created_ideogram, "id": str(created_ideogram.get('_id'))}

      if self.properties.id:
        updated_ideogram = await self.ideogram_repository.update(
          ideogram_data if ideogram_data else {},
          {
            'text_gff': self.chromosomes.get('text_file'),
            'citogenetic_view': response.get('karioplot'),
            'citogenomic_view': response.get('detail_plot')
          }
        )
        response['ideogram'] = {**updated_ideogram, "id": str(updated_ideogram.get('_id'))}

    return response

  async def convert_to_jpg(self) -> Dict:
    response = await self.rpc_proxy.api_proxy(self.__endpoint_url, self.chromosomes)

    return response
