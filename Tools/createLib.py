import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
from ..utils.FCC import create_rgb_image
from ..utils.pixelSpectrum import get_pixel_spectrum
from ..utils.spectralLib import save_entry_to_library, view_library

class SpectralLibraryCreationTool:
    def __init__(self, image_data, metadata, library_path='data/spectral_library.json'):
        """
        Initialize the Spectral Library Creation Tool with improved interactions
        """
        self.image_data = image_data
        self.metadata = metadata
        self.library_path = library_path

        # Create figure with tight layout to accommodate widgets
        self.figure, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(15, 6))
        self.figure.suptitle('Spectral Library Creation Tool', fontsize=16)

        # RGB Image
        self.rgb_image = create_rgb_image(image_data)
        self.ax1.imshow(self.rgb_image)
        self.ax1.set_title("Click on pixels to add to spectral library")

        # Spectrum Plot
        self.ax2.set_title("Pixel Spectrum")
        self.ax2.set_xlabel("Wavelength (nm)")
        self.ax2.set_ylabel("Radiance (DN)")

        # Reset state variables
        self.reset_state()

        # Add interactive elements
        self.setup_interactive_elements()

        plt.tight_layout(rect=[0, 0.1, 1, 0.9])
        self.figure.canvas.mpl_connect('button_press_event', self.on_click)

    def reset_state(self):
        """Reset tracking variables for library entry"""
        self.current_label = ""
        self.current_pixel_data = None
        self.current_wavelengths = None
        self.selected_pixel = None

    def setup_interactive_elements(self):
        """Create input widgets with explicit focus and key event handling"""
        # Label input
        self.label_ax = plt.axes([0.2, 0.02, 0.2, 0.05])
        self.label_textbox = TextBox(self.label_ax, 'Entry Label: ')
        self.label_textbox.on_submit(self.on_label_submit)

        # Save button
        self.save_ax = plt.axes([0.5, 0.02, 0.1, 0.05])
        self.save_button = Button(self.save_ax, 'Save Entry')
        self.save_button.on_clicked(self.save_entry)

        # View library button
        self.view_ax = plt.axes([0.65, 0.02, 0.1, 0.05])
        self.view_button = Button(self.view_ax, 'View Library')
        self.view_button.on_clicked(self.display_library)

    def on_click(self, event):
        """Enhanced pixel selection handling"""
        if event.inaxes == self.ax1:
            # Ensure click is within image bounds
            row, col = int(event.ydata), int(event.xdata)
            height, width = self.rgb_image.shape[:2]
            
            if 0 <= row < height and 0 <= col < width:
                self.selected_pixel = (row, col)

                # Clear previous highlights
                self.ax1.clear()
                self.ax1.imshow(self.rgb_image)
                self.ax1.scatter(col, row, color='red', s=100)
                self.ax1.set_title(f"Selected Pixel: ({row}, {col})")

                # Extract and plot pixel spectrum
                wavelengths, pixel_data = get_pixel_spectrum(
                    self.image_data,
                    self.metadata,
                    self.selected_pixel
                )

                self.current_wavelengths = wavelengths
                self.current_pixel_data = pixel_data

                self.ax2.clear()
                self.ax2.plot(wavelengths, pixel_data)
                self.ax2.set_title("Pixel Spectrum")
                self.ax2.set_xlabel("Wavelength (nm)")
                self.ax2.set_ylabel("Radiance (DN)")

                plt.draw()

    def on_label_submit(self, label):
        """Handle label input"""
        self.current_label = label.strip()
        print(f"Label set: {self.current_label}")

    def save_entry(self, event=None):
        """Robust save mechanism with error checking"""
        if not self.current_label:
            plt.msgbox("Please enter a label!")
            return

        if (self.current_pixel_data is None or 
            self.current_wavelengths is None or 
            self.selected_pixel is None):
            plt.msgbox("Please select a pixel first!")
            return

        try:
            save_entry_to_library(
                self.library_path,
                self.current_label,
                self.current_wavelengths,
                self.current_pixel_data
            )
            plt.msgbox(f"Saved entry: {self.current_label}")
            self.reset_state()
        except Exception as e:
            plt.msgbox(f"Error saving entry: {str(e)}")

    def display_library(self, event=None):
        """Enhanced library display with error handling"""
        try:
            library = view_library(self.library_path)
            
            lib_fig, lib_ax = plt.subplots(figsize=(10, 6))
            lib_fig.suptitle('Spectral Library Entries', fontsize=16)
            lib_fig.canvas.manager.set_window_title('Spectral Library')

            for label, entry in library.items():
                wavelengths = list(map(int, entry['spectrum'].keys()))
                pixel_data = list(entry['spectrum'].values())

                lib_ax.plot(wavelengths, pixel_data, label=label)

            lib_ax.set_xlabel("Wavelength (nm)")
            lib_ax.set_ylabel("Radiance (DN)")
            lib_ax.legend()
            plt.tight_layout()
            plt.show()
        except Exception as e:
            plt.msgbox(f"Error displaying library: {str(e)}")

    def get_figure(self):
        """Return the main figure"""
        return self.figure

# Example usage script remains the same
def main():
    # Load the hyperspectral data cube
    image_data = np.load('data/Salinas_corrected.npy')
    library_path = 'data/spectral_library.json'

    # Load the metadata
    with open('data/metadata.json', 'r') as f:
        metadata = json.load(f)

    # Create and run the library creation tool
    library_tool = SpectralLibraryCreationTool(image_data, metadata, library_path)
    plt.show()


if __name__ == "__main__":
    main()