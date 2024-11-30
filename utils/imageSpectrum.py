import matplotlib.pyplot as plt
from utils.pixelSpectrum import get_pixel_spectrum

def plot_rgb_and_spectrum(rgb_image, image_data, metadata, pixel_coords):
    """
    Plots the RGB image with pixel markers and their corresponding radiance spectra.
    
    Parameters:
        rgb_image (ndarray): The RGB image for visualization.
        image_data (ndarray): The hyperspectral image data (H x W x Bands).
        metadata (dict): Metadata containing wavelength information.
        pixel_coords (list of tuples): List of pixel coordinates (row, col) to plot.
    """
    # Create subplots
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    fig.canvas.manager.set_window_title('Spectral Analysis Tool')
    
    # Plot the RGB image
    axs[0].imshow(rgb_image)
    for i, (row, col) in enumerate(pixel_coords):
        axs[0].scatter(col, row, label=f"Pixel ({row}, {col})")
    axs[0].legend()
    axs[0].set_title("FCC Image with Pixel Markers")
    
    # Plot the radiance spectrum
    for row, col in pixel_coords:
        wavelengths, pixel_data = get_pixel_spectrum(image_data, metadata, (row, col))
        axs[1].plot(wavelengths, pixel_data, label=f"Pixel ({row}, {col})")
    
    axs[1].set_xlabel("Wavelength (nm)")
    axs[1].set_ylabel("Radiance (DN)")
    axs[1].set_title("Radiance Spectrum of Pixels")
    axs[1].legend()
    
    # Layout adjustment and show
    plt.tight_layout()
    plt.show()