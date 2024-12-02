import sys
import os
import numpy as np
import json
from PyQt5.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QFileDialog, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from spectralToolsQT import SpectralAnalysisTool

class DataInputWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        
        # Image Data Input
        self.image_label = QLabel("Hyperspectral Image: Not Selected")
        self.image_button = QPushButton("Select Hyperspectral Image (.npy)")
        self.image_button.clicked.connect(self.select_image)
        
        # Metadata Input
        self.metadata_label = QLabel("Metadata: Not Selected")
        self.metadata_button = QPushButton("Select Metadata (.json)")
        self.metadata_button.clicked.connect(self.select_metadata)

        # Spectral Library Input
        self.spectral_library_label = QLabel("Spectral Library: Not Selected")
        self.spectral_library_button = QPushButton("Select Spectral Library (.json)")
        self.spectral_library_button.clicked.connect(self.select_spectral_library)
        
        # Add widgets to layout
        layout.addWidget(QLabel("<b>Data Input</b>"))
        layout.addWidget(self.image_label)
        layout.addWidget(self.image_button)
        layout.addWidget(self.metadata_label)
        layout.addWidget(self.metadata_button)
        layout.addWidget(self.spectral_library_label)
        layout.addWidget(self.spectral_library_button)
        
        self.setLayout(layout)
        
        # Data storage
        self.image_data = None
        self.metadata = None
        self.spectral_library = None
    
    def select_image(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Hyperspectral Image", 
                                                  "", "NumPy Files (*.npy)")
        if filepath:
            try:
                self.image_data = np.load(filepath)
                self.image_label.setText(f"Image: {os.path.basename(filepath)}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not load image: {str(e)}")
    
    def select_metadata(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Metadata", 
                                                  "", "JSON Files (*.json)")
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    self.metadata = json.load(f)
                self.metadata_label.setText(f"Metadata: {os.path.basename(filepath)}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not load metadata: {str(e)}")

    def select_spectral_library(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Spectral Library", 
                                                  "", "JSON Files (*.json)")
        if filepath:
            try:
                self.spectral_library = filepath
                self.spectral_library_label.setText(f"Spectral Library: {os.path.basename(filepath)}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not load spectral library: {str(e)}")

class HyperspectralAnalysisTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SpectraVis - Hyperspectral Analysis Tool")
        self.setGeometry(100, 100, 300, 300)
        
        # Main widget
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Data Input Widget
        self.data_input_widget = DataInputWidget()
        main_layout.addWidget(self.data_input_widget)
        
        # Run Analysis Button
        self.run_analysis_button = QPushButton("Run Spectral Analysis")
        self.run_analysis_button.clicked.connect(self.run_analysis)
        main_layout.addWidget(self.run_analysis_button)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def run_analysis(self):
        # Validate data
        if (self.data_input_widget.image_data is None or 
            self.data_input_widget.metadata is None):
            QMessageBox.warning(self, "Error", "Please select hyperspectral image and metadata first")
            return

        if self.data_input_widget.spectral_library is None:
            QMessageBox.warning(self, "Warning", "Defaulting to preset spectral library")
            #use a default library path, if it doesn't exist, create it
            if not os.path.exists('data/spectral_library.json'):
                with open('data/spectral_library.json', 'w') as f:
                    f.write('{}')
            self.data_input_widget.spectral_library = 'data/spectral_library.json'

        
        # Open Spectral Analysis Tool
        self.spectral_tool = SpectralAnalysisTool(
            self.data_input_widget.image_data, 
            self.data_input_widget.metadata,
            self.data_input_widget.spectral_library
        )
        self.spectral_tool.show()

def main():
    app = QApplication(sys.argv)
    main_window = HyperspectralAnalysisTool()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()