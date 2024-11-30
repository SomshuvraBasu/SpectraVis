
def get_pixel_spectrum(image_data, metadata, pixel_no):
    spectral_dimension = image_data.shape[2]
    pixel_data = image_data[pixel_no[0], pixel_no[1], :]
    assert len(pixel_data) == spectral_dimension, (
        f"Pixel spectral data does not match the spectral dimension: "
        f"expected {spectral_dimension}, got {len(pixel_data)}"
    )
    wavelengths = [metadata["band_to_wavelength"][str(band)][1] for band in range(1, spectral_dimension+1)]
    return wavelengths, pixel_data
