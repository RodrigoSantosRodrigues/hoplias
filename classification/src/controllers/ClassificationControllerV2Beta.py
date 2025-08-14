import os
import re
import time
import numpy as np
import json
import cv2
import base64
import uuid
import itertools
from typing import List, Tuple, Union, Dict
from itertools import islice

from ..helpers.Filter import Filter
from ..helpers.Mask import Mask
from ..helpers.Extract import Extract
from ..helpers.Resize import Resize
from ..helpers.Rotation import Rotation
from ..helpers.ClassifyAdjustAnomalous import ClassifyAdjustAnomalous
from ..helpers.ZhangSue import ZhangSue
from ..helpers.ChromosomeCalculator import ChromosomeCalculator
from ..helpers.RotationAngle import RotationAngle
from ..helpers.NumpyToPng import NumpyToPng
from ..enums.StatusEnum import StatusKariotypeEnum, StatusChromosomeEnum
from ..enums.FilesEnum import FilesEnum
from ..enums.S3Enum import Bucket
from ..enums.AnalyseEnum import SpecieTypeEnum, OrdenationTypeEnum
from ..services.ClientS3 import ClientS3
from ..services.ClientGoogleDrive import ClientGoogleDrive
from ..services.ClientGoogleCloud import ClientGoogleCloud
from ..services.ClientLocalSorage import ClientLocalStorage
from ..models.IdeogramModel import IdeogramModel
from ..db.KariotypeCrud import KariotypeRepository
from ..db.IdeogramCrud import IdeogramRepository
from ..utils.debug_data import save_result


class ClassificationControllerV2beta:
    """
    >>> TODO: Add more detailed docstring here
    - Consider creating another class to simplify and organize the code
    - document the class logic
    """
    def __init__(self, db, publish, publish_ideogram, logger, data, mod_consumer=False):
        self.db = db
        self.logger = logger
        self.data = data
        self.image_base64 = ""
        self.publish = publish
        self.publish_ideogram = publish_ideogram
        self.image = None
        self.contour = ""
        self.coord_sum= []
        self.image_gray = ""
        self.image_rgb = ""
        self.properties = None
        self.remining_centromere = []
        self.remining_classification = []
        self.remining_centromered = []
        self.mod_consumer = mod_consumer
        self.__max_workers = 10
        self.client_s3 = ClientS3()
        self.client_google_drive = ClientGoogleDrive()
        self.client_google_cloud = ClientGoogleCloud()
        self.client_local_storage = ClientLocalStorage()
        self.kariotype_repository = KariotypeRepository(self.db)
        self.ideogram_repository = IdeogramRepository(self.db)
        self.path_payload_kariotype_v1 = FilesEnum.PATH_PAYLOAD_KARIOTYPE_V1
        self.path_payload_image = FilesEnum.PATH_PAYLOAD_IMAGE
        self.path_payload_polygon = FilesEnum.PATH_PAYLOAD_POLYGON
        self.path_payload_kariotype = FilesEnum.PATH_PAYLOAD_KARIOTYPE
        self.path_payload_text_label = FilesEnum.PATH_PAYLOAD_TEXT_LABEL
        self.path_payload_text_size = FilesEnum.PATH_PAYLOAD_SIZE
        self.path_payload_group = FilesEnum.PATH_PAYLOAD_GROUP

    def process_chrom(self, payload):
        """
        Processes chromosomes for centromere localization and classification.
        >>> TODO: Add more detailed docstring here
        """
        id = payload.get('kariotype_id')
        self.data = payload
        
        self.properties = self.kariotype_repository.get_by_id(id)
    
        if self.properties.get('status') == StatusKariotypeEnum.CENTROMERE_LOCALIZED or \
            self.properties.get('status') == StatusKariotypeEnum.CLASSIFIED_CHROMOSOMES:
            self.remining_centromere = [
                obj for obj in self.properties.get('chromosomes')
                if (obj.get('status_centromere') == StatusChromosomeEnum.PENDING or \
                obj.get('status_centromere') == StatusChromosomeEnum.IN_QUEUE) and \
                obj.get('empty') is not True
            ]

            account_id = self.properties.get('team_id') if self.properties.get('team_id') else self.properties.get('user_id')

            if self.properties.get('file_s3') is not None:
                base_64 = self.client_s3.load_image(
                    f"{account_id}/{self.properties.get('folder_s3')}/{self.properties.get('file_s3')}",
                    Bucket.BUCKET
                )

            if self.properties.get('file_gcs') is not None:
                base_64 = self.client_google_cloud.load_image(
                    f"{account_id}/{self.properties.get('folder_gcs')}/{self.properties.get('file_gcs')}",
                )

            if self.properties.get('file_local') is not None:
                base_64 = self.client_local_storage.load_image(
                    f"{Bucket.BUCKET}/{account_id}/{self.properties.get('folder_local')}/{self.properties.get('file_local')}",
                )

            self._load_image(base_64)
    
            self.remining_centromere = list(islice(self.remining_centromere, 6))
  
            for chrom in self.remining_centromere:
                self.kariotype_repository.bulk_update(self.properties.get('_id'), [
                    {
                        'id_chromosome': chrom.get('id_chromosome'),
                        'status_centromere': StatusChromosomeEnum.PROCESSING
                    }  
                ])
       
            self.centromere()
            return self.classify()

    # CENTROMERE STEP PROCCESS
    # functions to centromere chromosomes
    def _load_contour(self, objects: list) -> list:
        """Processes a list of contour objects and formats their coordinates.
        
        Performs the following operations:
        1. Formats base coordinates from contour objects
        2. Adjusts coordinates for "New polygon" objects by adding an offset
        3. Processes negative position values by converting them to positive
        4. Returns a list of formatted contour coordinates

        Args:
            objects: List of contour objects, where each object contains:
                - 'contour': List of coordinate dictionaries {'x', 'y'}
                - 'name': String identifier (special handling for "New polygon")
                - 'left': X-position (may be negative)
                - 'top': Y-position (may be negative)

        Returns:
            list: Nested list of formatted coordinates in the format:
                [[x1, y1], [x2, y2], ...] for each contour object

        Notes:
            - Negative 'left' and 'top' values are converted to positive
            - "New polygon" objects get additional coordinate offsets
            - Empty contours are filtered out
        """
        def format_object(item):
            """Extracts basic x,y coordinates from a coordinate item."""
            return [item['x'], item['y']]

        def format_new_object(item):
            """Formats coordinates with additional offset for new polygons."""
            return [item['x'] + self.coord_sum[0], item['y'] + self.coord_sum[1]]

        def format_list(item):
            """Processes a contour object and returns its formatted coordinates."""
            if len(item.get('contour')) > 0:
                if item.get('name') == "New polygon":
                    return list(map(format_new_object, item.get('contour')))
                return list(map(format_object, item.get('contour')))

        def format_coord(item):
            """Converts negative position values to positive."""
            left = abs(item.get('left', 0))
            top = abs(item.get('top', 0))
            return [left, top]
 
        self.coord_sum = format_coord(self.properties)
        contour = list(map(format_list, objects))
        return contour
    
    def _clean_base64(self, image_data):
        if image_data.startswith("data:image"):
            image_data = image_data.split(",")[1]

        image_data = re.sub(r'[^A-Za-z0-9+/=]', '', image_data)

        if isinstance(image_data, str):
            image_data = image_data.encode('utf-8')
        
        missing_padding = len(image_data) % 4
        if missing_padding:
            image_data += b'=' * (4 - missing_padding)
            
        return base64.b64decode(image_data)
   
    def centromere(self):
        """
        >>> TODO: Add more detailed docstring here
        """
        filtering = Filter(self.image)
        masking = Mask(filtering.morphological_filtration())

        for item in self.remining_centromere:
            contour = self._load_contour([item])
            
            image_mask = masking.build_mask((contour[0]))
            extracting = Extract(self.image, image_mask, filtering.morphological_filtration())
            singles, masks = extracting.extract_rgb()

            resizing = Resize()
            objects_rgb = resizing.Resize_images(singles)
            objects_binaries = resizing.Resize_images(masks)
        
            rotating_rgb = Rotation(objects_rgb[0], objects_binaries[0], self.logger)
            rotated_image_rgb, rotated_image_rgb_binary = rotating_rgb.rotation_particle()

            rotating_gray = Rotation(objects_rgb[0], objects_binaries[0], self.logger)
            rotated_image_gray, rotated_image_gray_binary = rotating_gray.rotation_particle_gray()

            zhang_sue = ZhangSue(rotated_image_rgb, rotated_image_rgb_binary.copy(), 0)
            points = zhang_sue.skel_chromosome()

            converting_rgb = NumpyToPng(rotated_image_rgb, self.logger)
            image_base64_rgb = converting_rgb.convert()

            converting_gray = NumpyToPng(rotated_image_gray, self.logger)
            image_base64_gray = converting_gray.convert_gray_image(rotated_image_rgb)

            account_id = self.properties.get('team_id') if self.properties.get('team_id') else self.properties.get('user_id')
            file_rgb_name = f"{str(uuid.uuid4())}.png"
            file_gray_name = f"{str(uuid.uuid4())}.png"

            if self.properties.get('file_s3') is not None:
                self.client_s3.upload_image(
                    self._clean_base64(image_base64_rgb),
                    Bucket.BUCKET,
                    f"{account_id}/{self.properties.get('folder_s3')}{Bucket.CROPED_RGB_FOLDERS}{file_rgb_name}"
                )
                self.client_s3.upload_image(
                    self._clean_base64(image_base64_gray),
                    Bucket.BUCKET,
                    f"{account_id}/{self.properties.get('folder_s3')}{Bucket.CROPED_GRAY_FOLDERS}{file_gray_name}"
                )

            if self.properties.get('file_gcs') is not None:
                self.client_google_cloud.upload_image(
                    self._clean_base64(image_base64_rgb),
                    f"{account_id}/{self.properties.get('folder_gcs')}{Bucket.CROPED_RGB_FOLDERS}{file_rgb_name}"
                )
                self.client_google_cloud.upload_image(
                    self._clean_base64(image_base64_gray),
                    f"{account_id}/{self.properties.get('folder_gcs')}{Bucket.CROPED_GRAY_FOLDERS}{file_gray_name}"
                )

            if self.properties.get('file_local') is not None:
                self.client_local_storage.upload_image(
                    self._clean_base64(image_base64_rgb),
                    f"{Bucket.BUCKET}/{account_id}/{self.properties.get('folder_local')}{Bucket.CROPED_RGB_FOLDERS}{file_rgb_name}"
                )
                self.client_local_storage.upload_image(
                    self._clean_base64(image_base64_gray),
                    f"{Bucket.BUCKET}/{account_id}/{self.properties.get('folder_local')}{Bucket.CROPED_GRAY_FOLDERS}{file_gray_name}"
                )

            self.kariotype_repository.bulk_update(
                self.properties.get('_id'),
                [
                    {
                        'id_chromosome': item.get('id_chromosome'),
                        'status_centromere': StatusChromosomeEnum.PROCESSED,
                        'file_rgb_s3': file_rgb_name if self.properties.get('file_s3') is not None else None,
                        'file_gray_s3': file_gray_name if self.properties.get('file_s3') is not None else None,
                        'file_rgb_gcs': file_rgb_name if self.properties.get('file_gcs') is not None else None,
                        'file_gray_gcs': file_gray_name if self.properties.get('file_gcs') is not None else None,
                        'file_rgb_local': file_rgb_name if self.properties.get('file_local') is not None else None,
                        'file_gray_local': file_gray_name if self.properties.get('file_local') is not None else None,
                        'dimension': {
                            'x': rotated_image_rgb.shape[1],
                            'y': rotated_image_rgb.shape[0]
                        },
                        'centromere_coord': {
                            'x': int(points[1]),
                            'y': int(points[0])
                        }
                    }
                ]
            )
            self.remining_centromered.append({ 
                'id': item.get('id'),
                'id_chromosome': item.get('id_chromosome'),
                'base64_gray': image_base64_gray,
                'base64_rgb': image_base64_rgb,
                'file_rgb_s3': file_rgb_name if self.properties.get('file_s3') is not None else None,
                'file_gray_s3': file_gray_name if self.properties.get('file_s3') is not None else None,
                'file_rgb_gcs': file_rgb_name if self.properties.get('file_gcs') is not None else None,
                'file_gray_gcs': file_gray_name if self.properties.get('file_gcs') is not None else None,
                'file_rgb_local': file_rgb_name if self.properties.get('file_local') is not None else None,
                'file_gray_local': file_gray_name if self.properties.get('file_local') is not None else None,
                'dimension': {
                    'x': rotated_image_rgb.shape[1],
                    'y': rotated_image_rgb.shape[0]
                },
                'centromere': {
                    'x': int(points[1]),
                    'y': int(points[0])
                }
            })


    # CLASSIFY STEP PROCCESS
    # functions to classify chromosomes
    def _load_image_grey(self, base_64):
        image_base64 = base_64
        image_b64 = image_base64.split(",")[1]
        binary = base64.b64decode(image_b64)
        image = np.asarray(bytearray(binary), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        self.image_gray = image

    def _load_image_rgb(self, base_64):
        image_base64 = base_64
        image_b64 = image_base64.split(",")[1]
        binary = base64.b64decode(image_b64)
        image = np.asarray(bytearray(binary), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        self.image_rgb = image

    def _generate_chromosome_data_text(self, chromosome_data):
        """
        Generate formatted text for chromosome data.

        Args:
        - chromosome_data (list): List of dictionaries containing chromosome data.

        Returns:
        - formatted_text (str): Formatted text containing chromosome data base GFF.
        """
        formatted_text = "#chrom\tchromStart\tchromEnd\ttype\tcolor\n"
        for chromosome in chromosome_data:
            # First part: gray
            formatted_text += f"chr{chromosome['id_chromosome']}\t0\t{chromosome['centromere_bp']}\tmarker\tgray\n"
            # Centromere: pink
            formatted_text += f"chr{chromosome['id_chromosome']}\t{chromosome['centromere_bp']}\t{chromosome['centromere_bp'] + 2}\tcentromere\tpink\n"
            # Third part: gray
            formatted_text += f"chr{chromosome['id_chromosome']}\t{chromosome['centromere_bp'] + 2}\t{chromosome['base_pairs']}\tmarker\tgray\n"
        return formatted_text
    
    def _generate_txt_download_format(self, chromosome_data_text):
        """
        Generate download format for the TXT file.

        Args:
        - chromosome_data_text (str): Formatted text containing chromosome data.

        Returns:
        - download_format (dict): Dictionary containing text and download format.
        """
        download_format = {
            "text": chromosome_data_text,
            "download_format": "txt"
        }
        return download_format
    
    def _sort_chromosomes(self, chromosomes, centromeric_index: bool = False):
        """
        Sorts the chromosomes based on 'size_chrom' or 'rb_mean' if ordenation_type is 'xx',
        while removing duplicates based on the 'id_chromosome' key.

        Args:
            chromosomes (list): A list of dictionaries, each representing a chromosome with 
                                'size_chrom', 'rb_mean', and 'id_chromosome' keys.
            ordenation_type (str): Determines the sorting criteria.

        Returns:
            list: The sorted list of chromosomes. If the input list is empty, returns an empty list.
        """
        if not chromosomes:
            return []
        sort_key = 'rb_mean' if centromeric_index else 'size_chrom'
        sorted_chromosomes = sorted(chromosomes, key=lambda x: x.get(sort_key, 0), reverse=True)
        return sorted_chromosomes
 
    def _format_number_round(self, number):
        return float(round(number, 2))
    
    def _format_class_brev(self, class_name):
        classes = {
            'metacentric': 'm',
            'acrocentric': 'a',
            'submetacentric': 'sm',
            'subtelocentric': 'st'
        }
        return classes[class_name]
    
    def _define_background_dimension_kariotype(self, quantity: int = 100):
        """
        Defines the ideal background dimensions for the karyotype based on the number of items.

        Parameters:
            quantity (int): The number of items to display. Default is 100.

        Returns:
            tuple: A tuple containing (width, height) in pixels.
        """
        width = 3000
        if quantity <= 100:
            height = 900
        elif quantity <= 500:
            height = 1200
        elif quantity <= 1000:
            height = 1600
        else:
            height = 1600 + (((quantity - 1000) // 500 + 1) * 200)
        return width, height
    
    def _normalize_angle(self, angle):
        """Converts negative angles to their positive equivalent in [0, 360) range,
        while leaving positive angles (including > 360) unchanged.

        This is useful for systems that:
        - Require angles to be non-negative (e.g., canvas rotations)
        - Need to preserve multi-rotation values (e.g., 370° = 1 full rotation + 10°)

        Args:
            angle: Input angle in degrees. Can be negative or arbitrarily large.

        Returns:
            float: 
            - If input is negative: Equivalent positive angle (0 ≤ θ < 360)
            - If input is positive: Returns the exact same angle (even if > 360)

        Examples:
            >>> normalize_angle(-159.31)
            200.69
            >>> normalize_angle(370)
            370
            >>> normalize_angle(45)
            45
        """
        return angle % 360 if angle < 0 else angle
 
    def _format_measuring_ruler(
            self, 
            upper, 
            lower, 
            centromere, 
            base_payload: dict,
            data_group_template: dict,
            obj_id: int,
            width: int,
            height: int,
            reference_width: int,
            reference_height: int,
            reference_top: int,
            reference_left: int,
            angle: int
        ):
        """
        Creates a payload for a curved measuring ruler object by closing the contour path.

        Args:
            contour (list): A list of (y, x) coordinates representing the curved contour.
            base_payload (dict): The base data dictionary to update.
            obj_id (int): Identifier for the object.
            ...
            >>> TODO: Add more detailed docstring here
            >>> TODO: 
                Issue:
                When resizing the canvas, grouped objects lose their original positions and drift within the work area.

                Action Items:
                Correct the group model structure to comply with Fabric.js requirements
                Notes:
                Validate canvas handling functions in the platform project codebase
                Ensure position persistence during canvas resize operations

        Returns:
            dict: The updated payload with geometric information and closed polygon path.
        """
        def build_polygon(coords, label, stroke):
            if not coords:
                return None

            contour_np = np.array(coords)
            Xmin = np.min(contour_np[:, 0])
            Ymin = np.min(contour_np[:, 1])
            top_poly = Xmin
            left_poly = Ymin

            points_forward = [{"x": int(p[1]), "y": int(p[0])} for p in coords]

            poly_payload = base_payload.copy()
            poly_payload.update({
                'id': str(uuid.uuid4()),
                'type': 'polygon',
                'points': points_forward,
                'top': float(top_poly),
                'left': float(left_poly),
                'name': "measure-label-" + str(obj_id),
                'id_chromosome': str(obj_id),
                'stroke': stroke
            })
            return poly_payload
   
        upper_poly = build_polygon(upper, 'Upper', "rgba(255,0,0,1)") # Red
        lower_poly = build_polygon(lower, 'Lower', "rgba(0,0,255,1)") # Blue
        centromere_poly = build_polygon([(centromere.get('x'), centromere.get('y'))], 'Centromere', "rgba(0,255,0,1)") # Green 
     
        objects = [poly for poly in [upper_poly, lower_poly, centromere_poly] if poly]

        top_group = reference_top + (reference_height - height) / 2
        left_group = reference_left + (reference_width - width) / 2
    
        group_payload = {
            **data_group_template.copy(),
            'id': str(uuid.uuid4()),
            'type': 'group',
            'objects': objects,
            'name': "group-"+str(obj_id),
            'id_chromosome': str(obj_id),
            'width': float(width),
            'height': float(height),
            'top': float(top_group) if angle == 0 else float(top_group) + float(height) / 2,
            'left': float(left_group) if angle == 0 else float(left_group) + float(width) / 2,
            'angle': self._normalize_angle(angle),
            'originX': 'left' if angle == 0 else 'center',
            'originY': 'top' if angle == 0 else 'center',
        }

        return group_payload

    def _get_circle_center(self, x, y, radius):
        """
        Calculates the center of a circle given the top-left coordinates and the radius.

        Args:
            x (float): The x-coordinate of the top-left corner of the bounding box.
            y (float): The y-coordinate of the top-left corner of the bounding box.
            radius (float): The radius of the circle.

        Returns:
            tuple: The (x, y) coordinates of the center of the circle.
        """
        center_x = x + 4
        center_y = y + 4
        return (center_x, center_y)

    def _load_image(self, base_64):
        self.image_base64 = base_64
        image_b64 = self.image_base64.split(",")[1]
        binary = base64.b64decode(image_b64)
        image = np.asarray(bytearray(binary), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        self.image = image
    
    def _convert_coordinate_path_measure(
        self,
        coords: Union[List[Tuple[float, float]], List[Dict[str, float]]],
        load: bool = False
    ) -> Union[List[Dict[str, float]], List[Tuple[float, float]]]:
        """
        Converts between coordinate path formats:
        
        - **When load=False**:  
        Converts `[(y, x), (y, x), ...]` → `[{'x': x, 'y': y}, ...]`  
        
        - **When load=True**:  
        Converts `[{'x': x, 'y': y}, ...]` → `[(y, x), (y, x), ...]`

        Args:
            coords (Union[List[Tuple[float, float]], List[Dict[str, float]]]):  
                - Se load=False: Recebe `[(y, x), (y, x), ...]`  
                - Se load=True: Recebe `[{'x': x, 'y': y}, ...]`  
            load (bool):  
                - False (default):
                - True: Converte dicionários → tuplas.  

        Returns:
            Union[List[Dict[str, float]], List[Tuple[float, float]]]:  
                - Se load=False: Retorna `[{'x': x, 'y': y}, ...]`  
                - Se load=True: Retorna `[(y, x), (y, x), ...]`  

        Examples:
            >>> coords = [(12, 24), (13, 25), (14, 25)]
            >>> convert_coordinate_path(coords)
            [{'x': 24, 'y': 12}, {'x': 25, 'y': 13}, {'x': 25, 'y': 14}]

            >>> json_coords = [{'x': 24, 'y': 12}, {'x': 25, 'y': 13}]
            >>> convert_coordinate_path(json_coords, load=True)
            [(12, 24), (13, 25)]
        """
        if load:
            return [(point['y'], point['x']) for point in coords]
        else:
            return [{'x': int(p[1]), 'y': int(p[0])} for p in coords]
    
    def classify(self):
        ordenation_list = [OrdenationTypeEnum.CLASS_SIZE, OrdenationTypeEnum.CLASS_INDEX_CENTROMERIC]
        path_base = self.path_payload_kariotype_v1 if self.properties.get('ordenation_type') in ordenation_list else self.path_payload_kariotype
        with open(path_base) as file_payload_kariotype:
            data_kariotype = json.load(file_payload_kariotype)

        with open(self.path_payload_image) as file_payload_image:
            data_image_template = json.load(file_payload_image)

        with open(self.path_payload_polygon) as file_payload_polygon:
            data_polygon_template = json.load(file_payload_polygon)

        with open(self.path_payload_group) as file_group_polygon:
            data_group_template = json.load(file_group_polygon)

        with open(self.path_payload_text_label) as file_payload_text_label:
            data_text_label_template = json.load(file_payload_text_label)

        with open(self.path_payload_text_size) as file_payload_text_size:
            data_text_size_template = json.load(file_payload_text_size)

        position_chromosome_left = 374.06
        position_chromosome_top = 194.86
        position_label_left = 390.06
        position_label_top = 291.04
        position_size_left = 390.06
        position_size_top = 160.22

        vertical_increment = 150

        chrom_list = []
        chrom_list_ids = []

        calculator = ChromosomeCalculator(self.properties.get('field_of_view'), self.properties.get('image_resolution'))
        account_id = self.properties.get('team_id') if self.properties.get('team_id') else self.properties.get('user_id')

        for obj in self.remining_centromered:
            id_chromosome = obj.get('id_chromosome')
            self._load_image_grey(obj['base64_gray'])
            image_gray = self.image_gray

            converting_gray = NumpyToPng(image_gray, self.logger)
            image_binary = converting_gray.generate_binary_mask_not_morph(image_gray)
            zhang_sue = ZhangSue(image_gray, image_binary.copy(), id_chromosome)
            if zhang_sue.skel is None:
                self.kariotype_repository.bulk_update(
                self.properties.get('_id'), 
                [
                    { 
                        'id_chromosome': id_chromosome, 
                        'empty': True,
                        'status_preclassification': StatusChromosomeEnum.PROCESSED
                    }
                ]
            )

            x, y = self._get_circle_center(obj['centromere']['y'], obj['centromere']['x'], radius=1)
            classifier = ClassifyAdjustAnomalous(zhang_sue.skel, image_binary, [x, y], self.logger)
            chromosomes_class_geodesic, rb_geodesic = classifier.chromosome_classify_geodesic()
            #chromosomes_class_point_to_point, rb_point = classifier.chromosome_classify_point_to_point()
            chromosomes_class_simple, rb_simple = classifier.chromosome_classify_simple()
            size_geodesic = classifier.size_chromosome_geodesic()
            #size_point_to_point = classifier.size_chromosome_point_to_point()
            size_simple = classifier.size_chromosome_simple()
            obj_area = classifier.calculate_binary_object_area()
            upper_chromatide_size = classifier.calculate_final_upper_chromatide()
            centromere_position_and_lower_value = classifier.calculate_final_lower_chromatide()
            size = upper_chromatide_size + centromere_position_and_lower_value
            rb_mean = classifier.rb_chromosome_default(upper_chromatide_size, centromere_position_and_lower_value)
            chromosomes_class = classifier.chromosome_classify(rb_mean)
            measure_width, measure_height = classifier.calculate_binary_dimensions()
            upper_measure_ruler, lower_measure_ruler, centromere_ruler = classifier.measure_ruler_paths()

            pixel_size = calculator.calculate_pixel_size()
            chromosome_size_micrometers = calculator.calculate_chromosome_size(pixel_size, self._format_number_round(size))
            centromere_bp = calculator.calculate_chromosome_size(pixel_size, centromere_position_and_lower_value)

            # if os.getenv("ENV") != 'production':
            #     save_result(classifier=classifier, skel=zhang_sue.skel, image=image_gray, id_chromosome=id_chromosome)
        
            chromosome  = {
                'status_preclassification': StatusChromosomeEnum.PROCESSED,
                'agent_who_identified_rotation': 'auto',
                'chromosomes_class_geodesic': chromosomes_class_geodesic,
                'chromosomes_class_point_to_point': None,
                'chromosomes_class_simple': chromosomes_class_simple,
                'rb_geodesic': rb_geodesic,
                'rb_point': None,
                'rb_simple': rb_simple,
                'rb_mean': rb_mean,
                'size_geodesic': size_geodesic,
                'size_point_to_point': None,
                'size_simple': size_simple,
                'upper_measure_ruler': self._convert_coordinate_path_measure(upper_measure_ruler),
                'lower_measure_ruler': self._convert_coordinate_path_measure(lower_measure_ruler),
                'chromosomes_class': chromosomes_class,
                'size_chrom': self._format_number_round(size),
                'obj_area': self._format_number_round(obj_area),
                'centromere_start': centromere_position_and_lower_value,
                'lower_chromatide_size': centromere_position_and_lower_value,
                'upper_chromatide_size': upper_chromatide_size,
                'measure_width': measure_width,
                'measure_height': measure_height,
                'type_chromosomes': True,
                'base_pairs': self._format_number_round(chromosome_size_micrometers),
                'centromere_bp': self._format_number_round(centromere_bp),
                'centromere_coord': {
                    'x': int(centromere_ruler[1]),
                    'y': int(centromere_ruler[0])
                },
                'id_chromosome': id_chromosome
            }

            self.kariotype_repository.bulk_update(
                self.properties.get('_id'), 
                [chromosome]
            )
            
            if not self.mod_consumer:
                chromosome['base64_rgb'] = obj['base64_rgb']
                chromosome['base64_gray'] = obj['base64_gray']
                chromosome['file_rgb_s3'] = obj['file_rgb_s3']
                chromosome['file_gray_s3'] = obj['file_gray_s3']
                chromosome['file_rgb_gcs'] = obj['file_rgb_gcs']
                chromosome['file_gray_gcs'] = obj['file_gray_gcs']
                chromosome['file_rgb_local'] = obj['file_rgb_local']
                chromosome['file_gray_local'] = obj['file_gray_local']
                chromosome['chromosomes_class'] = chromosomes_class
                chromosome['rb_mean'] = rb_mean
                chromosome['upper_measure_ruler'] = self._convert_coordinate_path_measure(upper_measure_ruler)
                chromosome['lower_measure_ruler'] = self._convert_coordinate_path_measure(lower_measure_ruler)
                chromosome['measure_width'] = measure_width
                chromosome['measure_height'] = measure_height
                chromosome['rotation'] = { 'angle': 0 },
                chromosome['dimension'] = obj.get('dimension')
                chromosome['centromere_coord'] = {
                    'x': int(centromere_ruler[1]),
                    'y': int(centromere_ruler[0])
                }
                chromosome['id_chromosome'] = id_chromosome
                chromosome['rotation'] = { 'angle': obj['angle'] if obj.get('angle') is not None else 0 }
                chromosome['id'] = str(obj['id'])
                
            chrom_list.append(chromosome)
            chrom_list_ids.append(id_chromosome)

        has_processed_property = self.kariotype_repository.get_by_id(self.properties.get('_id'))
        has_processed = [
            obj for obj in has_processed_property.get('chromosomes')
            if obj.get('status_centromere') == StatusChromosomeEnum.PROCESSED and \
            obj.get('status_preclassification') == StatusChromosomeEnum.PROCESSED and \
            obj.get('empty') is not True
        ]

        has_pending_or_processing = [
            obj for obj in has_processed_property.get('chromosomes')
            if obj.get('status_centromere') in [StatusChromosomeEnum.PENDING, StatusChromosomeEnum.PROCESSING] or \
            obj.get('status_preclassification') in [StatusChromosomeEnum.PENDING, StatusChromosomeEnum.PROCESSING]
        ]

        for obj_chrom in has_processed:
            if obj_chrom.get('id_chromosome') in chrom_list_ids or obj_chrom.get('empty') is True:
                return None
            
            if not self.mod_consumer:
                if self.properties.get('file_s3') is not None:
                    base_64_rgb = self.client_s3.load_image(
                        f"{account_id}/{self.properties.get('folder_s3')}{Bucket.CROPED_RGB_FOLDERS}{obj_chrom.get('file_rgb_s3')}",
                        Bucket.BUCKET
                    )
                if self.properties.get('file_gcs', None) is not None:
                    base_64_rgb = self.client_google_cloud.load_image(
                        f"{account_id}/{self.properties.get('folder_gcs')}{Bucket.CROPED_RGB_FOLDERS}{obj_chrom.get('file_rgb_gcs')}",
                    )
                if self.properties.get('file_local', None) is not None:
                    base_64_rgb = self.client_local_storage.load_image(
                        f"{Bucket.BUCKET}/{account_id}/{self.properties.get('folder_local')}{Bucket.CROPED_RGB_FOLDERS}{obj_chrom.get('file_rgb_local')}",
                    )
                obj_chrom['base64_rgb'] = base_64_rgb
            chrom_list.append(obj_chrom)
  
        def append_chromosome_data(chromosomes, position_chromosome_left, position_chromosome_top, position_label_left, position_label_top, position_size_left, position_size_top, index, kariotype):
            for chromosome in chromosomes:
                if chromosome.get('empty') is True:
                    continue
                
                offset = 15 if index % 2 != 0 else 30
                offset = offset + chromosome.get('measure_width', 0)

                data_image = data_image_template.copy()
                data_text_label = data_text_label_template.copy()
                data_text_size = data_text_size_template.copy()

                data_text_size['text'] = f"{str(chromosome.get('size_chrom'))}px ID:{chromosome.get('id_chromosome')}"
                data_text_size['name'] = data_text_size['text']
                data_text_size['left'] = position_size_left
                data_text_size['top'] = position_size_top
                data_text_size['id_chromosome'] = chromosome.get("id_chromosome")
                data_text_size['id'] = str(chromosome.get("id"))
                kariotype.append(data_text_size.copy())
                position_size_left += offset

                angle = chromosome.get('rotation').get('angle', 0) if chromosome.get('rotation') else 0
                data_image['src'] = None if self.mod_consumer else chromosome['base64_rgb']
                data_image['left'] = position_chromosome_left if angle == 0 else position_chromosome_left + chromosome['dimension']['x'] / 2
                data_image['top'] = position_chromosome_top  if angle == 0 else position_chromosome_top + chromosome['dimension']['y'] / 2
                data_image['name'] = f"chrom {index}"
                data_image['id_chromosome'] = chromosome.get("id_chromosome")
                data_image['id'] = str(chromosome.get("id"))
                data_image['file_rgb_s3'] = chromosome.get('file_rgb_s3')
                data_image['file_gray_s3'] = chromosome.get('file_gray_s3')
                data_image['file_rgb_gcs'] = chromosome.get('file_rgb_gcs')
                data_image['file_gray_gcs'] = chromosome.get('file_gray_gcs')
                data_image['file_rgb_local'] = chromosome.get('file_rgb_local')
                data_image['file_gray_local'] = chromosome.get('file_gray_local')
                data_image['originX'] = 'center' if angle != 0 else 'left'
                data_image['originY'] = 'center' if angle != 0 else 'top'
                data_image['angle'] = angle
                data_image['tooltip']['template'] = f"<div>chr{chromosome['id_chromosome']} | micrometers {chromosome.get('base_pairs')}</div>"
                kariotype.append(data_image.copy())
        
                measure_ruler = self._format_measuring_ruler(
                    upper=self._convert_coordinate_path_measure(chromosome['upper_measure_ruler'], load=True), 
                    lower=self._convert_coordinate_path_measure(chromosome['lower_measure_ruler'], load=True), 
                    centromere=chromosome['centromere_coord'], 
                    base_payload=data_polygon_template,
                    data_group_template=data_group_template,
                    obj_id=chromosome['id_chromosome'], 
                    width=chromosome['measure_width'], 
                    height=chromosome['measure_height'],
                    reference_width=chromosome['dimension']['x'],
                    reference_height=chromosome['dimension']['y'],
                    reference_top=position_chromosome_top, 
                    reference_left=position_chromosome_left,
                    angle=angle
                )
                if measure_ruler:
                    kariotype.append(measure_ruler)
                position_chromosome_left += offset

                data_text_label['text'] = f"{index} {self._format_class_brev(chromosome['chromosomes_class'])}"
                data_text_label['left'] = position_label_left
                data_text_label['top'] = position_label_top
                data_text_label['name'] = data_text_label['text']
                data_text_label['id_chromosome'] = chromosome.get("id_chromosome")
                data_text_label['id'] = str(chromosome.get("id"))
                kariotype.append(data_text_label.copy())
                position_label_left += offset

                index += 1
            return index

        width_background, heigth_background = self._define_background_dimension_kariotype(len(chrom_list))
        index_object_image = next((i for i, obj in enumerate(data_kariotype.get("objects")) if obj.get("type") == "image" and obj.get("refs") == "background"), -1)
        data_kariotype['objects'][index_object_image]['width'] = width_background
        data_kariotype['objects'][index_object_image]['height'] = heigth_background
        kariotype = []
        chrom_list_sorted = []

        if self.properties.get('ordenation_type') in [OrdenationTypeEnum.SIZE, OrdenationTypeEnum.INDEX_CENTROMERIC]:
            centromeric_index = True if self.properties.get('ordenation_type') == OrdenationTypeEnum.INDEX_CENTROMERIC else False
            chrom_list_sorted = self._sort_chromosomes(chrom_list, centromeric_index=centromeric_index)
            max_items = next((i for i, w in enumerate(itertools.accumulate(obj["measure_width"] for obj in chrom_list_sorted if obj.get("measure_width") is not None)) if w > width_background), sum(1 for obj in chrom_list_sorted if obj.get("measure_width") is not None))
            max_items = max(1, max_items)
            chromosome_slices = [chrom_list_sorted[i:i + max_items] for i in range(0, len(chrom_list_sorted), max_items)]
            base_height = max(
                (obj.get("measure_height") for obj in chrom_list_sorted if obj.get("measure_height") is not None),
                default=-1
            )
            
            index = 1
            for slice_index, chromosomes in enumerate(chromosome_slices):
                index = append_chromosome_data(
                    chromosomes,
                    position_chromosome_left,
                    position_chromosome_top,
                    position_label_left,
                    position_label_top,
                    position_size_left,
                    position_size_top,
                    index,
                    kariotype
                )
                position_chromosome_left = 374.06
                position_chromosome_top += vertical_increment + base_height
                position_label_left = 390.06
                position_label_top += vertical_increment + base_height
                position_size_left = 390.06
                position_size_top += vertical_increment + base_height
       
        if self.properties.get('ordenation_type') in [OrdenationTypeEnum.CLASS_SIZE, OrdenationTypeEnum.CLASS_INDEX_CENTROMERIC]:
            centromeric_index = True if self.properties.get('ordenation_type') == OrdenationTypeEnum.CLASS_INDEX_CENTROMERIC else False
            chrom_list_sorted = self._sort_chromosomes(chrom_list, centromeric_index=centromeric_index)
            class_groups = {}
            for chrom in chrom_list_sorted:
                cls = chrom.get('chromosomes_class', 'unknown')
                class_groups.setdefault(cls, []).append(chrom)
           
            index = 1
            position_class = position_chromosome_top
            for chrom_class in ['metacentric', 'submetacentric', 'subtelocentric', 'acrocentric']:
                chromosomes = class_groups.get(chrom_class, [])

                index_class = next((i for i, obj in enumerate(data_kariotype.get("objects")) if obj.get("type") == "textbox" and obj.get("text") == self._format_class_brev(chrom_class)), -1)
                data_kariotype['objects'][index_class]['top'] = position_class
                index_class = next((i for i, obj in enumerate(data_kariotype.get("objects")) if obj.get("type") == "line" and obj.get("refer") == self._format_class_brev(chrom_class)), -1)
                data_kariotype['objects'][index_class]['top'] = position_class # height line is fixed 50.32
                base_height = max(
                    (obj.get("measure_height") for obj in chromosomes if obj.get("measure_height") is not None),
                    default=-1
                )
                position_class += vertical_increment + base_height
                max_items = next((i for i, w in enumerate(itertools.accumulate(obj["measure_width"] for obj in chromosomes if obj.get("measure_width") is not None)) if w > width_background), sum(1 for obj in chromosomes if obj.get("measure_width") is not None))
                max_items = max(1, max_items)
                chromosome_slices = [chromosomes[i:i + max_items] for i in range(0, len(chromosomes), max_items)]
                for slice_index, slice_group in enumerate(chromosome_slices):
                    index = append_chromosome_data(
                        slice_group,
                        position_chromosome_left,
                        position_chromosome_top,
                        position_label_left,
                        position_label_top,
                        position_size_left,
                        position_size_top,
                        index,
                        kariotype
                    )
                    position_chromosome_left = 374.06
                    position_chromosome_top += vertical_increment + base_height
                    position_label_left = 390.06
                    position_label_top += vertical_increment + base_height
                    position_size_left = 390.06
                    position_size_top += vertical_increment + base_height

        data_kariotype['objects'] = data_kariotype['objects'] + kariotype

        if self.mod_consumer:
            if len(kariotype) > 0:
                self.kariotype_repository.update(
                    self.properties,
                    {
                        'canva': data_kariotype,
                        'finished': True if len(has_pending_or_processing) == 0 else False,
                        'status': StatusKariotypeEnum.CLASSIFIED_CHROMOSOMES
                    }
                )

        if (len(has_pending_or_processing) > 0) or (len(has_pending_or_processing) == 0 and not self.mod_consumer):
            self.publish({ 
                "kariotype_id": self.properties.get('_id')
            }, routing_key="classification_queue")

        elif len(has_pending_or_processing) == 0:
            ideogram = self.ideogram_repository.create(
                IdeogramModel(
                    kariotype_id=self.properties.get('_id'),
                    text_gff=self._generate_chromosome_data_text(chrom_list_sorted),
                    team_id=self.properties.get('team_id'),
                    user_id=self.properties.get('user_id')
                )
            )
            self.publish_ideogram({ 
                "ideogram_id": ideogram.get('_id')
            }, routing_key="ideogram_queue")

        if not self.mod_consumer:
            response = {
                'kariotype': data_kariotype,
            }
            return response


    def preclassify(self):
        radius_circle = 4
        chromosomes = []

        self.properties = self.kariotype_repository.get_by_id(self.data['config_chromosome'].get('kariotype_id'))
        calculator = ChromosomeCalculator(self.data['config_chromosome'].get('field_of_view'), self.data['config_chromosome'].get('image_resolution'))

        for obj in self.data['objects']:
            image_base64_gray = None
            image_base64_rgb = None
            id_chromosome = obj.get('id')

            obj_ = next((obj_ for obj_ in self.properties.get('chromosomes', []) if obj_["id_chromosome"] == id_chromosome), None)
            account_id = self.properties.get('team_id') if self.properties.get('team_id') else self.properties.get('user_id')
            
            if self.properties.get('file_s3') is not None:
                base_64_gray = self.client_s3.load_image(
                    f"{account_id}/{self.properties.get('folder_s3')}{Bucket.CROPED_GRAY_FOLDERS}{obj_.get('file_gray_s3')}",
                    Bucket.BUCKET
                )
                base_64_rgb = self.client_s3.load_image(
                    f"{account_id}/{self.properties.get('folder_s3')}{Bucket.CROPED_RGB_FOLDERS}{obj_.get('file_rgb_s3')}",
                    Bucket.BUCKET
                )

            if self.properties.get('file_gcs', None) is not None:
                base_64_gray = self.client_google_cloud.load_image(
                    f"{account_id}/{self.properties.get('folder_gcs')}{Bucket.CROPED_GRAY_FOLDERS}{obj_.get('file_gray_gcs')}",
                )
                base_64_rgb = self.client_google_cloud.load_image(
                    f"{account_id}/{self.properties.get('folder_gcs')}{Bucket.CROPED_RGB_FOLDERS}{obj_.get('file_rgb_gcs')}",
                )

            if self.properties.get('file_local', None) is not None:
                base_64_gray = self.client_local_storage.load_image(
                    f"{Bucket.BUCKET}/{account_id}/{self.properties.get('folder_local')}{Bucket.CROPED_GRAY_FOLDERS}{obj_.get('file_gray_local')}",
                )
                base_64_rgb = self.client_local_storage.load_image(
                    f"{Bucket.BUCKET}/{account_id}/{self.properties.get('folder_local')}{Bucket.CROPED_RGB_FOLDERS}{obj_.get('file_rgb_local')}",
                )

            self._load_image_grey(base_64_gray)
            image_gray = self.image_gray

            self._load_image_rgb(base_64_rgb)
            image_rgb = self.image_rgb

            converting_gray = NumpyToPng(image_gray, self.logger)
            image_binary = converting_gray.generate_binary_mask_not_morph(image_gray)
           
            new_angle_value = ((obj or {}).get('rotation') or {}).get('angle')
            old_angle_value = ((obj_ or {}).get('rotation') or {}).get('angle')
            angle_value = new_angle_value if new_angle_value is not None else old_angle_value
            if angle_value == 0:
                angle_value = old_angle_value if old_angle_value is not None else 0

            if angle_value:
                rotation_angle_gray = RotationAngle(image_gray, angle_value, self.logger)
                image_gray = rotation_angle_gray.rotate_image()

                converting_gray = NumpyToPng(image_gray, self.logger)
                image_base64_gray = converting_gray.convert(rgba_mode=True)

                image_binary = converting_gray.generate_binary_mask_not_morph(image_gray.copy())

                rotation_angle_rgb = RotationAngle(image_rgb, angle_value, self.logger)
                image_rgb = rotation_angle_rgb.rotate_image()

                converting_rgb = NumpyToPng(image_rgb, self.logger)
                image_base64_rgb = converting_rgb.convert(rgba_mode=True)

            zhang_sue = ZhangSue(image_gray, image_binary, id_chromosome)
            if zhang_sue.skel is None:
                chromosomes.append({ 
                    'id': id_chromosome, 
                    'empty': True,
                    'status_preclassification': StatusChromosomeEnum.PROCESSED
                })
                continue

            x, y = self._get_circle_center(obj['centromere']['y'], obj['centromere']['x'], radius_circle)
            classifier = ClassifyAdjustAnomalous(zhang_sue.skel, image_binary, [x, y], self.logger)
            chromosomes_class_geodesic, rb_geodesic = classifier.chromosome_classify_geodesic() # fist calculate because the adjustment centromere localization
            # chromosomes_class_point_to_point, rb_point = classifier.chromosome_classify_point_to_point()
            chromosomes_class_simple, rb_simple = classifier.chromosome_classify_simple()
            size_geodesic = classifier.size_chromosome_geodesic()
            # size_point_to_point = classifier.size_chromosome_point_to_point()
            size_simple = classifier.size_chromosome_simple()
            obj_area = classifier.calculate_binary_object_area()
            upper_chromatide_size = classifier.calculate_final_upper_chromatide()
            centromere_position_and_lower_value = classifier.calculate_final_lower_chromatide()
            size = upper_chromatide_size + centromere_position_and_lower_value
            rb_mean = classifier.rb_chromosome_default(upper_chromatide_size, centromere_position_and_lower_value)
            chromosomes_class = classifier.chromosome_classify(rb_mean)
            measure_width, measure_height = classifier.calculate_binary_dimensions()
            upper_measure_ruler, lower_measure_ruler, centromere_ruler = classifier.measure_ruler_paths()
     
            pixel_size = calculator.calculate_pixel_size()
            chromosome_size_micrometers = calculator.calculate_chromosome_size(pixel_size, self._format_number_round(size))
            centromere_bp = calculator.calculate_chromosome_size(pixel_size, centromere_position_and_lower_value)
            base_pairs = self._format_number_round(chromosome_size_micrometers)
            centromere_bp_final = self._format_number_round(centromere_bp)

            # if os.getenv("ENV") != 'production':
            #     save_result(classifier=classifier, skel=zhang_sue.skel, image=image_gray, id_chromosome=id_chromosome)

            chromosomes.append({
                'rotation_by_user': obj.get('rotation') if obj.get('rotation') else None,
                'image_base64_gray': image_base64_gray if obj.get('rotation') else None,
                'image_base64_rgb': image_base64_rgb if obj.get('rotation') else None,
                'chromosomes_class_geodesic': chromosomes_class_geodesic,
                'chromosomes_class_point_to_point': None,
                'chromosomes_class_simple': chromosomes_class_simple,
                'rb_geodesic': rb_geodesic,
                'rb_point': None,
                'rb_simple': rb_simple,
                'rb_mean': rb_mean,
                'size_geodesic': size_geodesic,
                'size_point_to_point': None,
                'size_simple': size_simple,
                'chromosomes_class': chromosomes_class,
                'size_chromosome': self._format_number_round(size),
                'obj_area': self._format_number_round(obj_area),
                'centromere_chromosome': centromere_position_and_lower_value,
                'upper_measure_ruler': self._convert_coordinate_path_measure(upper_measure_ruler),
                'lower_measure_ruler': self._convert_coordinate_path_measure(lower_measure_ruler),
                'measure_width': measure_width,
                'measure_height': measure_height,
                'centromere': {
                    'x': int(centromere_ruler[1]),
                    'y': int(centromere_ruler[0])
                },
                'upper_chromatide': self._format_number_round(upper_chromatide_size),
                'lower_chromatide':  self._format_number_round(centromere_position_and_lower_value),
                'empty': False,
                'id': id_chromosome,
                'base_pairs': base_pairs,
                'centromere_bp': centromere_bp_final,
                'rotation': { 'angle': angle_value } if angle_value else None
            })

        return {
            'data': chromosomes
        }
