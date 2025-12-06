# StereoDepth Engine: Monocular 3D Reconstruction

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Transform ordinary stereo photos into dense 3D point clouds — no calibration required.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [How It Works](#-how-it-works) • [Configuration](#%EF%B8%8F-configuration)

</div>

---

## 🎯 Overview

**StereoDepth Engine** is a complete computer vision pipeline that generates dense depth maps and 3D point clouds from uncalibrated stereo image pairs. Simply take two photos from slightly different positions (like shifting your phone a few centimeters) and let the algorithm reconstruct the 3D structure of your scene.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📐 **Automatic Rectification** | Uses SIFT feature matching + Fundamental Matrix estimation to align uncalibrated handheld images |
| 🖼️ **Dense Disparity Mapping** | Implements Semi-Global Block Matching (SGBM) for robust pixel-level correspondence |
| 🔧 **WLS Filtering** | Applies Weighted Least Squares smoothing to preserve edges while reducing noise |
| 🌐 **3D Point Cloud Export** | Generates colored `.ply` files viewable in MeshLab, CloudCompare, or Blender |
| ⚡ **Configurable Pipeline** | Easily tune camera parameters and algorithm settings for your specific hardware |

---

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/deevinandu/StereoDepth-Monocular-3DReconstruction.git
cd StereoDepth-Monocular-3DReconstruction

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
- `numpy` — Numerical computing
- `opencv-python` — Core image processing
- `opencv-contrib-python` — SIFT, WLS filter, and extra modules
- `matplotlib` — Visualization

---

## 🚀 Usage

### Basic Command

```bash
python main.py --left <path/to/left.jpg> --right <path/to/right.jpg> --out <output.ply>
```

### Example

```bash
python main.py --left inputs/left.jpg --right inputs/right.jpg --out my_scene.ply
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--left` | ✅ | Path to the left stereo image |
| `--right` | ✅ | Path to the right stereo image |
| `--out` | ❌ | Output filename (default: `output.ply`) |

### How To Capture Stereo Pairs

1. **Horizontal shift only** — Move your camera 5-10 cm to the right between shots (no rotation)
2. **Same settings** — Keep focus, exposure, and zoom identical
3. **Static scenes** — Moving objects will cause artifacts
4. **Good lighting** — More texture = better feature matching

---

## 🔬 How It Works

### Pipeline Overview

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────┐
│  Load Stereo │────▶│   Epipolar      │────▶│    SGBM         │────▶│   Depth     │
│    Images    │     │  Rectification  │     │  Disparity      │     │ Calculation │
└─────────────┘     └─────────────────┘     └─────────────────┘     └──────┬──────┘
                                                                           │
                                                                           ▼
                                                                   ┌─────────────┐
                                                                   │  3D Point   │
                                                                   │ Cloud (.ply)│
                                                                   └─────────────┘
```

### 1. Epipolar Rectification

Since handheld photos are rarely perfectly aligned, we compute the **Fundamental Matrix** from SIFT feature correspondences. Both images are warped so that corresponding points lie on the same horizontal scanlines.

```
Uncalibrated Input → SIFT Matching → Fundamental Matrix → Homography Warping → Aligned Output
```

### 2. Disparity Estimation

We use **Semi-Global Block Matching (SGBM)** to compute pixel-level disparities:

$$\text{Disparity} = x_{\text{left}} - x_{\text{right}}$$

A **WLS (Weighted Least Squares) filter** is applied to smooth the disparity map while preserving sharp object edges.

### 3. Depth Calculation

Depth is recovered via stereo triangulation:

$$Z = \frac{f \cdot B}{d}$$

Where:
- **f** = Focal length in pixels
- **B** = Baseline distance between camera positions
- **d** = Disparity value

---

## ⚙️ Configuration

Edit `src/config.py` to match your camera hardware:

```python
# Camera Intrinsic Parameters
FOCAL_LENGTH_MM = 4.76        # Lens focal length
SENSOR_WIDTH_MM = 6.40        # Physical sensor width
BASELINE_CM = 5.0             # Distance between left/right shots

# Processing Parameters
TARGET_WIDTH = 1000           # Resize width (affects speed)
SGBM_NUM_DISPARITIES = 160    # Max disparity range (multiple of 16)
SGBM_BLOCK_SIZE = 5           # Matching block size (odd number)
```

> You can find your phone's focal length and sensor size in the EXIF data of your photos or on [GSMArena](https://www.gsmarena.com/).

---

## 📁 Project Structure

```
StereoDepth-Monocular-3DReconstruction/
├── main.py              # Entry point
├── requirements.txt     # Python dependencies
├── inputs/              # Stereo images 
└── src/
    ├── config.py        # Camera & algorithm parameters
    ├── core.py          # StereoPipeline class (rectification, SGBM, depth)
    └── utils.py         # Image I/O, visualization, PLY export
```

---

## 📊 Output Visualization

Running the pipeline generates:
1. **Interactive matplotlib plots** showing:
   - Rectified left image
   - Disparity map (WLS filtered)
   - Depth map with colorbar (in cm)
2. **PLY point cloud file** for 3D viewing

### Viewing Point Clouds
- [**MeshLab**](https://www.meshlab.net/) — Free, cross-platform
- [**CloudCompare**](https://www.cloudcompare.org/) — Advanced point cloud processing
- [**Blender**](https://www.blender.org/) — Import via PLY importer add-on

---

## 🔗 Related Projects

**If you want to process your point cloud further** Check out my ground segmentation project:

👉 [**UAV-3D-PointCloud-Ground-Segmentation-RANSAC**](https://github.com/deevinandu/UAV-3D-PointCloud-Ground-Segmentation-RANSAC)

Use RANSAC plane fitting to separate ground surfaces from objects in your point cloud — perfect for robotics and autonomous vehicle applications.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs via Issues
- 💡 Suggest features
- 🔧 Submit pull requests

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

</div>