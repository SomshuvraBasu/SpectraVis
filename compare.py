import numpy as np
import matplotlib.pyplot as plt
import json
from utils.FCC import create_rgb_image
from utils.analyseSAM import plot_library_comparison

# Load the hyperspectral data cube
image_data = np.load('data/Salinas_corrected.npy')

# Load the metadata
with open('data/metadata.json', 'r') as f:
    metadata = json.load(f)

# Create the RGB image from the hyperspectral data
rgb_image = create_rgb_image(image_data)

# Create the figure and axis
fig, ax = plt.subplots(figsize=(12, 6))
fig.canvas.manager.set_window_title('Spectral Library Comparison Tool')

# Display the RGB image
ax.imshow(rgb_image)
ax.set_title("Click on a pixel to compare its spectrum with the library")

# Global variable to store the selected pixel
selected_pixel = None

def on_click(event):
    global selected_pixel
    if event.inaxes == ax:
        # Get the x, y coordinates of the click (row, col)
        row, col = int(event.ydata), int(event.xdata)
        selected_pixel = (row, col)
        
        # Close the current figure
        plt.close(fig)
        
        # Run library comparison
        plot_library_comparison(image_data, metadata, selected_pixel)

# Connect the click event
fig.canvas.mpl_connect('button_press_event', on_click)

# Show the plot
plt.show()