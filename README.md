
# Spectral Analysis Tool for Hyperspectral Data Cubes

## Overview
This tool enables the visualization and analysis of hyperspectral data cubes by allowing users to interactively select points on a False Color Composite (FCC) image. Once the points are selected, the corresponding spectra are plotted for easy inspection, saving to library and to compare with other spectrums.

## Features
### 1. Spectral Visualization
The spectral visualization module enables comprehensive exploration of pixel spectra within a Hyperspectral Data Cube. This feature allows:
- Detailed visual comparison of spectral signatures
- Interactive examination of individual pixel spectral characteristics
- Intuitive representation of spectral information across multiple bands

### 2. Spectral Library Creation
A robust spectral library management system that:
- Generates libraries of high-quality, preprocessed spectral signatures
- Ensures data integrity through quality assurance processes
- Provides a comprehensive reference database for spectral analysis
- Supports easy storage and retrieval of known spectral signatures

### 3. Spectral Comparison
Advanced spectral matching capabilities utilizing the Spectral Angle Mapper (SAM) algorithm:
- Computes spectral similarity between target pixels and reference spectra
- Treats spectra as vectors in n-dimensional spectral space
- Calculates the spectral angle between compared spectra
- Provides quantitative similarity measurements
- Supports identification and classification of spectral signatures

## Spectral Angle Mapper (SAM) Methodology
The Spectral Angle Mapper (SAM) is a geometrical method for spectral matching that:
- Compares the angle between the reference spectrum and target spectrum
- Treats spectra as vectors in n-dimensional space
- Provides a measure of spectral similarity independent of illumination effects

### SAM Calculation
- **Input**: Two spectra as n-dimensional vectors
- **Computation**: Calculates the spectral angle between the vectors
- **Output**: Angle value representing spectral similarity

## How It Works
1. Load your hyperspectral data cube and metadata file.
2. View the FCC image of the hyperspectral cube.
3. Click on the image to select pixels.
4. Click the **Submit** button to display the radiance spectra for the selected pixels.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/SomshuvraBasu/SpectraVis.git
   ```
2. Navigate into the repository directory:
   ```bash
   cd SpectraVis
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
   
## Usage
Run the tool with the following command:
```bash
python app.py
```

## Demo


https://github.com/user-attachments/assets/210b7631-2536-48d5-be09-99a483d33b6f


## File Structure
- `app.py`: Entry point of the application.
- `spectralToolsQT.py`: Contains the main implementation classes for the application.
- `utils/`: Contains helper scripts for image generation and plotting.
  - `analyseSAM.py`: Compares Spectrums using Spectral Angle Mapper (SAM).
  - `FCC.py`: Generates the FCC image from the hyperspectral cube.
  - `pixelSpectrum.py`: Extracts the Spectral Data.
  - `imageSpectrum.py`: Handles spectra plotting for selected pixels.
  - `canvasHandler.py`: Handles the user interface canvas.
  - `spectralLib.py`: Loads the spectral library.
- `Tools/` : Contains the scripts for individual tools
  - `visualise.py`: Visualising the hyperspectral data cube.
  - `createLib.py` : Create a spectral library from the data cube.
  - `compare.py`: Compares Spectrums using Spectral Angle Mapper (SAM).
- `data/`: Contains the hyperspectral data cube and metadata files.


## Requirements
- Python 3.8+
- NumPy
- Matplotlib
- PyQt
