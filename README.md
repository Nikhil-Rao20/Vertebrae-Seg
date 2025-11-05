# 🦴 Vertebrae Segmentation 3D Viewer

Professional 3D visualization tool for vertebrae segmentation with post-processing capabilities. Built for the BodyMaps Program at Johns Hopkins University.

![Vertebrae 3D Visualization](BDMAP_00000006_vertebrae_3d_ENHANCED.png)

## 🌟 Features

### Interactive 3D Viewer
- **Real-time 3D rendering** with Three.js
- **Smooth controls**: Rotate (left-click), Pan (right-click), Zoom (scroll)
- **Professional lighting** matching PyVista quality
- **High-performance** mesh decimation and optimization

### Processing Options
- **Raw Prediction**: Original SuPreM model output
- **Post-Processed**: Enhanced with 4-phase pipeline
  - Morphological cleaning (fill holes, closing, opening)
  - Largest component extraction (removes fragments)
  - Gaussian smoothing (boundary refinement)
  - Taubin smoothing (mesh-level enhancement)

### Vertebrae Controls
- **Individual toggle** for all 24 vertebrae
- **Grouped selection** by region:
  - Cervical (C1-C7) - Red to Turquoise
  - Thoracic (T1-T12) - Blue to Brown spectrum
  - Lumbar (L1-L5) - Green to Steel Blue
- **Select All / Deselect All** shortcuts

### Multiple Patients
- Switch between different patient datasets
- Currently supports:
  - BDMAP_00000006
  - BDMAP_00000031

## 🚀 Live Demo

**[View Live Demo →](https://nikhil-rao20.github.io/Vertebrae_Seg/)**

## 📊 Post-Processing Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Fragmented vertebrae | 18/24 | 0/24 | ✅ 100% fixed |
| Connected components | 1-9 | 1 | ✅ All single |
| Average compactness | 152.68 | 121.50 | ✅ 31.18 reduction |
| Processing time | - | ~15s/vertebra | - |

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **3D Rendering**: Three.js r128
- **Backend Processing**: Python 3.12
- **Libraries**:
  - PyVista 0.46.4 (3D visualization)
  - nibabel 5.3.2 (NIfTI file handling)
  - scikit-image 0.23.2 (image processing)
  - scipy 1.13.1 (scientific computing)

## 📁 Project Structure

```
Vertebrae_Seg/
├── index.html              # Main website
├── app.js                  # Three.js viewer logic
├── vertebrae_visualization.ipynb  # Analysis notebook
├── export_meshes_for_web.py      # Mesh export script
├── web_data/               # Processed mesh data
│   ├── BDMAP_00000006/     # Raw patient data
│   │   ├── C1.json, C2.json, ...
│   │   └── metadata.json
│   └── BDMAP_00000006_cleaned/  # Post-processed data
│       ├── C1.json, C2.json, ...
│       └── metadata.json
└── README.md
```

## 🔧 Local Setup

### Prerequisites
```bash
# Python 3.12+
conda create -n vertebrae python=3.12
conda activate vertebrae

# Install dependencies
pip install pyvista nibabel scikit-image scipy pandas
```

### Run Locally
```bash
# Clone repository
git clone https://github.com/nikhil-rao20/Vertebrae_Seg.git
cd Vertebrae_Seg

# Start HTTP server
python -m http.server 8080

# Open browser
# Navigate to http://localhost:8080
```

## 📝 Usage

### Jupyter Notebook Analysis
The `vertebrae_visualization.ipynb` notebook contains:
1. Quality analysis of raw segmentation
2. 4-phase post-processing pipeline
3. Before/after comparison metrics
4. High-resolution PyVista visualization
5. Export to web-ready JSON meshes

### Export New Data
```bash
python export_meshes_for_web.py
```

This will:
- Load NIfTI segmentation files
- Apply PyVista smoothing and decimation
- Export to JSON format for web viewing
- Generate metadata with colors and file paths

## 🎨 Color Scheme

### Cervical (C1-C7)
- C1: Red (#FF0000) → C7: Dark Turquoise (#00CED1)
- Gradient from warm (top) to cool colors

### Thoracic (T1-T12)
- T1: Dodger Blue (#1E90FF) → T12: Khaki (#F0E68C)
- Blue-purple-pink-brown spectrum

### Lumbar (L1-L5)
- L1: Olive (#808000) → L5: Steel Blue (#4682B4)
- Green to blue gradient

## 📈 Pipeline Details

### Phase 1: Morphological Cleaning
- Binary fill holes (close internal gaps)
- Closing operation (3×3×3 structuring element)
- Opening operation (2×2×2 structuring element)

### Phase 2: Component Extraction
- Label connected components
- Identify largest component by volume
- Remove all smaller fragments

### Phase 3: Gaussian Smoothing
- Apply Gaussian filter (σ=1.5)
- Re-threshold at 0.5 to maintain binary mask
- Smooth boundary irregularities

### Phase 4: Mesh Enhancement
- Marching cubes surface extraction
- Taubin smoothing (50 iterations, pass_band=0.05)
- Gentle decimation (30% reduction if >5000 vertices)

## 👤 Author

**Nikhileswara Rao Sulake**  
Research Assistant - BodyMaps Program  
Johns Hopkins University

- Website: [nikhil-rao20.github.io](https://nikhil-rao20.github.io)
- GitHub: [@nikhil-rao20](https://github.com/nikhil-rao20)

## 📄 License

This project is part of research work at Johns Hopkins University.

## 🙏 Acknowledgments

- BodyMaps Program at Johns Hopkins University
- SuPreM segmentation model team
- PyVista community for excellent 3D visualization tools

---

**Built with ❤️ for medical imaging research**
