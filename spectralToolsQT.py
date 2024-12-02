import sys
import numpy as np
import json
import os
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QMessageBox, QDialog, QSpinBox,
                             QTabWidget, QMainWindow, QApplication)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from utils.FCC import create_rgb_image
from utils.pixelSpectrum import get_pixel_spectrum
from utils.analyseSAM import compare_pixel_to_library
from utils.spectralLib import save_entry_to_library, view_library
from utils.canvasHandler import CanvasHandler


class SpectralVisualizationWidget(QWidget):
    def __init__(self, image_data, metadata, max_pixels=10):
        super().__init__()
        self.image_data = image_data
        self.metadata = metadata
        self.max_pixels = max_pixels
        
        # State tracking
        self.selected_pixels = []
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Matplotlib figure with two subplots side by side
        self.figure, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(16, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # RGB Image setup (left subplot)
        self.rgb_image = create_rgb_image(self.image_data)
        self.ax1.imshow(self.rgb_image)
        self.ax1.set_title(f"Click on the image to select up to {self.max_pixels} pixels")
        
        # Spectrum plot setup (right subplot)
        self.ax2.set_title("Pixel Spectrum")
        self.ax2.set_xlabel("Wavelength (nm)")
        self.ax2.set_ylabel("Radiance (DN)")
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Max pixels input
        pixels_label = QLabel("Max Pixels:")
        self.max_pixels_input = QSpinBox()
        self.max_pixels_input.setRange(1, 20)
        self.max_pixels_input.setValue(self.max_pixels)
        self.max_pixels_input.valueChanged.connect(self.update_max_pixels)
        
        controls_layout.addWidget(pixels_label)
        controls_layout.addWidget(self.max_pixels_input)
        
        # Reset button
        reset_button = QPushButton("Reset Selection")
        reset_button.clicked.connect(self.reset_selection)
        controls_layout.addWidget(reset_button)
        
        # Undo button
        undo_button = QPushButton("Undo")
        undo_button.clicked.connect(self.undo_last_selection)
        controls_layout.addWidget(undo_button)
        
        layout.addLayout(controls_layout)
        self.setLayout(layout)
        
        # Custom matplotlib navigation toolbar
        toolbar = NavigationToolbar2QT(self.canvas, self)
        layout.addWidget(toolbar)
        
        # Connect click event
        self.canvas_handler = CanvasHandler(
            self.figure, 
            self.ax1,  # Pass RGB image subplot 
            self.ax2,  # Pass spectrum subplot
            self.rgb_image, 
            self.image_data, 
            self.metadata, 
            self.max_pixels
        )
        self.canvas.mpl_connect('button_press_event', self.canvas_handler.on_click)

    # Update these methods to work with two-subplot layout
    def update_max_pixels(self, value):
        """Update the maximum number of pixels that can be selected"""
        self.max_pixels = value
        self.canvas_handler.max_pixels = value
        self.ax1.set_title(f"Click on the image to select up to {self.max_pixels} pixels")
        self.canvas.draw()

    def reset_selection(self):
        """Reset the pixel selection and clear the plot"""
        self.canvas_handler.reset()
        self.canvas.draw()

    def undo_last_selection(self):
        """
        Undo the last pixel selection.
        """
        self.canvas_handler.undo_last_selection()
        self.canvas.draw()

class SpectralLibraryCreationWidget(QWidget):
    def __init__(self, image_data, metadata, library_path):
        super().__init__()
        self.image_data = image_data
        self.metadata = metadata
        self.library_path = library_path
        
        # State tracking
        self.current_label = ""
        self.current_pixel_data = None
        self.current_wavelengths = None
        self.selected_pixel = None
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Matplotlib figure
        self.figure, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # RGB Image setup
        self.rgb_image = create_rgb_image(self.image_data)
        self.ax1.imshow(self.rgb_image)
        self.ax1.set_title("Click on pixels to add to spectral library")
        
        # Spectrum setup
        self.ax2.set_title("Pixel Spectrum")
        self.ax2.set_xlabel("Wavelength (nm)")
        self.ax2.set_ylabel("Radiance (DN)")
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Label input
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Enter library entry label")
        controls_layout.addWidget(QLabel("Label:"))
        controls_layout.addWidget(self.label_input)
        
        # Save button
        save_button = QPushButton("Save Entry")
        save_button.clicked.connect(self.save_entry)
        controls_layout.addWidget(save_button)
        
        # View Library button
        view_library_button = QPushButton("View Library")
        view_library_button.clicked.connect(self.display_library)
        controls_layout.addWidget(view_library_button)
        
        layout.addLayout(controls_layout)
        self.setLayout(layout)
        
        # Connect click event
        self.canvas.mpl_connect('button_press_event', self.on_click)
    
    def on_click(self, event):
        if event.inaxes == self.ax1:
            row, col = int(event.ydata), int(event.xdata)
            self.selected_pixel = (row, col)
            
            self.ax1.clear()
            self.ax1.imshow(self.rgb_image)
            self.ax1.scatter(col, row, color='red', s=100)
            self.ax1.set_title(f"Selected Pixel: ({row}, {col})")
            
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
            
            self.canvas.draw()
    
    def save_entry(self):
        label = self.label_input.text().strip()
        
        if not label:
            QMessageBox.warning(self, "Error", "Please enter a label!")
            return
        
        if (self.current_pixel_data is None or 
            self.current_wavelengths is None or 
            self.selected_pixel is None):
            QMessageBox.warning(self, "Error", "Please select a pixel first!")
            return
        
        try:
            save_entry_to_library(
                self.library_path,
                label,
                self.current_wavelengths,
                self.current_pixel_data
            )
            QMessageBox.information(self, "Success", f"Saved entry: {label}")
            self.label_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save entry: {str(e)}")
    
    def display_library(self):
        try:
            library = view_library(self.library_path)
            
            # Create a new dialog to display library
            dialog = QDialog(self)
            dialog.setWindowTitle("Spectral Library")
            layout = QVBoxLayout()
            
            # Create matplotlib figure in dialog
            lib_fig, lib_ax = plt.subplots(figsize=(10, 6))
            lib_canvas = FigureCanvas(lib_fig)
            layout.addWidget(lib_canvas)
            
            for label, entry in library.items():
                wavelengths = list(map(int, entry['spectrum'].keys()))
                pixel_data = list(entry['spectrum'].values())
                lib_ax.plot(wavelengths, pixel_data, label=label)
            
            lib_ax.set_xlabel("Wavelength (nm)")
            lib_ax.set_ylabel("Radiance (DN)")
            lib_ax.legend()
            
            dialog.setLayout(layout)
            dialog.resize(800, 600)
            dialog.exec_()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not display library: {str(e)}")

class SAMComparisonWidget(QWidget):
    def __init__(self, image_data, metadata, library_path):
        super().__init__()
        self.image_data = image_data
        self.metadata = metadata
        self.library_path = library_path
        
        # State tracking
        self.selected_pixel = None
        
        # Load library
        self.library = self._load_library()
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Matplotlib figure
        self.figure, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # RGB Image setup
        self.rgb_image = create_rgb_image(self.image_data)
        self.ax1.imshow(self.rgb_image)
        self.ax1.set_title("Click on RGB image to select a pixel")
        
        # SAM Comparison Plot setup
        self.ax2.set_title("SAM Comparison")
        self.ax2.set_xlabel("Library Entry")
        self.ax2.set_ylabel("SAM Score (radians)")
        
        self.setLayout(layout)
        
        # Connect click event
        self.canvas.mpl_connect('button_press_event', self.on_click)
    
    def _load_library(self):
        try:
            if os.path.exists(self.library_path):
                with open(self.library_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load library: {str(e)}")
        return {}
    
    def on_click(self, event):
        if event.inaxes == self.ax1:
            row, col = int(event.ydata), int(event.xdata)
            self.selected_pixel = (row, col)
            
            self.ax1.clear()
            self.ax1.imshow(self.rgb_image)
            self.ax1.scatter(col, row, color='red', s=100)
            self.ax1.set_title(f"Selected Pixel: ({row}, {col})")
            
            self.update_comparison_plot()
            
            self.canvas.draw()
    
    def update_comparison_plot(self):
        if not self.selected_pixel or not self.library:
            QMessageBox.warning(self, "Error", "No pixel or library data available!")
            return
        
        try:
            sam_scores = compare_pixel_to_library(
                self.image_data, 
                self.metadata, 
                self.selected_pixel, 
                self.library_path
            )
            
            labels = list(sam_scores.keys())
            scores = [entry['sam_score'] for entry in sam_scores.values()]
            
            # Confidence thresholds
            sam_high_confidence = 0.03
            sam_low_confidence = 0.1
            
            colors = [
                'green' if score <= sam_high_confidence else
                'yellow' if score <= sam_low_confidence else 
                'grey' for score in scores
            ]
            
            self.ax2.clear()
            self.ax2.bar(labels, scores, color=colors)
            self.ax2.set_title(f"SAM Scores for Selected Pixel")
            self.ax2.set_xlabel("Library Entry")
            self.ax2.set_ylabel("SAM Score (radians)")
            self.ax2.set_xticklabels(labels, rotation=45, ha='right')
            
            # Confidence lines
            self.ax2.axhline(y=sam_high_confidence, color='blue', linestyle='--')
            self.ax2.text(len(sam_scores) - 1, sam_high_confidence, "High Confidence", color='blue', ha='right')
            
            self.ax2.axhline(y=sam_low_confidence, color='orange', linestyle='--')
            self.ax2.text(len(sam_scores) - 1, sam_low_confidence, "Low Confidence", color='orange', ha='right')
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"SAM comparison failed: {str(e)}")

class SpectralAnalysisTool(QMainWindow):
    def __init__(self, image_data, metadata, spectral_library):
        super().__init__()
        self.image_data = image_data
        self.metadata = metadata
        self.spectral_library = spectral_library
        
        self.setWindowTitle("Spectral Analysis Toolbox")
        self.resize(1200, 800)
        
        # Create central widget and tab system
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        self.central_widget.setLayout(main_layout)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.visualization_tab = SpectralVisualizationWidget(self.image_data, self.metadata)
        self.library_tab = SpectralLibraryCreationWidget(self.image_data, self.metadata, self.spectral_library)
        self.sam_tab = SAMComparisonWidget(self.image_data, self.metadata, self.spectral_library)
        
        # Add tabs
        self.tabs.addTab(self.visualization_tab, "Spectral Visualization")
        self.tabs.addTab(self.library_tab, "Spectral Library Creation")
        self.tabs.addTab(self.sam_tab, "SAM Comparison")

def main():
    # Load the hyperspectral data cube
    image_data = np.load('data/Salinas_corrected.npy')

    # Load the metadata
    with open('data/metadata.json', 'r') as f:
        metadata = json.load(f)

    # Load the spectral library
    spectral_library = 'data/spectral_library.json'

    # Create application
    app = QApplication(sys.argv)
    
    # Create and show main window
    main_window = SpectralAnalysisTool(image_data, metadata, spectral_library)
    main_window.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()        