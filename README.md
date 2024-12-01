
# Spectral Analysis Tool for Hyperspectral Data Cubes

## Overview
This tool enables the visualization and analysis of hyperspectral data cubes by allowing users to interactively select points on a False Color Composite (FCC) image. Once the points are selected, the corresponding spectra are plotted for easy inspection.

## Features
- Interactive selection of pixels on the FCC image.
- Visualization of the radiance spectra for selected points.
- Easy-to-use interface with multiple pixel selections at a time.
- Seamless integration with hyperspectral data in `.npy` format.

## How It Works
1. Load your hyperspectral data cube and metadata file.
2. View the FCC image of the hyperspectral cube.
3. Click on the image to select pixels.
4. Click the **Submit** button to display the radiance spectra for the selected pixels.

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/SomshuvraBasu/SpectraVis.git
   ```
2. Place your hyperspectral data cube and metadata file in the `data/` directory.

## Usage
Run the tool with the following command:
```bash
python visualise.py
```

## Demo

https://github.com/user-attachments/assets/72ed3d63-f2b9-496f-ae93-210535fcb0b4


## File Structure
- `visualise.py`: Entry point of the application.
- `utils/`: Contains helper scripts for image generation and plotting.
  - `FCC.py`: Generates the FCC image from the hyperspectral cube.
  - `pixelSpectrum.py`: Extracts the Spectral Data.
  - `imageSpectrum.py`: Handles spectra plotting for selected pixels.
  - `canvasHandler.py`: Handles the user interface canvas.
- `data/`: Contains the hyperspectral data cube and metadata files.

## Requirements
- Python 3.8+
- NumPy
- Matplotlib
