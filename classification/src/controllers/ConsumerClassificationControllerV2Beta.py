import numpy as np
import cv2
import base64
import os
from typing import List, Tuple, Union, Dict

from ..helpers.ClassifyAdjustAnomalous import ClassifyAdjustAnomalous
from ..helpers.ZhangSue import ZhangSue
from ..helpers.ChromosomeCalculator import ChromosomeCalculator
from ..helpers.NumpyToPng import NumpyToPng
from ..enums.StatusEnum import StatusKariotypeEnum, StatusChromosomeEnum
from ..enums.S3Enum import Bucket
from ..services.ClientS3 import ClientS3
from ..services.ClientGoogleDrive import ClientGoogleDrive
from ..services.ClientGoogleCloud import ClientGoogleCloud
from ..services.ClientLocalSorage import ClientLocalStorage
from ..db.KariotypeCrud import KariotypeRepository
from ..utils.debug_data import save_result


class ConsumerClassificationControllerV2beta:
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger
        self.image_gray = ""
        self.properties = None
        self.remining = None
        self.client_s3 = ClientS3()
        self.client_google_drive = ClientGoogleDrive()
        self.client_google_cloud = ClientGoogleCloud()
        self.client_local_storage = ClientLocalStorage()
        self.kariotype_repository = KariotypeRepository(self.db)

    def process_chrom(self, payload):
        id = payload.get('kariotype_id')
        self.properties = self.kariotype_repository.get_by_id(id)
    
        if self.properties.get('status') == StatusKariotypeEnum.CENTROMERE_LOCALIZED or \
            self.properties.get('status') == StatusKariotypeEnum.CLASSIFIED_CHROMOSOMES:
            self.remining = [
                obj for obj in self.properties.get('chromosomes')
                if obj.get('status_preclassification') == StatusChromosomeEnum.PENDING and \
                obj.get('id_chromosome') in payload.get('batch')
            ]
 
            for chrom in self.remining:
                self.kariotype_repository.bulk_update(id, [{
                'id_chromosome': chrom.get('id_chromosome'),
                'status_preclassification': StatusChromosomeEnum.PROCESSING 
                }])
      
            self.preclassify()

    def load_image_grey(self, base_64):
        image_base64 = base_64
        image_b64 = image_base64.split(",")[1]
        binary = base64.b64decode(image_b64)
        image = np.asarray(bytearray(binary), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image
    
    def format_number_round(self, number):
        return float(round(number, 2))
    
    def convert_coordinate_path_measure(
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
                - Se load=False: Param `[(y, x), (y, x), ...]`  
                - Se load=True: Param `[{'x': x, 'y': y}, ...]`  
            load (bool):  
                - False (default):
                - True: Convert dict → tuple.  

        Returns:
            Union[List[Dict[str, float]], List[Tuple[float, float]]]:  
                - Se load=False: Return `[{'x': x, 'y': y}, ...]`  
                - Se load=True: Return  `[(y, x), (y, x), ...]`  

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
    
    def get_circle_center(self, x, y, radius):
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
 
    def preclassify(self):
        radius_circle = 4
        account_id = self.properties.get('team_id') if self.properties.get('team_id') else self.properties.get('user_id')
        calculator = ChromosomeCalculator(self.properties.get('field_of_view'), self.properties.get('image_resolution'))
      
        for obj in self.remining:
            if self.properties.get('file_s3', None) is not None:
                base_64 = self.client_s3.load_image(
                    f"{account_id}/{self.properties.get('folder_s3')}{Bucket.CROPED_GRAY_FOLDERS}{obj.get('file_gray_s3')}",
                    Bucket.BUCKET
                )

            if self.properties.get('file_gcs', None) is not None:
                base_64 = self.client_google_cloud.load_image(
                    f"{account_id}/{self.properties.get('folder_gcs')}{Bucket.CROPED_GRAY_FOLDERS}{obj.get('file_gray_gcs')}",
                )

            if self.properties.get('file_local', None) is not None:
                base_64 = self.client_local_storage.load_image(
                    f"{Bucket.BUCKET}/{account_id}/{self.properties.get('folder_local')}{Bucket.CROPED_GRAY_FOLDERS}{obj.get('file_gray_local')}",
                )

            image_gray = self.load_image_grey(base_64)

            converting_gray = NumpyToPng(image_gray, self.logger)
            image_binary = converting_gray.generate_binary_mask_not_morph(image_gray)
            zhang_sue = ZhangSue(image_gray, image_binary.copy(), 0)
            if zhang_sue.skel is None:
                self.kariotype_repository.bulk_update(
                self.properties.get('_id'), 
                [
                    { 
                        'id_chromosome': obj.get('id_chromosome'), 
                        'empty': True,
                        'status_preclassification': StatusChromosomeEnum.PROCESSED
                    }
                ]
            )
                continue
        
            x, y = self.get_circle_center(obj['centromere_coord']['y'], obj['centromere_coord']['x'], radius_circle)
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
            chromosome_size_micrometers = calculator.calculate_chromosome_size(pixel_size, self.format_number_round(size))
            centromere_bp = calculator.calculate_chromosome_size(pixel_size, centromere_position_and_lower_value)
            base_pairs = self.format_number_round(chromosome_size_micrometers)
            centromere_bp_final = self.format_number_round(centromere_bp)

            # if os.getenv("ENV") != 'production':
            #     save_result(classifier=classifier, skel=zhang_sue.skel, image=image_gray, id_chromosome=obj.get('id_chromosome'))

            chromosome = {
                'id_chromosome': obj.get('id_chromosome'),
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
                'chromosomes_class': chromosomes_class,
                'size_chrom': self.format_number_round(size),
                'obj_area': self.format_number_round(obj_area),
                'centromere_start': centromere_position_and_lower_value,
                'upper_chromatide_size': self.format_number_round(upper_chromatide_size),
                'lower_chromatide_size':  self.format_number_round(centromere_position_and_lower_value),
                'upper_measure_ruler': self.convert_coordinate_path_measure(upper_measure_ruler),
                'lower_measure_ruler': self.convert_coordinate_path_measure(lower_measure_ruler),
                'measure_width': measure_width,
                'measure_height': measure_height,
                'centromere_coord': {
                    'x': int(centromere_ruler[1]),
                    'y': int(centromere_ruler[0])
                },
                'base_pairs': base_pairs,
                'centromere_bp': centromere_bp_final
            }
            self.kariotype_repository.bulk_update(
                self.properties.get('_id'), 
                [chromosome]
            )
