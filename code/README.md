# Camera Simulation & Calibration Toolkit

A modular Python package for **screen-based camera calibration**, **pendulum dynamics simulation**, and **synthetic image generation** with optional noise models.

---

## Features

- **Display modeling**:
  - Convert pixel <-> physical mm
  - Generate calibration patterns (checkerboards)
- **Camera modeling**:
  - Intrinsics (K) and Brown–Conrady distortion model
  - OpenCV-based calibration workflow
- **Pendulum dynamics**:
  - Spherical pendulum ODE simulation (damping, gravity)
- **Image simulation**:
  - Forward projection of world plane to camera
  - Gaussian, Poisson noise, motion blur
- **Validation**:
  - Reprojection error, Mean Squared Error (MSE)
  - TODO: Add SSIM, perceptual metrics
- **I/O helpers**:
  - Save/load calibration results to YAML

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd camera_simulation

2. Install dependencies:

```bash
pip install numpy opencv-python matplotlib scipy

### or conda/mamba
conda install numpy opencv-python matplotlib scipy
```



## Usage Overview

1. Generate Calibration Pattern
2. Calibrate Camera
3. Save & Load Calibration (YAML)
4. Simulate Pendulum & Camera View
5. Validate



## File Structure

```
camera_simulation/
├── display.py
├── camera_model.py
├── physical_model.py
├── simulation.py
├── validation.py
├── io_helpers.py
├── __init__.py
└── main_demo.py
```



## TODO

* Add SSIM (Structural Similarity Index) and perceptual metrics
* Extend to support asymmetric circle grid calibration patterns
* Add pendulum synthetic video generation for tracking algorithm tests



## License

MIT License (modify as needed)



## Author

* **ekafex**
  Created on Thu Jul 24 2025



## **Next Step**

Do you want me to:
1. **Integrate the YAML helper into `main_demo.py`** (so it saves calibration after computing)?  
2. Also **generate synthetic calibration images automatically** (for full offline testing without real camera)?  
3. Prepare a **setup.py or pyproject.toml** so you can install this as a package (`pip install -e .`)?
