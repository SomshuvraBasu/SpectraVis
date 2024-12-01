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

        print(pixel_common_values, lib_common_values)

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

def plot_library_comparison(image_data, metadata, pixel, library_path='data/spectral_library.json'):
    """
    Plot SAM scores comparison between a pixel and library entries.
    
    Parameters:
    image_data (ndarray): Hyperspectral image data cube
    metadata (dict): Metadata containing wavelength information
    pixel (tuple): Pixel coordinates (row, col)
    library_path (str): Path to the spectral library JSON
    """
    # Get comparison results
    sam_scores = compare_pixel_to_library(image_data, metadata, pixel, library_path)
    
    # Prepare data for plotting
    labels = list(sam_scores.keys())
    scores = [entry['sam_score'] for entry in sam_scores.values()]

    sam_high_confidence = 0.03
    sam_low_confidence = 0.1
    
    # Color bars based on the score
    colors = []
    for score in scores:
        if score <= sam_high_confidence:
            colors.append('green')  # High confidence (lower SAM score)
        elif score > sam_high_confidence and score < sam_low_confidence:
            colors.append('yellow')  # Low confidence (higher SAM score)
        else:
            colors.append('grey')  # Borderline confidence
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, scores, color=colors)
    plt.title(f"SAM Scores for Pixel {pixel}")
    plt.xlabel("Library Entry")
    plt.ylabel("SAM Score (radians)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Annotate bars with exact scores
    for i, (label, entry) in enumerate(sam_scores.items()):
        plt.text(i, entry['sam_score'], 
                 f"{entry['sam_score']:.4f}", 
                 ha='center', va='bottom')

    # Annotate threshold
    plt.axhline(y=sam_high_confidence, color='blue', linestyle='--')
    plt.text(len(sam_scores) - 1, sam_high_confidence, "High Confidence", color='blue', ha='right')
    plt.axhline(y=sam_low_confidence, color='orange', linestyle='--')
    plt.text(len(sam_scores) - 1, sam_low_confidence, "Low Confidence", color='orange', ha='right')

    #annotate the plot to display which library entry is the best match which should be atleast less than sam_low_confidence and if possible less than sam_high_confidence
    best_match = None
    for label, entry in sam_scores.items():
        if entry['sam_score'] <= sam_low_confidence:
            best_match = label
            confidence = 'Low Confidence'
            if entry['sam_score'] <= sam_high_confidence:
                best_match = label
                confidence = 'High Confidence'
            else:
                continue
        else:
            continue
    if best_match:
        plt.text(0, 0.6, f"Best Match: {best_match} ({confidence})", color='black', ha='left')
    else:
        plt.text(0, 0.6, "No confident match found", color='black', ha='left')

    # Show the plot
    plt.show()

    return sam_scores