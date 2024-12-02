import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from utils.pixelSpectrum import get_pixel_spectrum

class CanvasHandler:
    def __init__(self, fig, ax1, ax2, rgb_image, image_data, metadata, max_pixels=5):
        self.fig = fig
        self.ax1 = ax1  # RGB Image axis
        self.ax2 = ax2  # Spectrum axis
        self.rgb_image = rgb_image
        self.image_data = image_data
        self.metadata = metadata
        self.max_pixels = max_pixels
        self.selected_pixels = []
        self.selected_pixel_data = []

        # Connect the event handler
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        # Initial image display
        self.ax1.imshow(self.rgb_image)
        self.ax1.set_title(f"Click on image to select up to {self.max_pixels} pixels")
        self.ax2.set_title("Pixel Spectrum")
        self.ax2.set_xlabel("Wavelength (nm)")
        self.ax2.set_ylabel("Radiance (DN)")

    def on_click(self, event):
        """
        Handle mouse click events to select pixels from the image.
        """
        if len(self.selected_pixels) < self.max_pixels and event.inaxes == self.ax1:
            # Get the x, y coordinates of the click (row, col)
            row, col = int(event.ydata), int(event.xdata)
            self.selected_pixels.append((row, col))

            # Update RGB image with selected pixels
            self.update_image()

            # Get and plot pixel spectrum
            wavelengths, pixel_data = get_pixel_spectrum(
                self.image_data, 
                self.metadata, 
                (row, col)
            )
            self.selected_pixel_data.append((wavelengths, pixel_data))
            
            # Plot all selected pixel spectra
            self.plot_spectra()

    def plot_spectra(self):
        """
        Plot spectra for all selected pixels with pixel coordinates in the legend.
        """
        self.ax2.clear()
        self.ax2.set_title("Pixel Spectrum")
        self.ax2.set_xlabel("Wavelength (nm)")
        self.ax2.set_ylabel("Radiance (DN)")

        for (row, col), (wavelengths, pixel_data) in zip(self.selected_pixels, self.selected_pixel_data):
            self.ax2.plot(wavelengths, pixel_data, label=f"Pixel ({row}, {col})")
        
        if self.selected_pixel_data:
            # Add legend with pixel coordinates
            self.ax2.legend(loc='best')
        
        self.fig.canvas.draw_idle()

    def update_image(self):
        """
        Update the image and replot the selected pixels.
        """
        self.ax1.clear()  # Clear the previous scatter points and image
        self.ax1.imshow(self.rgb_image)  # Replot the image

        # Plot the selected pixels as a marker on the image
        for (r, c) in self.selected_pixels:
            self.ax1.scatter(c, r, color='red', label=f"Pixel ({r}, {c})")
        
        self.ax1.set_title(f"Click on the FCC image to select up to {self.max_pixels} pixels")
        self.fig.canvas.draw_idle()  # Redraw the plot

    def reset(self):
        """
        Reset the pixel selection and clear the plots.
        """
        self.selected_pixels = []
        self.selected_pixel_data = []
        
        # Reset RGB image
        self.ax1.clear()
        self.ax1.imshow(self.rgb_image)
        self.ax1.set_title(f"Click on the FCC image to select up to {self.max_pixels} pixels")
        
        # Reset spectrum plot
        self.ax2.clear()
        self.ax2.set_title("Pixel Spectrum")
        self.ax2.set_xlabel("Wavelength (nm)")
        self.ax2.set_ylabel("Radiance (DN)")
        
        self.fig.canvas.draw_idle()

    def clear_spectrum_plot(self):
        """
        Clear the spectrum plot.
        """
        self.ax2.clear()
        self.ax2.set_title("Pixel Spectrum")
        self.ax2.set_xlabel("Wavelength (nm)")
        self.ax2.set_ylabel("Radiance (DN)")
        self.fig.canvas.draw_idle()