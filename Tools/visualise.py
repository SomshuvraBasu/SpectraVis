# visualise.py
import numpy as np
import matplotlib.pyplot as plt
import json
from ..utils.FCC import create_rgb_image
from ..utils.canvasHandler import CanvasHandler

class SpectralVisualizationTool:
    def __init__(self, image_data, metadata, max_pixels=10):
        # Create the figure and axis
        self.figure, self.ax = plt.subplots(figsize=(12, 6))
        self.figure.canvas.manager.set_window_title('Spectral Analysis Tool')

        # Create the RGB image from the hyperspectral data
        self.rgb_image = create_rgb_image(image_data)

        # Display the RGB image
        self.ax.imshow(self.rgb_image)
        self.ax.set_title(f"Click on the FCC image to select up to {max_pixels} pixels")

        # Initialize the CanvasHandler to manage clicks and submit
        self.canvas_handler = CanvasHandler(self.figure, self.ax, self.rgb_image, image_data, metadata, max_pixels)

    def get_figure(self):
        """
        Return the main figure
        """
        return self.figure

# Example usage script
def main():
    # Load the hyperspectral data cube
    image_data = np.load('data/Salinas_corrected.npy')

    # Load the metadata
    with open('data/metadata.json', 'r') as f:
        metadata = json.load(f)

    # Create visualization tool
    visualization_tool = SpectralVisualizationTool(image_data, metadata)
    plt.show()

if __name__ == "__main__":
    main()