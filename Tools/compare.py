import numpy as np
import os
import matplotlib.pyplot as plt
import json
from ..utils.FCC import create_rgb_image
from ..utils.analyseSAM import compare_pixel_to_library

class SAMComparisonTool:
    def __init__(self, image_data, metadata, library_path='data/spectral_library.json'):
        """
        Initialize the SAM Comparison Tool with robust pixel selection
        """
        self.image_data = image_data
        self.metadata = metadata
        self.library_path = library_path
        
        # Load library
        self.library = self.load_library()
        
        # Create figure with better layout
        self.figure, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(15, 6))
        self.figure.suptitle('SAM Comparison Tool', fontsize=16)

        # RGB Image
        self.rgb_image = create_rgb_image(image_data)
        self.ax1.imshow(self.rgb_image)
        self.ax1.set_title("Click on RGB image to select a pixel")

        # Comparison Plot
        self.ax2.set_title("SAM Comparison")
        self.ax2.set_xlabel("Library Entry")
        self.ax2.set_ylabel("SAM Score (radians)")

        # State tracking
        self.selected_pixel = None

        # Event connection
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        self.figure.canvas.mpl_connect('button_press_event', self.on_click)

    def load_library(self):
        """
        Load the spectral library from file or return an empty dictionary
        with robust error handling
        """
        try:
            if self.library_path and os.path.exists(self.library_path):
                with open(self.library_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading library: {e}")
        return {}

    def on_click(self, event):
        """
        Enhanced pixel selection with comprehensive bounds checking
        """
        if event.inaxes == self.ax1:
            # Validate click coordinates
            row, col = int(event.ydata), int(event.xdata)
            height, width = self.rgb_image.shape[:2]
            
            if 0 <= row < height and 0 <= col < width:
                self.selected_pixel = (row, col)

                # Clear and redraw with highlight
                self.ax1.clear()
                self.ax1.imshow(self.rgb_image)
                self.ax1.scatter(col, row, color='red', s=100)
                self.ax1.set_title(f"Selected Pixel: ({row}, {col})")

                # Update comparison plot
                self.update_comparison_plot()
                
                plt.draw()

    def update_comparison_plot(self):
        """
        Comprehensive SAM score comparison
        """
        if not self.selected_pixel:
            print("No pixel selected.")
            return

        # Safety checks before SAM comparison
        if not self.library:
            plt.msgbox("No spectral library available!")
            return

        row, col = self.selected_pixel
        
        try:
            # Perform SAM comparison
            sam_scores = compare_pixel_to_library(
                self.image_data, 
                self.metadata, 
                self.selected_pixel, 
                self.library_path
            )
            
            # Safety check for comparison results
            if not sam_scores:
                plt.msgbox("No SAM comparisons possible!")
                return

            labels = list(sam_scores.keys())
            scores = [entry['sam_score'] for entry in sam_scores.values()]

            sam_high_confidence = 0.03
            sam_low_confidence = 0.1

            # Deterministic color mapping
            colors = [
                'green' if score <= sam_high_confidence else
                'yellow' if score <= sam_low_confidence else 
                'grey' for score in scores
            ]

            # Clear previous plot
            self.ax2.clear()
            bars = self.ax2.bar(labels, scores, color=colors)
            self.ax2.set_title(f"SAM Scores for Pixel ({row}, {col})")
            self.ax2.set_xlabel("Library Entry")
            self.ax2.set_ylabel("SAM Score (radians)")
            self.ax2.set_xticklabels(labels, rotation=45, ha='right')
            
            # Confidence lines
            self.ax2.axhline(y=sam_high_confidence, color='blue', linestyle='--')
            self.ax2.text(len(sam_scores) - 1, sam_high_confidence, "High Confidence", color='blue', ha='right')
            
            self.ax2.axhline(y=sam_low_confidence, color='orange', linestyle='--')
            self.ax2.text(len(sam_scores) - 1, sam_low_confidence, "Low Confidence", color='orange', ha='right')

        except Exception as e:
            print(f"Error in SAM comparison: {e}")
            plt.msgbox(f"Comparison error: {e}")

    def get_figure(self):
        """Return the main figure"""
        return self.figure

# Example usage
if __name__ == "__main__":
    # Load the hyperspectral data cube and metadata
    image_data = np.load('data/Salinas_corrected.npy')
    with open('data/metadata.json', 'r') as f:
        metadata = json.load(f)

    # Create the SAM comparison tool
    tool = SAMComparisonTool(image_data, metadata, library_path='data/spectral_library.json')
    plt.show()