from typing import Any
from fastapi import Request
import asyncio
from typing import Any, Dict
from motor.motor_asyncio import AsyncIOMotorCollection

from ..domain.interfaces.request.kariotype_request import CreateKariotypeRequest, UpdateKariotype
from ..infra.repository.kariotype_repository import KariotypeRepository
from ..infra.repository.ideogram_repository import IdeogramRepository
from ..helpers.mappers import FilterType, Bucket
from ..infra.base.client_s3 import ClientS3
from ..infra.base.client_google_drive import ClientGoogleDrive
from ..infra.base.client_google_cloud import ClientGoogleCloudStorage
from ..infra.base.client_local_storage import ClientLocalStorage
from ..infra.repository.category_repository import CategoryRepository
from ..domain.enums.messages_enum import MessagesEnum
from ..domain.enums.rules_enum import RolesEnum
from ..domain.interfaces.dto.category_dto import CategoryData
from ..helpers.utils import slugify, get_payload_segmented_initial_request
from ..helpers.editor_kario import EditorKario
from ..domain.enums.status_enum import StatusKariotypeEnum, StatusChromosomeEnum


async def create_kariotype(
  data: CreateKariotypeRequest,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
) -> Dict:
  kariotype_repository = KariotypeRepository(db)
  category_repository = CategoryRepository(db)

  for category in data.categories_name:
    category_slug = await category_repository.get_by_slug_and_team_or_user(
      slugify(category),
      data.team_id, auth
    )
    if category_slug:
      data.categories.append(category_slug.get('_id')) if category_slug.get('_id') not in data.categories else None
    else:
      await category_repository.create(
        CategoryData(
          name= category,
          slug= slugify(category),
          description= '',
          team_id= data.team_id if data.team_id else None,
          user_id=auth if not data.team_id else None
        ))
      category_slug = await category_repository.get_by_slug_and_team_or_user(slugify(category), data.team_id, auth)
      if category_slug:
        data.categories.append(category_slug.get('_id')) if category_slug.get('_id') not in data.categories else None

  del data.categories_name
  data.user_id = auth if not data.team_id else None
  data.team_id = data.team_id if data.team_id else None,
  data.created_by_user = auth

  kariotype = await kariotype_repository.create(data)

  return {
    'success': True,
    'message': MessagesEnum.CREATED,
    'data': {**kariotype, "id": str(kariotype.get('_id'))}
  }


async def get_by_search(
  request: Request,
  db: AsyncIOMotorCollection,
  auth: int,
  team_id: str,
  order_by: str = None,
  search: str = None,
  page: int = 1,
  page_size: int = 10,
  start_date: str = None,
  end_date: str = None,
  status: str = None,
  by_today: bool = False
) -> Any:
  kariotype_repository = KariotypeRepository(db)
  client_s3 = ClientS3(request.app.config)
  client_drive = ClientGoogleDrive(request.app.config)
  client_cloud = ClientGoogleCloudStorage(request.app.config)
  client_local = ClientLocalStorage(request.app.config)

  kariotypes = await kariotype_repository.get_by_user_or_team(
    order_by=order_by,
    search=search,
    start_date=start_date,
    end_date=end_date,
    status=status,
    page=page, 
    page_size=page_size,
    team_id=team_id,
    user_id=auth,
    by_today=by_today
  )
  
  for item in kariotypes['items']:
    account_id = item.get('team_id') if item.get('team_id') else item.get('user_id')
    
    if item.get('folder_s3') and item.get('file_s3'):
      base_64 = await client_s3.load_image(
        f"{account_id}/{item.get('folder_s3')}/{item.get('file_s3')}",
        Bucket.BUCKET
      )
      item['base64'] = base_64

    if item.get('folder_gcs') and item.get('file_gcs'):
      base_64 = await client_cloud.load_image(
        f"{account_id}/{item.get('folder_gcs')}/{item.get('file_gcs')}",
      )
      item['base64'] = base_64

    if item.get('folder_local') and item.get('file_local'):
      base_64 = await client_local.load_image(
        f"{Bucket.BUCKET}/{account_id}/{item.get('folder_local')}/{item.get('file_local')}",
      )
      item['base64'] = base_64

  return kariotypes


async def get_kariotype_by_id(
    id: str,
    request: Request,
    db: AsyncIOMotorCollection,
    auth: str,
    page: int = 1,
    filter_type: str = None
) -> Any:
  kariotype_repository = KariotypeRepository(db)
  ideogram_repository = IdeogramRepository(db)
  client_s3 = ClientS3(request.app.config)
  editor_kario = EditorKario()
  client_drive = ClientGoogleDrive(request.app.config)
  client_cloud = ClientGoogleCloudStorage(request.app.config)
  client_local = ClientLocalStorage(request.app.config)

  data = await kariotype_repository.get_by_id(id)
  if not data:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  account_id = data.get('team_id') if data.get('team_id') else data.get('user_id')

  if data.get('folder_s3') and data.get('file_s3'):
    base_64 = await client_s3.load_image(
      f"{account_id}/{data.get('folder_s3')}/{data.get('file_s3')}",
      Bucket.BUCKET
    )

  if data.get('folder_gcs') and data.get('file_gcs'):
    base_64 = await client_cloud.load_image(
      f"{account_id}/{data.get('folder_gcs')}/{data.get('file_gcs')}",
    )

  if data.get('folder_local') and data.get('file_local'):
    base_64 = await client_local.load_image(
      f"{Bucket.BUCKET}/{account_id}/{data.get('folder_local')}/{data.get('file_local')}",
    )

  if (data.get('status') == StatusKariotypeEnum.SEGMENTED_CHROMOSOMES):
    data['work_area'] = editor_kario.get_response_first_step(
      base_64,
      data,
      data.get('segmented_automatic', [])
    )
  
  chromosomes = data.get('chromosomes', [])
  total_chromosomes = 0
  if data.get('status') == StatusKariotypeEnum.CENTROMERE_LOCALIZED:
    items = editor_kario.get_items_base()
    total_chromosomes = len(chromosomes)
    page_size = 6
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    tasks = []

    for i, chrom in enumerate(chromosomes):
      if chrom.get('empty') is not True:
        async def load_and_update(i, chrom):
          base_rgb_64 = None
          base_gray_64 = None
          if start_index <= i <= end_index:
            if chrom.get('file_gray_s3'):
              base_gray_64 = await client_s3.load_image(
                f"{account_id}/{data.get('folder_s3')}{Bucket.CROPED_GRAY_FOLDERS}{chrom.get('file_gray_s3')}",
                Bucket.BUCKET
              )
            if chrom.get('file_gray_gcs'):
              base_gray_64 = await client_cloud.load_image_(
                f"{account_id}/{data.get('folder_gcs')}{Bucket.CROPED_GRAY_FOLDERS}{chrom.get('file_gray_gcs')}",
              )
            if chrom.get('file_gray_local'):
              base_gray_64 = await client_local.load_image(
                f"{Bucket.BUCKET}/{account_id}/{data.get('folder_local')}{Bucket.CROPED_GRAY_FOLDERS}{chrom.get('file_gray_local')}")
          return chrom, base_rgb_64, base_gray_64

        tasks.append(asyncio.create_task(load_and_update(i, chrom)))

    results = await asyncio.gather(*tasks)

    for chrom, base_rgb_64, base_gray_64 in results:
      payload = editor_kario.get_data_centromeres_second_step(
        chrom=chrom,
        image_base64_rgb=base_rgb_64,
        image_base64_gray=base_gray_64
      )
      items['objects'].append(payload.copy())

    image = editor_kario.get_data_image_second_step(
      image_base64=base_64,
      data=data
    )
    items['objects'].append(image)
    data['work_area'] = items

  canva = data.get('canva', {})
  if data.get('status') == StatusKariotypeEnum.CLASSIFIED_CHROMOSOMES or filter_type == FilterType.REPORT:
    items = editor_kario.get_items_base()
    tasks = []
    for index, chrom in enumerate(canva.get('objects', [])):
      if chrom.get('type') == 'image':
        async def load_and_update_(index, chrom):
          max_concurrent_io = request.app.config.MAX_CONCURRENT_IO_LOAD_IMAGES
          async with asyncio.Semaphore(max_concurrent_io if max_concurrent_io else 10):
            base64_img = None
            if chrom.get('file_gray_s3'):
              base64_img = await client_s3.load_image(
                f"{account_id}/{data.get('folder_s3')}{Bucket.CROPED_GRAY_FOLDERS}{chrom.get('file_gray_s3')}",
                Bucket.BUCKET
              )
            if chrom.get('file_gray_gcs'):
              base64_img = await client_cloud.load_image_(
                f"{account_id}/{data.get('folder_gcs')}{Bucket.CROPED_GRAY_FOLDERS}{chrom.get('file_gray_gcs')}",
              )
            if chrom.get('file_gray_local'):
              base64_img = await client_local.load_image(
                f"{Bucket.BUCKET}/{account_id}/{data.get('folder_local')}{Bucket.CROPED_GRAY_FOLDERS}{chrom.get('file_gray_local')}"
              )

            return index, base64_img
          
        tasks.append(asyncio.create_task(load_and_update_(index, chrom)))

    results = await asyncio.gather(*tasks)
    for index, base64_img in results:
      if base64_img:
        canva['objects'][index]['src'] = base64_img

    if filter_type == FilterType.REPORT:
      for i, chrom in enumerate(chromosomes):
        if chrom.get('empty') is not True:
          payload = editor_kario.get_data_centromeres_second_step(
            chrom=chrom,
            image_base64_rgb=None
          )
          items['objects'].append(payload.copy())
 
      image = editor_kario.get_data_image_second_step(
        image_base64=base_64,
        data=data
      )
      items['objects'].append(image)
      data['work_area'] = items
    
    if data.get('finished', False):
      ideogram = await ideogram_repository.get_by_kariotype_id(data.get('_id'))
      if ideogram.get('citogenetic_view', None) is not None:
        data['ideogram'] = {**ideogram, "id": str(ideogram.get('_id'))}

    data['canva'] = canva

  return {
    'success': True,
    'message': MessagesEnum.SUCCESS,
    'data': {
      **data,
      "id": str(data.get('_id')),
      "pagination": {
        "page": page,
        "page_size": 6,
        "total_items": total_chromosomes,
        "total_pages": (total_chromosomes + 5) // 6
      }
    }
  }


async def update_kariotype(
  id: str,
  data: UpdateKariotype,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str
) -> Any:
  kariotype_repository = KariotypeRepository(db)

  data.modified_by_user = auth
  update_data = data.dict(exclude_unset=True)

  kariotype = await kariotype_repository.get_by_id(id)
  if not kariotype:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  kariotype_updated = {}
  if kariotype.get('status') == StatusKariotypeEnum.SEGMENTED_CHROMOSOMES:
    data = get_payload_segmented_initial_request(update_data.get('segmented_automatic', []))
    obj = next((obj for obj in update_data.get('segmented_automatic', []) if obj["type"] == "image"), None)
    
    kariotype_updated = await kariotype_repository.update(kariotype, {
      'top': obj.get('top'),
      'left':  obj.get('left'),
      'width': obj.get('width'),
      'height': obj.get('height'),
      'segmented_automatic': data
    })
  
  if kariotype.get("status") == StatusKariotypeEnum.CLASSIFIED_CHROMOSOMES:
    canva = update_data.get("canva", {})
    for obj in canva.get("objects", []):
      if obj.get("type") == "image":
        obj['src'] = None
    
    await kariotype_repository.update(kariotype, {"canva": canva})

  return {
    'success': True,
    'message': MessagesEnum.UPDATED,
    'data': kariotype_updated
  }


async def remove_kariotype(
    id: str,
    request: Request,
    db: AsyncIOMotorCollection,
    auth: str
) -> Dict[str, str]:
  kariotype_repository = KariotypeRepository(db)
  client_drive = ClientGoogleDrive(request.app.config)
  client_cloud = ClientGoogleCloudStorage(request.app.config)
  client_local = ClientLocalStorage(request.app.config)

  kariotype = await kariotype_repository.get_by_id(id)
  if not kariotype:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  account_id = kariotype.get('team_id') if kariotype.get('team_id') else kariotype.get('user_id')
  if kariotype.get('folder_s3') and kariotype.get('file_s3'):
    await client_cloud.remove_folder_by_name(
      account_id,                              
      kariotype.get('folder_s3')
    )
  if kariotype.get('folder_gcs') and kariotype.get('file_gcs'):
    await client_cloud.remove_folder_by_name(
      account_id,                              
      kariotype.get('folder_gcs')
    )
  if kariotype.get('folder_local') and kariotype.get('file_local'):
    await client_local.remove_folder_by_name(  
      account_id,                       
      kariotype.get('folder_local')
    )
  await kariotype_repository.delete(kariotype.get('_id'))

  return {
    'success': True,
    'message': MessagesEnum.DELETED
  }
