# main.py
import numpy as np
import matplotlib.pyplot as plt
import json
from utils.FCC import create_rgb_image
from utils.canvasHandler import CanvasHandler  # Import the CanvasHandler class

# Load the hyperspectral data cube
image_data = np.load('data/Salinas_corrected.npy')

# Load the metadata
with open('data/metadata.json', 'r') as f:
    metadata = json.load(f)

max_pixels = 5

# Create the RGB image from the hyperspectral data
rgb_image = create_rgb_image(image_data)

# Create the figure and axis
fig, ax = plt.subplots(figsize=(12, 6))
fig.canvas.manager.set_window_title('Spectral Analysis Tool')

# Display the RGB image
ax.imshow(rgb_image)
ax.set_title(f"Click on the FCC image to select up to {max_pixels} pixels")

# Initialize the CanvasHandler to manage clicks and submit
canvas_handler = CanvasHandler(fig, ax, rgb_image, image_data, metadata, max_pixels=5)

# Show the plot
plt.show()
