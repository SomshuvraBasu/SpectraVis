import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import json
from utils.FCC import create_rgb_image
from utils.analyseSAM import compare_pixel_to_library

class SAMComparisonTool:
    def __init__(self, image_data, metadata, library_path='data/spectral_library.json'):
        """
        Initialize the SAM Comparison Tool.
        
        Parameters:
        image_data (ndarray): Hyperspectral image data cube
        metadata (dict): Metadata containing wavelength information
        library_path (str): Path to the spectral library JSON.
        """
        self.image_data = image_data
        self.metadata = metadata
        self.library_path = library_path
        
        # Load library
        self.library = self.load_library()
        
        # Create main figure with subplots for image and comparison plot
        self.fig = plt.figure(figsize=(12, 6))
        self.fig.suptitle('SAM Comparison Tool', fontsize=16)
        self.fig.canvas.manager.set_window_title('Spectral Library')

        # Subplot 1: RGB image
        self.ax1 = self.fig.add_subplot(121)
        self.rgb_image = create_rgb_image(image_data)
        self.ax1.imshow(self.rgb_image)
        self.ax1.set_title("Click on the RGB image to select a pixel")

        # Subplot 2: Comparison plot
        self.ax2 = self.fig.add_subplot(122)
        self.ax2.set_title("SAM Comparison")
        self.ax2.set_xlabel("Library Entry")
        self.ax2.set_ylabel("SAM Score (radians)")

        # # Create submit button
        # self.submit_ax = plt.axes([0.85, 0.02, 0.1, 0.05])  # Button position
        # self.submit_button = Button(self.submit_ax, 'Submit')

        # # Connect events
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        # self.submit_button.on_clicked(self.on_submit)

        # Storage for selected pixel
        self.selected_pixel = None

    def load_library(self):
        """
        Load the spectral library from file or return an empty dictionary.
        """
        if self.library_path and os.path.exists(self.library_path):
            with open(self.library_path, 'r') as f:
                return json.load(f)
        return {}

    def on_click(self, event):
        """
        Handle pixel selection on the RGB image.
        """
        if event.inaxes == self.ax1:
            # Get pixel coordinates
            row, col = int(event.ydata), int(event.xdata)
            self.selected_pixel = (row, col)
            
            # Highlight selected pixel
            self.ax1.clear()
            self.ax1.imshow(self.rgb_image)
            self.ax1.scatter(col, row, color='red', s=100)
            self.ax1.set_title(f"Selected Pixel: ({row}, {col})")
            
            # Perform comparison and update plot
            self.update_comparison_plot()

    def update_comparison_plot(self):
        """
        Update the SAM comparison plot for the selected pixel.
        """
        if not self.selected_pixel:
            print("No pixel selected.")
            return

        # Perform SAM comparison
        row, col = self.selected_pixel
        sam_scores = compare_pixel_to_library(self.image_data, self.metadata, self.selected_pixel, self.library_path)
        
        labels = list(sam_scores.keys())
        scores = [entry['sam_score'] for entry in sam_scores.values()]

        sam_high_confidence = 0.03
        sam_low_confidence = 0.1

        # Color bars based on confidence
        colors = ['green' if score <= sam_high_confidence else
                  'yellow' if score <= sam_low_confidence else
                  'grey' for score in scores]

        # Update the plot
        self.ax2.clear()
        bars = self.ax2.bar(labels, scores, color=colors)
        self.ax2.set_title(f"SAM Scores for Pixel ({row}, {col})")
        self.ax2.set_xlabel("Library Entry")
        self.ax2.set_ylabel("SAM Score (radians)")
        self.ax2.set_xticks(range(len(labels)))
        self.ax2.set_xticklabels(labels, rotation=45, ha='right')
        self.ax2.axhline(y=sam_high_confidence, color='blue', linestyle='--')
        self.ax2.text(len(sam_scores) - 1, sam_high_confidence, "High Confidence", color='blue', ha='right')
        self.ax2.axhline(y=sam_low_confidence, color='orange', linestyle='--')
        self.ax2.text(len(sam_scores) - 1, sam_low_confidence, "Low Confidence", color='orange', ha='right')

        # Annotate best match
        best_match = None
        for label, score in zip(labels, scores):
            if score <= sam_high_confidence:
                best_match = (label, score, "High Confidence")
                break
            elif score <= sam_low_confidence:
                best_match = (label, score, "Low Confidence")

        if best_match:
            label, score, confidence = best_match
            self.ax2.text(1, max(scores) * 0.9, f"Best Match: {label} ({confidence})\nSAM Score: {score:.4f}",
                          color='black', ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        else:
            self.ax2.text(1, max(scores) * 0.9, "No confident match found", color='red', ha='center',
                          fontsize=10, bbox=dict(facecolor='white', alpha=0.7))

        plt.draw()

    # def on_submit(self, event):
    #     """
    #     Handle submit button click.
    #     """
    #     if self.selected_pixel:
    #         print(f"Pixel {self.selected_pixel} processed.")
    #     else:
    #         print("No pixel selected.")

# Example usage
if __name__ == "__main__":
    # Load the hyperspectral data cube and metadata
    image_data = np.load('data/Salinas_corrected.npy')
    with open('data/metadata.json', 'r') as f:
        metadata = json.load(f)

    # Create the SAM comparison tool
    tool = SAMComparisonTool(image_data, metadata, library_path='data/spectral_library.json')
    plt.show()
