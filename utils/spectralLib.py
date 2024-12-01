import json
import os
import numpy as np


def load_library(library_path):
    """
    Load existing spectral library from the given path or create a new one.
    
    Parameters:
    library_path (str): Path to the spectral library JSON file
    
    Returns:
    dict: Loaded spectral library
    """
    if os.path.exists(library_path):
        with open(library_path, 'r') as f:
            return json.load(f)
    return {}


def save_entry_to_library(library_path, label, wavelengths, pixel_data):
    """
    Save a pixel spectrum entry to the spectral library.

    Parameters:
    library_path (str): Path to the spectral library JSON file
    label (str): Label for the library entry
    wavelengths (list): List of wavelengths
    pixel_data (list): Corresponding radiance data
    """
    # Load existing library
    library = load_library(library_path)
    
    # Create library entry
    entry = {
        "label": label,
        "spectrum": dict(zip([int(w) for w in wavelengths], [int(p) for p in pixel_data]))
    }
    
    # Add to library
    library[label] = entry
    
    # Save updated library
    with open(library_path, 'w') as f:
        json.dump(library, f, indent=4)

    print(f"Saved entry: {label}")


def view_library(library_path):
    """
    Load and return the spectral library for visualization.
    
    Parameters:
    library_path (str): Path to the spectral library JSON file
    
    Returns:
    dict: Spectral library data
    """
    return load_library(library_path)
