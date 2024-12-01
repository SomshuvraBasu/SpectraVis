import numpy as np
import matplotlib.pyplot as plt
import json
import os
from matplotlib.widgets import Button, TextBox
from FCC import create_rgb_image
from pixelSpectrum import get_pixel_spectrum

class SpectralLibraryCreationTool:
    def __init__(self, image_data, metadata, library_path='data/spectral_library.json'):
        """
        Initialize the Spectral Library Creation Tool
        
        Parameters:
        image_data (ndarray): Hyperspectral image data cube
        metadata (dict): Metadata about the image
        library_path (str): Path to save the spectral library
        """
        self.image_data = image_data
        self.metadata = metadata
        self.library_path = library_path
        
        # Load existing library or create new one
        self.library = self.load_library()
        
        # Create the main figure with 2 columns for RGB image and spectrum plot
        self.fig = plt.figure(figsize=(12, 6))
        self.fig.suptitle('Spectral Library Creation Tool', fontsize=16)
        
        # Create RGB image for left column (column 1)
        self.ax1 = self.fig.add_subplot(121)
        self.rgb_image = create_rgb_image(image_data)
        self.ax1.imshow(self.rgb_image)
        self.ax1.set_title("Click on pixels to add to spectral library")
        
        # Placeholder for spectrum plot in right column (column 2)
        self.ax2 = self.fig.add_subplot(122)
        self.ax2.set_title("Pixel Spectrum")
        self.ax2.set_xlabel("Wavelength (nm)")
        self.ax2.set_ylabel("Radiance (DN)")
        self.ax2.set_xlim([0, 1000])  # Adjust this based on actual wavelength range

        # Create input text box for label
        self.label_ax = plt.axes([0.25, 0.02, 0.15, 0.05]) # x, y, width, height
        self.label_textbox = TextBox(self.label_ax, 'Entry Label')
        
        # Create buttons
        self.save_ax = plt.axes([0.65, 0.02, 0.1, 0.05])
        self.save_button = Button(self.save_ax, 'Save Entry')
        
        self.view_ax = plt.axes([0.76, 0.02, 0.1, 0.05])
        self.view_button = Button(self.view_ax, 'View Library')

        plt.subplots_adjust(bottom=0.17) 
        self.fig.canvas.manager.set_window_title('Spectral Library Tool')

        # Connect events
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.label_textbox.on_submit(self.on_label_submit)
        self.save_button.on_clicked(self.save_entry)
        self.view_button.on_clicked(self.view_library)
        
        # Temporary storage for current entry
        self.current_label = None
        self.current_pixel_data = None
        self.current_wavelengths = None

    def load_library(self):
        """
        Load existing library or return empty dict.
        
        Returns:
        dict: Spectral library
        """
        if os.path.exists(self.library_path):
            with open(self.library_path, 'r') as f:
                return json.load(f)
        return {}

    def on_click(self, event):
        """
        Handle pixel selection on the image
        """
        if event.inaxes == self.ax1:
            # Get pixel coordinates
            row, col = int(event.ydata), int(event.xdata)
            self.selected_pixel = (row, col)
            
            # Extract pixel spectrum
            wavelengths, pixel_data = get_pixel_spectrum(
                self.image_data, 
                self.metadata, 
                self.selected_pixel
            )
            
            # Store for potential saving
            self.current_wavelengths = wavelengths
            self.current_pixel_data = pixel_data
            
            # Highlight selected pixel on the RGB image
            self.ax1.clear()
            self.ax1.imshow(self.rgb_image)
            self.ax1.scatter(col, row, color='red', s=100)
            self.ax1.set_title(f"Selected Pixel: ({row}, {col})")
            
            # Update spectrum plot
            self.ax2.clear()
            self.ax2.plot(wavelengths, pixel_data)
            self.ax2.set_title("Pixel Spectrum")
            self.ax2.set_xlabel("Wavelength (nm)")
            self.ax2.set_ylabel("Radiance (DN)")
            
            plt.draw()

    def on_label_submit(self, label):
        """
        Handle label submission
        """
        self.current_label = label
        print(f"Label set: {label}")

    def save_entry(self, event):
        """
        Save the current pixel spectrum to the library
        """
        if not all([self.current_label, 
                    self.current_pixel_data is not None, 
                    self.current_wavelengths is not None]):
            print("Please select a pixel and provide a label first!")
            return

        # convert current wavelength and pixel data to int
        self.current_wavelengths = [int(w) for w in self.current_wavelengths]
        self.current_pixel_data = [int(p) for p in self.current_pixel_data]
        
        # Create library entry
        entry = {
            "label": self.current_label,
            # dictionary of (wavelength, pixel_data) pairs
            'spectrum': dict(zip(self.current_wavelengths, self.current_pixel_data)),            
        }
        
        # Add to library
        self.library[self.current_label] = entry
        
        # Save to file
        with open(self.library_path, 'w') as f:
            json.dump(self.library, f, indent=4)
        
        print(f"Saved entry: {self.current_label}")
        
        # Reset for next entry
        self.current_label = None
        self.current_pixel_data = None
        self.current_wavelengths = None

    def view_library(self, event):
        """
        View existing library entries
        """
        # Close existing library figure if it exists
        if 'Spectral Library' in plt.get_figlabels():
            plt.close('Spectral Library')

        # Create a new figure to show library entries
        lib_fig, lib_ax = plt.subplots(figsize=(10, 6), label='Spectral Library')

        lib_fig.suptitle('Spectral Library Entries', fontsize=16)
        lib_fig.canvas.manager.set_window_title('Spectral Library')
        
        # List entries
        entries = list(self.library.keys())
        for i, label in enumerate(entries):
            entry = self.library[label]
            lib_ax.plot(
                list(entry['spectrum'].keys()),
                list(entry['spectrum'].values()),
                label=f"{label}"
            )
        
        lib_ax.set_xlabel("Wavelength (nm)")
        lib_ax.set_ylabel("Radiance (DN)")
        lib_ax.legend()
        
        plt.tight_layout()
        plt.show()

# Example usage script
def main():
    # Load the hyperspectral data cube
    image_data = np.load('../data/Salinas_corrected.npy')
    library_path = '../data/spectral_library.json'

    # Load the metadata
    with open('../data/metadata.json', 'r') as f:
        metadata = json.load(f)

    # Create and run the library creation tool
    library_tool = SpectralLibraryCreationTool(image_data, metadata, library_path)
    plt.show()

if __name__ == "__main__":
    main()