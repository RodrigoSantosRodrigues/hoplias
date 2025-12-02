import datetime
from pydantic import BaseModel, field_validator
from typing import Union, List, Dict
from ...enums.status_enum import StatusKariotypeEnum
from ...enums.analyse_enum import SpecieTypeEnum, OrdenationTypeEnum


class SegmentedAutomatic(BaseModel):
    contour: List[dict] = []
    id_chromosome: Union[int, None] = None
    left: Union[str, None] = None
    top: Union[int, None] = None
    name: Union[int, None] = None

    class Config:
        from_attributes = True


class ChromosomeDto(BaseModel):
    class_name: str = ''
    upper_chromatide_size: Union[int, None] = None
    lower_chromatide_size: Union[int, None] = None
    checked: bool = False
    obj_area: Union[float, None] = None
    dimension: Dict = {}
    contour: Dict = {}
    upper_measure_ruler: Dict = {}
    lower_measure_ruler: Dict = {}
    centromere_coord: List[float]
    id_chromosome: Union[int, None] = None
    left: Union[str, None] = None
    top: Union[int, None] = None
    name: Union[int, None] = None
    width: Union[int, None] = None
    height: Union[int, None] = None
    size: Union[int, None] = None
    type_extension: Union[int, None] = None
    agent_who_identified_chromosome: Union[str, None] = None
    agent_who_identified_centromere: Union[str, None] = None
    agent_who_identified_rotation: Union[str, None] = None
    times_recalculated: Union[int, None] = None
    batch_number: Union[int, None] = None
    status_centromero: Union[str, None] = None
    status_preclassification: Union[str, None] = None
    canva: Dict = {}
    file_rgb_s3: Union[str, None] = None
    file_gray_s3: Union[str, None] = None
    folder_s3: Union[str, None] = None
    file_rgb_gcs: Union[str, None] = None
    file_gray_gcs: Union[str, None] = None
    file_gray_local: Union[str, None] = None
    file_rgb_local: Union[str, None] = None
    file_rgb_drive: Union[str, None] = None
    file_rgb_drive_id: Union[str, None] = None
    file_gray_drive: Union[str, None] = None
    file_gray_drive_id: Union[str, None] = None

    class Config:
        from_attributes = True


class KariotypeDto(BaseModel):
    id: Union[str, None] = None 
    name: Union[str, None] = None
    description: Union[str, None] = None
    status: Union[str, None] = None
    scheduled: Union[datetime.datetime, None] = None
    categories: List[str] = []
    field_of_view: Union[int, None] = None
    image_resolution: Union[int, None] = None
    chromosomes: List[ChromosomeDto] = []
    segmented_automatic: List[dict] = []
    chromosome_number: Union[int, None] = None
    block_threshold: Union[int, None] = None
    canva: Dict = {}
    left: Union[str, float, None] = None
    top: Union[int, float, None] = None
    width: Union[int, None] = None
    height: Union[int, None] = None
    size: Union[int, None] = None
    type_extension: Union[int, None] = None
    user_id: Union[str, None] = None
    team_id: Union[str, None] = None
    specie_id: Union[str, None] = None
    folder_id: Union[str, None] = None
    file_s3: Union[str, None] = None
    folder_s3: Union[str, None] = None
    file_gcs: Union[str, None] = None
    folder_gcs: Union[str, None] = None
    file_local: Union[str, None] = None
    folder_local: Union[str, None] = None
    file_drive: Union[str, None] = None
    file_drive_id: Union[str, None] = None
    folder_drive: Union[str, None] = None
    address_id: Union[str, None] = None
    specie_type: Union[str, None] = None
    ordenation_type: Union[str, None] = None
    batches_total: Union[int, None] = None
    categories_name: List[str] = []
    created_by_user: Union[str, None] = None
    created_at: Union[datetime.datetime, None] = None

    class Config:
        from_attributes = True

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in [StatusKariotypeEnum.PENDING, StatusKariotypeEnum.COMPLETED,
                     StatusKariotypeEnum.CANCELED, StatusKariotypeEnum.PLANNED,
                     StatusKariotypeEnum.PAUSED, StatusKariotypeEnum.SEGMENTED_CHROMOSOMES,
                     StatusKariotypeEnum.CENTROMERE_LOCALIZED, StatusKariotypeEnum.CLASSIFIED_CHROMOSOMES,
                     StatusKariotypeEnum.IDEOGRAM_BUILDED]:
            raise ValueError(f'Invalid status: {v}. Must be one of {list(StatusKariotypeEnum.__dict__.values())}')
        return v

    @field_validator('specie_type')
    @classmethod
    def validate_specie_type(cls, v):
        if v not in [SpecieTypeEnum.ANIMALS,
                     SpecieTypeEnum.HUMANS,
                     SpecieTypeEnum.PLANTS]:
            raise ValueError(f'Invalid specie type: {v}. Must be one of {list(SpecieTypeEnum.__dict__.values())}')
        return v

    @field_validator('ordenation_type')
    @classmethod
    def validate_ordenation_type(cls, v):
        if v not in [OrdenationTypeEnum.SIZE,
                     OrdenationTypeEnum.CLASS_SIZE,
                     OrdenationTypeEnum.INDEX_CENTROMERIC,
                     OrdenationTypeEnum.CLASS_INDEX_CENTROMERIC]:
            raise ValueError(f'Invalid ordenation type: {v}. Must be one of {list(OrdenationTypeEnum.__dict__.values())}')
        return v


class UpdateDto(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    status: Union[str, None] = None
    scheduled: Union[datetime.datetime, None] = None
    categories: List[str] = []
    field_of_view: Union[int, None] = None
    image_resolution: Union[int, None] = None
    chromosomes: List[ChromosomeDto] = []
    segmented_automatic: List[dict] = []
    chromosome_number: Union[int, None] = None
    block_threshold: Union[int, None] = None
    canva: Dict = {}
    left: Union[str, None] = None
    top: Union[int, None] = None
    width: Union[int, None] = None
    height: Union[int, None] = None
    size: Union[int, None] = None
    type_extension: Union[int, None] = None
    specie_id: Union[str, None] = None
    address_id: Union[str, None] = None
    specie_type: Union[str, None] = None
    ordenation_type: Union[str, None] = None
    user_id: Union[str, None] = None
    team_id: Union[str, None] = None
    file_s3: Union[str, None] = None
    folder_s3: Union[str, None] = None
    file_gcs: Union[str, None] = None
    folder_gcs: Union[str, None] = None
    file_local: Union[str, None] = None
    folder_local: Union[str, None] = None
    file_drive: Union[str, None] = None
    file_drive_id: Union[str, None] = None
    folder_drive: Union[str, None] = None
    categories_name: List[str] = []
    batches_total: Union[int, None] = None
    modified_by_user: Union[str, None] = None
    modified_at: Union[datetime.datetime, None] = None

    class Config:
        from_attributes = True

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in [StatusKariotypeEnum.PENDING, StatusKariotypeEnum.COMPLETED,
                     StatusKariotypeEnum.CANCELED, StatusKariotypeEnum.PLANNED,
                     StatusKariotypeEnum.PAUSED, StatusKariotypeEnum.SEGMENTED_CHROMOSOMES,
                     StatusKariotypeEnum.CENTROMERE_LOCALIZED, StatusKariotypeEnum.CLASSIFIED_CHROMOSOMES,
                     StatusKariotypeEnum.IDEOGRAM_BUILDED]:
            raise ValueError(f'Invalid status: {v}. Must be one of {list(StatusKariotypeEnum.__dict__.values())}')
        return v

    @field_validator('specie_type')
    @classmethod
    def validate_specie_type(cls, v):
        if v not in [SpecieTypeEnum.ANIMALS,
                     SpecieTypeEnum.HUMANS,
                     SpecieTypeEnum.PLANTS]:
            raise ValueError(f'Invalid specie type: {v}. Must be one of {list(SpecieTypeEnum.__dict__.values())}')
        return v

    @field_validator('ordenation_type')
    @classmethod
    def validate_ordenation_type(cls, v):
        if v not in [OrdenationTypeEnum.SIZE,
                     OrdenationTypeEnum.CLASS_SIZE,
                     OrdenationTypeEnum.INDEX_CENTROMERIC,
                     OrdenationTypeEnum.CLASS_INDEX_CENTROMERIC]:
            raise ValueError(f'Invalid ordenation type: {v}. Must be one of {list(OrdenationTypeEnum.__dict__.values())}')
        return v
