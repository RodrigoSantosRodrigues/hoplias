"""
Trask, B. J. (2002). Nature Reviews Genetics: Descreve como a densidade de DNA em cromossomos é utilizada para análises moleculares.
Scherf, M., et al. (1997). Cytometry: Explica métodos de análise de imagens para medir características cromossômicas.
Manuelidis, L. (1990). Chromosome Lengths and Structural DNA Sequences: Relação entre tamanho e densidade do DNA.
"""

import numpy as np

def calculate_base_pairs(length, width, species="human", centromere_position=None):
    """
    Estimate the number of base pairs in a chromosome.

    Parameters:
        length (float): Chromosome length in micrometers.
        width (float): Average width of the chromosome in micrometers.
        species (str): The species for density estimation. Default is "human".
        centromere_position (float): Position of the centromere as a proportion (0 to 1).

    Returns:
        dict: Estimated base pairs and chromosomal classification.

        # Example usage
        length = 5.2  # in micrometers
        width = 1.0   # in micrometers
        centromere_position = 0.3
        result = calculate_base_pairs(length, width, species="human", centromere_position=centromere_position)
        print(result)

    """
    # Densities in Mb/μm (millions of base pairs per micrometer)
    densities = {
        "human": 6.4,
        "mouse": 6.0,
        "zebrafish": 4.5,
        "fly": 1.2,
    }

    # Get density based on species
    density = densities.get(species.lower(), 6.4)  # Default to human if species unknown

    # Calculate base pairs
    base_pairs = length * density * 1e6  # Convert Mb to base pairs

    # Classify chromosome type based on centromere position
    if centromere_position is not None:
        if centromere_position < 0.25:
            classification = "telocentric"
        elif centromere_position < 0.4:
            classification = "acrocentric"
        elif centromere_position < 0.75:
            classification = "submetacentric"
        else:
            classification = "metacentric"
    else:
        classification = "unknown"

    return {
        "base_pairs": int(base_pairs),
        "classification": classification,
        "species": species,
    }
