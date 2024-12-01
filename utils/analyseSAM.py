import numpy as np
import matplotlib.pyplot as plt
import json
from utils.pixelSpectrum import get_pixel_spectrum

def calculate_sam_score(spectrum1, spectrum2):
    """
    Calculate the Spectral Angle Mapper (SAM) score between two spectra.
    
    Parameters:
    spectrum1 (ndarray): First pixel's spectral data
    spectrum2 (ndarray): Second pixel's spectral data
    
    Returns:
    float: SAM score in radians (0 = identical, π/2 = orthogonal)
    """
    # Normalize the spectra 
    norm1 = spectrum1 / np.linalg.norm(spectrum1)
    norm2 = spectrum2 / np.linalg.norm(spectrum2)
    
    # Calculate the spectral angle (dot product)
    sam_score = np.arccos(np.clip(np.dot(norm1, norm2), -1.0, 1.0))
    
    return sam_score

def compare_pixel_to_library(image_data, metadata, pixel, library_path='data/spectral_library.json'):
    """
    Compare a pixel's spectrum to a spectral library.
    
    Parameters:
    image_data (ndarray): Hyperspectral image data cube
    metadata (dict): Metadata containing wavelength information
    pixel (tuple): Pixel coordinates (row, col)
    library_path (str): Path to the spectral library JSON
    
    Returns:
    dict: SAM scores and library entry details
    """
    # Load the library from the JSON file
    with open(library_path, 'r') as f:
        library = json.load(f)

    # Get the pixel's spectrum
    wavelengths, pixel_spectrum = get_pixel_spectrum(image_data, metadata, pixel)

    # Convert the pixel spectrum to a dictionary for easier matching
    pixel_spectrum_dict = dict(zip(wavelengths, pixel_spectrum))

    # Calculate SAM scores
    sam_scores = {}
    for label, entry in library.items():
        # Extract the library's spectrum as a dictionary
        lib_spectrum_dict = entry['spectrum']

        #convert botht he dictionary keys to int
        lib_spectrum_dict = {int(k):v for k,v in lib_spectrum_dict.items()}
        pixel_spectrum_dict = {int(k):v for k,v in pixel_spectrum_dict.items()}

        # Ensure that the wavelengths are the same between the pixel and library spectrum
        common_wavelengths = set(pixel_spectrum_dict.keys()).intersection(lib_spectrum_dict.keys())
        
        if len(common_wavelengths) == 0:
            continue  # Skip if no common wavelengths

        # Create common wavelength arrays for both pixel and library spectra
        common_wavelengths = sorted(common_wavelengths)  # Sorting ensures consistency
        pixel_common_values = np.array([pixel_spectrum_dict[w] for w in common_wavelengths])
        lib_common_values = np.array([lib_spectrum_dict[w] for w in common_wavelengths])

        # Calculate SAM score using common wavelengths
        sam_score = calculate_sam_score(pixel_common_values, lib_common_values)
        
        # Store the SAM score and the pixel coordinates from the library
        sam_scores[label] = {
            'sam_score': float(sam_score),
            'pixel_coords': entry.get('pixel_coords', None)  # Use None if not available
        }

    # Sort scores from lowest to highest
    sorted_scores = dict(sorted(sam_scores.items(), key=lambda x: x[1]['sam_score']))

    return sorted_scores