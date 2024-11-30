import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from utils.imageSpectrum import plot_rgb_and_spectrum

class CanvasHandler:
    def __init__(self, fig, ax, rgb_image, image_data, metadata, max_pixels=5):
        self.fig = fig
        self.ax = ax
        self.rgb_image = rgb_image
        self.image_data = image_data
        self.metadata = metadata
        self.max_pixels = max_pixels
        self.selected_pixels = []

        # Connect the event handler
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        # Create and connect the submit button
        self.create_submit_button()

    def on_click(self, event):
        """
        Handle mouse click events to select pixels from the image.
        """
        if len(self.selected_pixels) < self.max_pixels and event.inaxes == self.ax:
            # Get the x, y coordinates of the click (row, col)
            row, col = int(event.ydata), int(event.xdata)
            self.selected_pixels.append((row, col))
            print(f"Pixel selected: ({row}, {col})")

            self.update_image()

    def create_submit_button(self):
        """
        Create and connect the submit button that processes the selected pixels.
        """
        # Adjust position and size of the button to ensure it's visible
        ax_submit = plt.axes([0.8, 0.01, 0.15, 0.075])  # Position of the button (x, y, width, height)
        self.submit_button = Button(ax_submit, 'Submit')  # Save as an attribute to retain reference
        
        # Explicitly redraw canvas after button creation
        # Button may not work immediately due to deferred event handling in Matplotlib, where the callback is not fully registered until the next draw cycle.
  
        self.fig.canvas.draw_idle()

        # Connect the button to the on_submit callback
        self.submit_button.on_clicked(self.on_submit)

    def on_submit(self, event):
        """
        Handles the submit action once the user selects up to the maximum number of pixels.
        """
        if len(self.selected_pixels) <= self.max_pixels:
            print("Submit button clicked!")
            self.fig.canvas.mpl_disconnect(self.cid)  # Disconnect the click event
            plt.close()
            print("Proceeding with the spectra plot...")
            plot_rgb_and_spectrum(self.rgb_image, self.image_data, self.metadata, self.selected_pixels)
        else:
            print(f"Maximum number of pixels ({self.max_pixels}) exceeded!")

    def update_image(self):
        """
        Update the image and replot the selected pixels.
        """
        self.ax.clear()  # Clear the previous scatter points and image
        self.ax.imshow(self.rgb_image)  # Replot the image

        # Plot the selected pixels as a marker on the image
        for (r, c) in self.selected_pixels:
            self.ax.scatter(c, r, color='red', label=f"Pixel ({r}, {c})")
        
        self.ax.set_title(f"Click on the FCC image to select up to {self.max_pixels} pixels")
        plt.draw()  # Redraw the plot
