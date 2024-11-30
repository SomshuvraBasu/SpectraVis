import numpy as np

def create_rgb_image(image_data):
    # Adjust the indices to match the visible spectrum
    red_band = image_data[:, :, 32]  # Example index for red
    green_band = image_data[:, :, 15]  # Example index for green
    blue_band = image_data[:, :, 6]  # Example index for blue

    # Stack bands to create an RGB image
    rgb_image = np.stack((red_band, green_band, blue_band), axis=-1)

    # Normalize to [0, 1] for visualization
    rgb_image = (rgb_image - np.min(rgb_image)) / (np.max(rgb_image) - np.min(rgb_image))

    return rgb_image
