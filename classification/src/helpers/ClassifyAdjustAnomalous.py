import numpy as np
from skimage import feature, measure, morphology
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import cv2
from itertools import combinations
from collections import deque
from scipy.spatial.distance import cdist
from skimage.draw import line
from math import sqrt


class ClassifyAdjustAnomalous:
    #DOCUMENTATION LOGIC: 
    """
        Calculates distances between chromatid points and centromere using different methods.

        Parameters:
        -----------
        image : ndarray
            Binary image containing chromatids and centromere (uint8 format, 0-255)
        method : str, optional
            Distance calculation method ('geodesic', 'point to point', 'simple_euclidean')
            Default: 'geodesic'

        Returns:
        --------
        tuple
            (average_distance, key_points, skeleton_image)
            where:
            - average_distance: float (normalized average distance)
            - key_points: ndarray (coordinates [x,y] of the reference points)
            - skeleton_image: ndarray (binary image of the processed skeleton)

        Analyzes methods for distance calculation in chromatids and centromeres.

        1. Geodesic Distance (Most Accurate Method)
            - Calculates the shortest path between two points on a curved surface
            * Application:
            - Considers 4 points from the chromatid and centromere in a convex area
            - Provides more accurate measurement (accounts for curvature)
            * Issues:
            - Sensitive to inaccuracy in the 4 points
            - Especially affected by errors in points distant from the centromere
            
        * NOTE: NOT USED IN THE FINAL VERSION, JUST FOR REFERENCE AND DEVELOPMENT DEBUG
        2. Euclidean Distance (Point-to-Point) with Convex Area
            - Calculates straight-line distance in flat space
            * Application:
            - Measures between 4 points from the chromatid and centromere
            - Considers convex area
            * Issues:
            - Simpler than geodesic
            - Does not account for curvature

        3. Simple Euclidean Distance (Upper/Lower Extremes)
            - Simplified version
            * Application:
            - Uses only:
                * Furthest upper point
                * Furthest lower point
                * Centromere
            * Issues:
            - Useful for quick measurements
            - Less accurate on curved structures

        Problems in Method Combination:
        - Challenge in accurate path reconstruction
        * Proposed Solution:
        - Use of skeletonization
        - Extracts central axis to guide filling
        * Issues Encountered:
        1. Uncertain Filling Direction:
            - Mean can result in shorter path than actual object
            - Difficulty in properly connecting to the edge
        2. Geodesic with Undesired Turns:
            - Due to inaccuracies in end points (Canny + Convex Hull)
            - May not close properly
        3. Error in Extreme Points:
            - Convex Hull selects 4 largest area points
            - Points may not represent real extremities
            - Introduces error in final curvature
    
        Observation:
            By convention, the p arm is expected to lie above the centromere and the q arm below. After this alignment, 
            “at the top of the image is the upper arm; at the bottom, the lower one”
            mdpi.com. In standardized databases, images are pre-oriented so that the short arm lies above the long one.
            arxiv.org.

            References:
            -------
            - Tjio, J. H., & Levan, A. (1960). Standardization of human karyotyping: I. Morphology of the normal chromosomes: Denver conference, April 1960. Hereditas, 46(3-4), 225-237.
            - Barch, M. J., Knutsen, T., & Spurbeck, J. L. (1997). Cytogenetics: Basic Concepts and Clinical Applications. Springer Science & Business Media.
            - Yunis, J. J. (1983). Cytogenetics of Human Chromosomes. Academic Press.
    """
    def __init__(self, skeleton, binary, centromere, logger):
        self.logger = logger
        self.skeleton = skeleton
        self.binary = binary
        self.centromere = centromere
        self.canny_and_convexhull()
        self.upper_chromatid, self.lower_chromatid = self.calculate_chromatids_by_geodesic_distance__()
        #self.upper_chromatid_2, self.lower_chromatid_2 = self.calculate_by_point_to_point_distance()
        self.upper_chromatid_3, self.lower_chromatid_3 = self.calculate_by_simple_distance()
    
    def calculate_final_upper_chromatide(self):
        """
        Calculates the final height of a chromosome based on three different height measurements.
        
        Args:
            size_geodesic (float): Height measured using the geodesic method.
            size_point_to_point (float): Height measured using the point-to-point method.
            size_simple (float): Height measured using the simple method.
        
        Returns:
            float: The final height calculated as a simple average.
        """
        if not self.is_skel_straight():
            return self.upper_chromatid
        return self.upper_chromatid_3
    
    def calculate_final_lower_chromatide(self):
        """
        Calculates the final height of a chromosome based on three different height measurements.
        
        Args:
            size_geodesic (float): Height measured using the geodesic method.
            size_point_to_point (float): Height measured using the point-to-point method.
            size_simple (float): Height measured using the simple method.
        
        Returns:
            float: The final height calculated as a simple average.
        """
        if not self.is_skel_straight():
            return self.lower_chromatid
        return self.lower_chromatid_3

    def calculate_binary_object_area(self):
        """
        Calculates the area of the binary object in the binary image.

        Returns:
            float: Total area of the binary objects in the image.
        """
        # Convert the binary image to boolean format (True for 1, False for 0)
        binary_image = self.binary > 0

        # Label connected regions of the binary image
        labeled_image, num_features = measure.label(binary_image, connectivity=2, return_num=True)

        # Calculate properties of labeled regions
        regions = measure.regionprops(labeled_image)

        # Calculate the total area of all regions
        total_area = sum(region.area for region in regions)

        return total_area
    
    def canny_and_convexhull(self):
        def find_max_area_points(points):
            """
            Find the four points that form the largest convex area along the chromosome.

            Parameters:
            points (np.ndarray): Points along the edges of the chromosome.

            Returns:
            max_area_points (np.ndarray): Four points forming the largest convex area.
            """
            max_area = 0
            max_area_points = None
            
            for combination in combinations(points, 4):
                hull = ConvexHull(combination)
                if hull.volume > max_area:
                    max_area = hull.volume
                    max_area_points = combination
                    
            return np.array(max_area_points)
    
        binary = self.binary > 0
   
        edges = feature.canny(binary, sigma=1)

        if np.count_nonzero(edges) < 3:
            binary_dilated = morphology.binary_dilation(binary, morphology.disk(1))
            edges = feature.canny(binary_dilated, sigma=1)
  
        if np.count_nonzero(edges) < 3:
            edges = morphology.binary_erosion(binary) ^ binary

        edge_points = np.column_stack(np.nonzero(edges))

        hull = ConvexHull(edge_points)
        hull_points = edge_points[hull.vertices]

        self.edges = edges
        self.hull_points = hull_points
        self.farthest_points = find_max_area_points(hull_points)

    def calculate_chromatids_by_geodesic_distance__(self):
        """
        Calcula os comprimentos das cromátides considerando todas as combinações possíveis:
        - 2 braços acima e 2 abaixo (caso ideal)
        - 3 acima e 1 abaixo (ou vice-versa)
        - 4 acima ou 4 abaixo (casos extremos)
        - Outras combinações incompletas
        """
        centromere = self.centromere

        centromere_point = self._find_closest_skeleton_point(centromere)
        self.centromere_point = centromere_point
  
        all_arms = []
        for i, point in enumerate(self.farthest_points):
            length, path = self.calculate_arm_length(centromere_point, point)
            endpoint = point
            relative_pos = 'above' if endpoint[0] < self.centromere_point[1] else 'below'
            all_arms.append({
                'length': length,
                'path': path,
                'position': relative_pos
            })

        arms_above = sorted([a for a in all_arms if a['position'] == 'above'], 
                        key=lambda x: x['length'], reverse=True)
        arms_below = sorted([a for a in all_arms if a['position'] == 'below'], 
                        key=lambda x: x['length'], reverse=True)
     
        self.upper_path = []
        self.lower_path = []
        self.upper_path_2 = []
        self.lower_path_2 = []
      
        if len(arms_above) >= 2 and len(arms_below) >= 2:
            self.upper_path = arms_above[0]['path']
            self.upper_path_2 = arms_above[1]['path']
            self.lower_path = arms_below[0]['path']
            self.lower_path_2 = arms_below[1]['path']
            return arms_above[0]['length'], arms_below[0]['length']
     
        elif len(arms_above) >= 3 and len(arms_below) >= 1:
            self.upper_path = arms_above[0]['path']
            self.upper_path_2 = arms_above[1]['path']
            self.lower_path = arms_below[0]['path']
            return arms_above[0]['length'], arms_below[0]['length']
      
        elif len(arms_above) >= 1 and len(arms_below) >= 3:
            self.upper_path = arms_above[0]['path']
            self.lower_path = arms_below[0]['path']
            self.lower_path_2 = arms_below[1]['path']
            return arms_above[0]['length'], arms_below[0]['length']
     
        elif len(arms_above) == 4 or len(arms_below) == 4:
            arms = arms_above if len(arms_above) == 4 else arms_below
            self.upper_path = arms[0]['path']
            self.lower_path = arms[1]['path']
            self.upper_path_2 = arms[2]['path']
            self.lower_path_2 = arms[3]['path']
            return arms[0]['length'], arms[1]['length']
        
    def calculate_by_point_to_point_distance(self):
        centromere = self.centromere_point

        upper_path = self._calculate_straight_line_path(self.farthest_points[0], centromere)
        lower_path = self._calculate_straight_line_path(self.farthest_points[1], centromere)
        upper_path_2 = self._calculate_straight_line_path(self.farthest_points[2], centromere)
        lower_path_2 = self._calculate_straight_line_path(self.farthest_points[3], centromere)

        upper_chromatid_length = len(upper_path)
        lower_chromatid_length = len(lower_path)
        upper_chromatid_length_2 = len(upper_path_2)
        lower_chromatid_length_2 = len(lower_path_2)

        self.upper_path_point_to_point = upper_path
        self.lower_path_point_to_point = lower_path
        self.upper_path_2_point_to_point = upper_path_2
        self.lower_path_2_point_to_point = lower_path_2

        return max(upper_chromatid_length, upper_chromatid_length_2), max(lower_chromatid_length, lower_chromatid_length_2)
    
    def calculate_by_simple_distance(self):
        centromere = self.centromere
        #centromere = self.centromere_point

        upper_chromatid_length, upper_point = self._superior_chromosomal_chromatide(centromere)
        lower_chromatid_length, lower_point = self._lower_chromosomal_chromatide(centromere)

        upper_path = self._calculate_straight_line_path(upper_point, centromere)
        lower_path = self._calculate_straight_line_path(lower_point, centromere)

        self.upper_point_simple = upper_point
        self.lower_point_simple = lower_point

        self.upper_path_simple= upper_path
        self.lower_path_simple = lower_path
        return len(upper_path), len(lower_path)

    def _find_closest_skeleton_point(self, point):
        skeleton_points = np.column_stack(np.nonzero(self.skeleton))
        distances = np.linalg.norm(skeleton_points - point, axis=1)
        closest_point_index = np.argmin(distances)
        return tuple(skeleton_points[closest_point_index].astype(int))

    def calculate_arm_length(self, centromere_point, end_point):
        """
        Calculate the shortest path length along the skeleton from the nearest skeleton point to the centromere.

        Parameters:
        centromere_point (tuple): Coordinates of the centromere.
        end_point (tuple): Coordinates of the end point.

        Returns:
        arm_length (int): Length of the path.
        path (list): List of points in the path.
        """
        def calculate_path(start_point, end_point):
            """
            Calculate the path from start_point to end_point using the shortest path algorithm.

            Parameters:
            start_point (tuple): Starting point coordinates.
            end_point (tuple): Ending point coordinates.

            Returns:
            path (list): List of points in the path.
            """
            end_point = tuple(end_point)
            queue = deque([start_point])
            visited = set()
            visited.add(tuple(start_point))
            parents = {tuple(start_point): None}

            while queue:
                current_point = queue.popleft()

                if np.array_equal(current_point, end_point):
                    break

                for neighbor in get_neighbors(current_point):
                    if (neighbor not in visited):
                        queue.append(neighbor)
                        visited.add(tuple(neighbor))
                        parents[tuple(neighbor)] = tuple(current_point)

            path = []
            current = end_point
            while current is not None:
                path.append(current)
                current = parents.get(tuple(current))

            return path
        
        def find_nearest_skeleton_point(point):
            skeleton_points = np.column_stack(np.nonzero(self.skeleton))
            distances = np.linalg.norm(skeleton_points - point, axis=1)
            closest_point_index = np.argmin(distances)
            return tuple(skeleton_points[closest_point_index].astype(int))
        
        def get_neighbors(point):
            x, y = point
            neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
            neighbors += [(x-1, y-1), (x+1, y+1), (x-1, y+1), (x+1, y-1)]
            neighbors = [(a, b) for a, b in neighbors if 0 <= a < self.binary.shape[0] and 0 <= b < self.binary.shape[1]]
            return neighbors
        
        skeleton = self.skeleton
        nearest_point = find_nearest_skeleton_point(end_point)

        queue = deque([nearest_point])
        visited = set()
        visited.add(tuple(nearest_point))
        parents = {tuple(nearest_point): None}

        while queue:
            current_point = queue.popleft()

            if np.array_equal(current_point, centromere_point):
                break

            for neighbor in get_neighbors(current_point):
                if (neighbor not in visited) and (skeleton[neighbor] == 1):
                    queue.append(neighbor)
                    visited.add(tuple(neighbor))
                    parents[tuple(neighbor)] = tuple(current_point)

        path_to_centromere = []
        current = centromere_point
        while current is not None:
            path_to_centromere.append(current)
            current = parents.get(tuple(current))

        path_to_nearest = calculate_path(end_point, nearest_point)

        complete_path = path_to_centromere + path_to_nearest
        return len(complete_path), complete_path
    
    def _calculate_straight_line_path(self, start_point, end_point):
        """
        Calculate a straight line path from start_point to end_point.

        Parameters:
        start_point (tuple): Starting point coordinates.
        end_point (tuple): Ending point coordinates.

        Returns:
        path (list): List of points in the path.
        """
        rr, cc = line(int(start_point[0]), int(start_point[1]), int(end_point[0]), int(end_point[1]))
        path = list(zip(rr, cc))
        return path

    def is_skel_straight(self, threshold=5.0):
        """
        Verifica se o esqueleto é predominantemente reto ou curvo.
        
        Parâmetros:
        - skel: array binário (True/False) representando o esqueleto.
        - binary: array binário opcional representando o objeto completo (não usado nesta versão).
        - threshold: limite médio de distância para considerar o esqueleto reto.
        
        Retorna:
        - True se o esqueleto for considerado reto, False caso contrário.
        """
        # Obter as coordenadas dos pontos do esqueleto
        y, x = np.where(self.skeleton)
        points = np.column_stack((x, y))
        
        if len(points) < 2:
            return True  # esqueleto trivial (pouco pontos)
        
        # Encontrar os pontos extremos (mais distantes um do outro)
        # Usamos a distância euclidiana para encontrar o par mais distante
        distances = cdist(points, points)
        max_dist_idx = np.unravel_index(np.argmax(distances), distances.shape)
        p1, p2 = points[max_dist_idx[0]], points[max_dist_idx[1]]
        
        # Equação da linha entre p1 e p2: ax + by + c = 0
        # Calculando os coeficientes a, b, c
        a = p2[1] - p1[1]
        b = p1[0] - p2[0]
        c = p2[0] * p1[1] - p1[0] * p2[1]
        
        # Calcular distâncias de todos os pontos à linha
        denom = np.sqrt(a**2 + b**2)
        if denom == 0:
            return True  # pontos coincidentes, linha degenerada
        
        distances = np.abs(a * points[:,0] + b * points[:,1] + c) / denom
        
        # Verificar se a média das distâncias está abaixo do threshold
        mean_distance = np.mean(distances)
        return mean_distance <= threshold
    
    def measure_ruler_paths(self):
        """
        Define rule measure

        Returns:
        upper_path_final (List): coord lines
        lower_path_final (List): coord lines
        """
        upper_path_final = None
        lower_path_final = None
        centromere_final = None

        if not self.is_skel_straight():
            upper_path_final = self.upper_path
            lower_path_final = self.lower_path
            centromere_final = self.centromere_point
        else:
            upper_path_final = self.upper_path_simple
            lower_path_final = self.lower_path_simple
            centromere_final = self.centromere
    
        return upper_path_final, lower_path_final, centromere_final
    
    def calculate_binary_dimensions(self):
        """
        Args:
            binary_image (np.ndarray):

        Returns:
            tuple: (width, height)
        """
        ys, xs = np.nonzero(self.binary)

        if ys.size == 0 or xs.size == 0:
            return 0, 0

        width = int(xs.max() - xs.min())
        height = int(ys.max() - ys.min())

        return width, height

    def _superior_chromosomal_chromatide(self, point):
        im = self.binary
        flag= False
        for i in range(0, im.shape[0]):
            for j in range(0, im.shape[1]):
                if flag == False:
                    if im[i][j] == 1:
                        x=i
                        y=j
                        flag= True
                        
        d =  sqrt((point[0]-point[1])**2) + ((x-y)**2)
        d= abs(d)
        return d, (x, y)

    def _lower_chromosomal_chromatide(self, point):
        im = self.binary
        for i in range(0, im.shape[0]):
            for j in range(0, im.shape[1]):
                if im[i][j] == 1:
                    x=i
                    y=j
        d =  sqrt((point[0]-point[1])**2) + ((x-y)**2)
        d= abs(d)
        return d, (x, y)

    def chromosome_classify_geodesic(self):
        """
        Classify the chromosome based on the arm ratio (RB).

        Returns:
        classification (float): Chromosome classification.
        """
        upper_chromatid = self.upper_chromatid
        lower_chromatid = self.lower_chromatid

        rb = max(upper_chromatid, lower_chromatid) / min(upper_chromatid, lower_chromatid)

        #self.logger.info('rb geodesic: {0}'.format(rb))
        return self.chromosome_classify(rb), rb
        
    def chromosome_classify_point_to_point(self):
        """
        Classify the chromosome based on the arm ratio (RB).

        Returns:
        classification (str): Chromosome classification.
        """
        upper_chromatid = self.upper_chromatid_2
        lower_chromatid = self.lower_chromatid_2

        rb = max(upper_chromatid, lower_chromatid) / min(upper_chromatid, lower_chromatid)
        
        #self.logger.info('rb point: {0}'.format(rb))
        return self.chromosome_classify(rb), rb

    def chromosome_classify_simple(self):
        '''
            Classify the chromosome based on the arm ratio (RB).

        Returns:
        classification (float): Chromosome classification.
        '''
        upper_chromatid = self.upper_chromatid_3
        lower_chromatid = self.lower_chromatid_3

        rb = max(upper_chromatid, lower_chromatid) / min(upper_chromatid, lower_chromatid)

        #self.logger.info('rb simple: {0}'.format(rb))
        return self.chromosome_classify(rb), rb
    
    def rb_chromosome_default(self, upper, lower):
        '''
            Classify the chromosome based on the arm ratio (RB).

        Returns:
        classification (float): Chromosome classification.
        '''
        rb = max(upper, lower) / min(upper, lower)
        return rb
    
    def chromosome_classify(self, rb):
        '''
            Classify the chromosome based on the arm ratio (RB).

        Returns:
        classification (str): Chromosome classification.
        '''
        if 1 <= rb and rb < 1.71:
            return 'metacentric'
        elif 1.71 <= rb and rb <= 3.0:
            return 'submetacentric'
        elif 3.0 < rb and rb <= 7.0:
            return 'subtelocentric'
        elif rb > 7.0:
            return 'acrocentric'

    def size_chromosome_geodesic(self):
        """
        Calculate the total size of the chromosome.

        Returns:
        size (float): Total size of the chromosome.
        """
        upper_chromatid = self.upper_chromatid
        lower_chromatid = self.lower_chromatid
        size = upper_chromatid + lower_chromatid
        return size
    
    def size_chromosome_point_to_point(self):
        """
        Calculate the total size of the chromosome.

        Returns:
        size (float): Total size of the chromosome.
        """
        upper_chromatid = self.upper_chromatid_2
        lower_chromatid = self.lower_chromatid_2
        size = upper_chromatid + lower_chromatid
        return size
    
    def size_chromosome_simple(self):
        upper_chromatid = self.upper_chromatid_3
        lower_chromatid = self.lower_chromatid_3
        size = upper_chromatid + lower_chromatid
        return size

    def create_overlay_image(self, image):
        """
        Create an overlay image with the paths of the chromatids.

        Parameters:
        image (np.ndarray): Original image.

        Returns:
        overlay_image (np.ndarray): Image with the overlay.
        """
        overlay_image = image.copy()
  
        if overlay_image.shape[2] == 4:
            overlay_image = cv2.cvtColor(overlay_image, cv2.COLOR_BGRA2BGR)

        # Overlay Canny edges
        edges_color = cv2.cvtColor((self.edges * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
        overlay_image = cv2.addWeighted(overlay_image, 0.7, edges_color, 0.3, 0)

        # Overlay ConvexHull points
        for point in self.hull_points:
            cv2.circle(overlay_image, (point[1], point[0]), 1, (0, 255, 255), -1)  # Yellow points

        # Draw paths
        for point in self.upper_path:
            overlay_image[point[0], point[1]] = [255, 0, 0]  # Red

        for point in self.lower_path:
            overlay_image[point[0], point[1]] = [0, 0, 255]  # Blue

        for point in self.upper_path_2:
            overlay_image[point[0], point[1]] = [255, 0, 0]  # Red

        for point in self.lower_path_2:
            overlay_image[point[0], point[1]] = [0, 0, 255]  # Blue

        overlay_image[self.centromere_point[0], self.centromere_point[1]] = [0, 255, 0]  # Green

        return overlay_image
    
    def create_overlay_image_geodesic(self, image):
        """
        Create an overlay image with the paths of the chromatids and the path from the end of the skeleton 
        to the chromatid points.

        Parameters:
        image (np.ndarray): Original image.

        Returns:
        overlay_image (np.ndarray): Image with the overlay.
        """
        overlay_image = image.copy()
        if overlay_image.shape[2] == 4:
            overlay_image = cv2.cvtColor(overlay_image, cv2.COLOR_BGRA2BGR)

        # Overlay skeleton paths in red
        self.draw_path(overlay_image, self.upper_path, [255, 0, 0])  # Red for upper path
        self.draw_path(overlay_image, self.lower_path, [0, 0, 255])  # Blue for lower path
        self.draw_path(overlay_image, self.upper_path_2, [255, 0, 0])  # Red for upper path 2
        self.draw_path(overlay_image, self.lower_path_2, [0, 0, 255])  # Blue for lower path 2

        overlay_image[self.centromere_point[0], self.centromere_point[1]] = [0, 255, 0]  # Green

        # Draw the farthest points
        for point in self.farthest_points:
            cv2.circle(overlay_image, (point[1], point[0]), 1, (0, 255, 255), -1)  # Yellow points for farthest points

        return overlay_image
    
    def create_overlay_image_point_to_point(self, image):
        """
        Create an overlay image with the paths of the chromatids and the path from the end of the skeleton 
        to the chromatid points.

        Parameters:
        image (np.ndarray): Original image.

        Returns:
        overlay_image (np.ndarray): Image with the overlay.
        """
        overlay_image = image.copy()
        if overlay_image.shape[2] == 4:
            overlay_image = cv2.cvtColor(overlay_image, cv2.COLOR_BGRA2BGR)

        # Overlay skeleton paths in red
        self.draw_path(overlay_image, self.upper_path_point_to_point, [255, 0, 0])  # Red for upper path
        self.draw_path(overlay_image, self.lower_path_point_to_point, [0, 0, 255])  # Red for lower path
        self.draw_path(overlay_image, self.upper_path_2_point_to_point, [255, 0, 0])  # Red for upper path 2
        self.draw_path(overlay_image, self.lower_path_2_point_to_point, [0, 0, 255])  # Red for lower path 2

        overlay_image[int(self.centromere_point[0]), int(self.centromere_point[1])] = [0, 255, 0]  # Green

        # Draw the farthest points
        for point in self.farthest_points:
            cv2.circle(overlay_image, (point[1], point[0]), 1, (0, 255, 255), -1)  # Yellow points for farthest points

        return overlay_image
    
    def create_overlay_image_final_paths(self, image):
        """
        Create an overlay image with the paths of the chromatids and the path from the end of the skeleton 
        to the chromatid points.

        Parameters:
        image (np.ndarray): Original image.

        Returns:
        overlay_image (np.ndarray): Image with the overlay.
        """
        overlay_image = image.copy()
        if overlay_image.shape[2] == 4:
            overlay_image = cv2.cvtColor(overlay_image, cv2.COLOR_BGRA2BGR)

        upper_path_final = None
        lower_path_final = None

        if not self.is_skel_straight():
            upper_path_final = self.upper_path
            lower_path_final = self.lower_path
        else:
            upper_path_final = self.upper_path_simple
            lower_path_final = self.lower_path_simple

        # Overlay skeleton paths in red
        self.draw_path_(overlay_image, upper_path_final, [255, 0, 0])  # Red for upper path
        self.draw_path_(overlay_image, lower_path_final, [0, 0, 255])  # Red for lower path

        overlay_image[int(self.centromere[0]), int(self.centromere[1])] = [0, 255, 0]  # Green
        # cv2.circle(overlay_image, (self.upper_path_final[1], self.upper_path_final[0]), 1, (0, 255, 255), -1)  # Yellow points for farthest points
        # cv2.circle(overlay_image, (self.lower_path_final[1], self.lower_path_final[0]), 1, (0, 255, 255), -1)

        return overlay_image

    def create_overlay_image_simple(self, image):
        """
        Create an overlay image with the paths of the chromatids and the path from the end of the skeleton 
        to the chromatid points.

        Parameters:
        image (np.ndarray): Original image.

        Returns:
        overlay_image (np.ndarray): Image with the overlay.
        """
        overlay_image = image.copy()
        if overlay_image.shape[2] == 4:
            overlay_image = cv2.cvtColor(overlay_image, cv2.COLOR_BGRA2BGR)

        # Overlay skeleton paths in red
        self.draw_path(overlay_image, self.upper_path_simple, [255, 0, 0])  # Red for upper path
        self.draw_path(overlay_image, self.lower_path_simple, [0, 0, 255])  # Red for lower path

        overlay_image[int(self.centromere[0]), int(self.centromere[1])] = [0, 255, 0]  # Green
        cv2.circle(overlay_image, (self.upper_point_simple[1], self.upper_point_simple[0]), 1, (0, 255, 255), -1)  # Yellow points for farthest points
        cv2.circle(overlay_image, (self.lower_point_simple[1], self.lower_point_simple[0]), 1, (0, 255, 255), -1)

        return overlay_image

    def draw_path(self, image, path, color):
        """
        Draws a path on the image.

        Parameters:
        image (np.ndarray): Image on which to draw.
        path (list of tuples): Path to draw.
        color (list): Color of the path.
        """
        for point in path:
            image[int(point[0]), int(point[1])] = color

    def draw_path_(self, image, path, color):
        """
        Draw a path on the image with boundary checking
        
        Parameters:
        - image: numpy array (the image to draw on)
        - path: list of (y,x) tuples
        - color: [R,G,B] values
        """
        h, w = image.shape[:2]  # Get image dimensions
        
        for point in path:
            y, x = int(point[0]), int(point[1])
            # Check if coordinates are within bounds
            if 0 <= y < h and 0 <= x < w:
                image[y, x] = color
