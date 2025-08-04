class ChromosomeCalculator:
    def __init__(self, fov_micrometers, image_width_pixels):
        """
        Constructor to initialize the ChromosomeCalculator class.

        Args:
        - fov_micrometers (float): Field of View in micrometers.
        - image_width_pixels (int): Width of the captured image in pixels.
        """
        self.fov_micrometers = float(fov_micrometers)
        self.image_width_pixels = float(image_width_pixels)

    def calculate_pixel_size(self):
        """
        Calculate the size of a pixel in micrometers.

        Returns:
        - pixel_size_micrometers (float): Size of a pixel in micrometers.
        """
        pixel_size_micrometers = self.fov_micrometers / self.image_width_pixels
        return pixel_size_micrometers

    def calculate_chromosome_size(self, pixel_size_micrometers, chromosome_size_pixels):
        """
        Calculate the size of a chromosome in micrometers.

        Args:
        - pixel_size_micrometers (float): Size of a pixel in micrometers.
        - chromosome_size_pixels (float): Size of the chromosome in pixels.

        Returns:
        - chromosome_size_micrometers (float): Size of the chromosome in micrometers.
        """
        chromosome_size_micrometers = pixel_size_micrometers * chromosome_size_pixels
        return chromosome_size_micrometers

    def calculate_base_pairs(self, chromosome_size_micrometers, base_pair_density):
        """
        Calculate the number of base pairs in a chromosome.

        Args:
        - chromosome_size_micrometers (float): Size of the chromosome in micrometers.
        - base_pair_density (float): Density of base pairs per micrometer.

        Returns:
        - base_pairs_count (float): Number of base pairs in the chromosome.
        """
        base_pairs_count = chromosome_size_micrometers * float(base_pair_density)
        return base_pairs_count
