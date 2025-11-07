# Vertebrae Segmentation 3D Viewer

An interactive 3D web application for visualizing and analyzing vertebrae segmentation results from medical imaging. This tool provides real-time visualization of raw predictions, post-processed results, and detailed difference analysis to understand the impact of post-processing on segmentation quality. Built as part of the BodyMaps research program at Johns Hopkins University.

The viewer enables researchers and clinicians to interactively explore vertebrae segmentation outputs from the SuPreM (Supreme) segmentation model, compare raw predictions against cleaned results, and identify specific regions affected by the post-processing pipeline. With intuitive controls and professional rendering quality, it bridges the gap between automated segmentation and clinical interpretation.

<!-- Patient 06 -->
<div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:18px;flex-wrap:wrap;">
  <figure style="flex:1;min-width:220px;margin:0;">
    <img src="assest/img1.png" alt="BDMAP_00000006" style="width:100%;height:auto;">
  </figure>

  <figure style="flex:1;min-width:220px;margin:0;">
    <img src="assest/img2.png" alt="BDMAP_00000031" style="width:100%;height:auto">
  </figure>
</div>


## 🌟 Key Features

### **Three Visualization Modes**

The application offers three distinct viewing modes to comprehensively analyze segmentation results:

- **Raw Prediction Mode**: Displays the original output from the SuPreM vertebrae segmentation model without any modifications. This shows the baseline performance including any artifacts, noise, or fragmentation that may be present in the automated segmentation.

- **Post-Processed Mode**: Shows the enhanced segmentation after applying a sophisticated 4-phase cleaning pipeline. This mode demonstrates how morphological operations, component extraction, and smoothing improve the segmentation quality by removing noise, filling holes, and producing anatomically coherent vertebrae structures.

- **Difference Mode**: Provides a direct visual comparison between raw and post-processed results by highlighting exactly what changed during the cleaning pipeline. This unique feature uses color-coded visualization where red regions (False Positives) indicate voxels removed during post-processing, and blue regions (False Negatives) show voxels added. This allows precise identification of where and how the post-processing algorithm modified the segmentation.

### **Interactive 3D Controls**

Experience professional-grade 3D interaction with smooth, responsive controls:

- **Rotation**: Left-click and drag to freely rotate the 3D view and examine vertebrae from any angle
- **Panning**: Right-click and drag to pan the camera and reposition the view
- **Zooming**: Use the mouse scroll wheel to zoom in for detailed inspection or zoom out for overview
- **Preset Views**: Quick access buttons for standard anatomical views (3D, Front, Side, Top)
- **Real-time Rendering**: Smooth 60 FPS rendering with high-quality lighting and shadows

### **Granular Vertebrae Control**

Fine-tune your visualization by controlling individual vertebrae visibility:

- **Individual Toggle**: Show or hide any of the 24 vertebrae (C1-L5) independently
- **Anatomical Grouping**: Vertebrae organized by spinal region with collapsible sections:
  - Cervical (C1-C7): 7 neck vertebrae
  - Thoracic (T1-T12): 12 mid-back vertebrae  
  - Lumbar (L1-L5): 5 lower back vertebrae
- **Batch Operations**: Quick "Select All" or "Deselect All" buttons for rapid control
- **Color Indicators**: Each vertebra has a distinct color shown in the control panel matching its 3D representation

### **Multi-Patient Support**

Seamlessly switch between different patient datasets to compare segmentation quality across cases:

- **Patient Selection**: Toggle between available patient IDs with a single click
- **Persistent Settings**: Viewing mode and visibility preferences maintained when switching patients
- **Default Loading**: Application automatically loads Patient 06 (BDMAP_00000006) on startup for immediate viewing

### **Professional Quality Rendering**

The viewer uses advanced rendering techniques to produce publication-quality visualizations:

- **PyVista-Matched Lighting**: Multi-directional lighting setup that precisely replicates PyVista's professional rendering
- **Smooth Shading**: Per-vertex normal computation for smooth, artifact-free surface appearance
- **Shadow Mapping**: Real-time shadow casting for enhanced depth perception
- **High-Resolution Meshes**: Carefully optimized mesh decimation balances visual quality with performance
- **Anti-Aliasing**: Multi-sample anti-aliasing (MSAA) eliminates jagged edges

### **Informative Legend & UI**

Context-aware interface elements provide necessary information without cluttering the view:

- **Dynamic Legend**: Automatically appears in Difference mode showing color coding for FP (red) and FN (blue)
- **Status Badge**: Displays current visualization mode with color-coded indicator (blue for Raw, green for Post-Processed, orange for Difference)
- **Loading Indicators**: Clear visual feedback during data loading with progress information
- **Responsive Layout**: Clean, modern interface that adapts to different screen sizes

## 🚀 Quick Start Guide

### For Users with SuPreM Vertebrae Predictions

If you have vertebrae segmentation results from the SuPreM model, follow these steps to visualize them in the 3D viewer:

#### **Step 1: Prepare Your Data**

Ensure your segmentation is in NIfTI format (`.nii.gz`) with the following structure:
- **File format**: NIfTI compressed (`.nii.gz`)
- **Label encoding**: Integer labels from 1-24 representing vertebrae C1-L5
- **Background**: Label 0 for non-vertebrae regions
- **Required files**:
  - `combined_labels.nii.gz` - Raw predictions from SuPreM model
  - `combined_labels_CLEANED.nii.gz` - Post-processed version (generated in Step 3)

Place your files in a folder structure like:
```
YourProject/
├── PATIENT_ID_001/
│   └── combined_labels.nii.gz
├── PATIENT_ID_002/
│   └── combined_labels.nii.gz
```

#### **Step 2: Set Up Python Environment**

Install required dependencies:

```bash
# Create a conda environment (recommended)
conda create -n vertebrae_viewer python=3.12
conda activate vertebrae_viewer

# Install required packages
pip install pyvista nibabel scikit-image scipy pandas numpy
```

#### **Step 3: Run Post-Processing (Optional but Recommended)**

If you want to see the post-processed results and difference visualization, run the cleaning pipeline:

```python
# The post_processing.ipynb notebook contains the full pipeline
# Or you can process directly with the included script
python export_all_for_web.py
```

This will:
- Apply the 4-phase post-processing pipeline to your raw predictions
- Generate the `combined_labels_CLEANED.nii.gz` file
- Create both raw and cleaned versions for visualization

#### **Step 4: Export to Web Format**

Convert your NIfTI segmentations to web-ready 3D meshes:

```bash
# Run the export script
python export_all_for_web.py
```

This script will:
1. **Load** your NIfTI files (both raw and cleaned versions)
2. **Extract** 3D surface meshes using marching cubes algorithm
3. **Apply** smoothing and optimization for web performance
4. **Generate** three datasets:
   - `web_data/PATIENT_ID/` - Raw prediction meshes
   - `web_data/PATIENT_ID_cleaned/` - Post-processed meshes
   - `web_data/PATIENT_ID_difference/` - Difference visualization meshes
5. **Create** metadata JSON files with colors and file references

Expected output structure:
```
web_data/
├── PATIENT_ID/
│   ├── metadata.json
│   ├── C1.json, C2.json, ..., L5.json
├── PATIENT_ID_cleaned/
│   ├── metadata.json
│   ├── C1.json, C2.json, ..., L5.json
└── PATIENT_ID_difference/
    ├── metadata.json
    ├── C1_removed.json, C1_added.json, ...
```

#### **Step 5: Add Your Patient to the Viewer**

Update the patient list in `index.html`:

```html
<div class="nav-group">
    <span class="nav-label">Patient:</span>
    <div class="processing-buttons">
        <button class="processing-btn active" onclick="setPatient('BDMAP_00000006')">Patient 06</button>
        <button class="processing-btn" onclick="setPatient('BDMAP_00000031')">Patient 31</button>
        <!-- Add your new patient -->
        <button class="processing-btn" onclick="setPatient('PATIENT_ID_001')">Patient 001</button>
    </div>
</div>
```

#### **Step 6: Launch the Viewer**

Start a local web server and open the viewer:

```bash
# Navigate to project directory
cd YourProject

# Start HTTP server (Python 3)
python -m http.server 8080

# Or use Python 2
python -m SimpleHTTPServer 8080

# Or use Node.js http-server
npx http-server -p 8080
```

Open your browser and navigate to: **http://localhost:8080**

#### **Step 7: Explore Your Data**

1. **Select your patient** using the Patient buttons
2. **Switch between modes**:
   - Click "Raw" to see original SuPreM predictions
   - Click "Post-Processed" to see cleaned results
   - Click "Difference" to analyze what changed
3. **Control visibility**: Use the "Vertebrae Controls" dropdown to show/hide specific vertebrae
4. **Navigate the 3D view**: Rotate, pan, and zoom to explore from different angles

### Verification & Quality Check

After exporting, you can verify your data was processed correctly:

```bash
# Optional: Run verification script
python verify_difference_data.py
```

This will display statistics about:
- Number of voxels in raw vs cleaned segmentations
- Voxels removed and added during post-processing
- Per-vertebra change percentages
- Overall segmentation quality metrics

## 📊 Post-Processing Pipeline Details

### **Phase 1: Morphological Cleaning**

The first phase removes noise and fills internal gaps using binary morphological operations:

- **Binary Fill Holes**: Closes internal voids within vertebrae that often occur due to CT imaging artifacts or incomplete segmentation
- **Closing Operation**: Applies dilation followed by erosion using a 3×3×3 cubic structuring element to bridge small gaps between nearby regions
- **Opening Operation**: Applies erosion followed by dilation using a 2×2×2 cubic structuring element to remove small isolated noise pixels

**Effect**: Produces cleaner, more solid vertebrae structures without small holes or noise speckles

### **Phase 2: Largest Component Extraction**

Removes fragmented pieces by keeping only the main connected component:

- **Connected Components Labeling**: Identifies all separate 3D regions for each vertebra label
- **Volume Calculation**: Measures the size of each connected component
- **Component Selection**: Retains only the largest component (by voxel count) and discards all fragments
- **Reassignment**: Updates the segmentation mask to contain only the main vertebral body

**Effect**: Eliminates spurious fragments that are disconnected from the main vertebral body, ensuring each vertebra is represented by a single coherent structure

### **Phase 3: Gaussian Smoothing**

Refines boundaries while preserving overall structure:

- **Gaussian Filter**: Applies 3D Gaussian blur with sigma=1.5 to smooth voxel intensities
- **Re-thresholding**: Converts smoothed floating-point values back to binary mask at threshold 0.5
- **Boundary Refinement**: Smooths jagged edges while maintaining overall vertebra shape

**Effect**: Produces smoother, more anatomically realistic surface boundaries without the "blocky" appearance of raw voxel segmentation

### **Phase 4: Mesh-Level Enhancement**

Optimizes the 3D surface mesh for visual quality and performance:

- **Marching Cubes**: Extracts triangulated surface mesh from binary mask using physical spacing for correct proportions
- **Taubin Smoothing**: Applies 50 iterations of Taubin low-pass filtering (pass_band=0.05) to smooth mesh surfaces without shrinkage
- **Selective Decimation**: Reduces mesh complexity by 30% for meshes with >5000 vertices to improve rendering performance while maintaining visual quality

**Effect**: Creates smooth, high-quality 3D meshes suitable for interactive web visualization with optimal performance

### **Performance Results**

| Metric | Raw Prediction | Post-Processed | Improvement |
|--------|----------------|----------------|-------------|
| Vertebrae with fragments | 18/24 (75%) | 0/24 (0%) | ✅ 100% fixed |
| Connected components per vertebra | 1-9 | 1 | ✅ All unified |
| Average surface roughness | 152.68 | 121.50 | ✅ 20% smoother |
| Processing time per vertebra | - | ~15 seconds | Acceptable for clinical use |
| Average mesh vertices | ~8,500 | ~6,000 | ✅ 29% optimized |

## 🎨 Color Coding Scheme

Vertebrae are color-coded by spinal region to facilitate anatomical identification:

### **Cervical Vertebrae (C1-C7)** - Warm to Cool Gradient
- **C1 (Atlas)**: `#FF0000` - Bright Red
- **C2 (Axis)**: `#FF4500` - Orange Red
- **C3**: `#FF8C00` - Dark Orange
- **C4**: `#FFD700` - Gold
- **C5**: `#ADFF2F` - Green Yellow
- **C6**: `#00FF00` - Lime Green
- **C7**: `#00CED1` - Dark Turquoise

### **Thoracic Vertebrae (T1-T12)** - Cool Spectrum
- **T1**: `#1E90FF` - Dodger Blue
- **T2**: `#0000FF` - Pure Blue
- **T3**: `#8A2BE2` - Blue Violet
- **T4**: `#9400D3` - Dark Violet
- **T5**: `#FF00FF` - Magenta
- **T6**: `#FF1493` - Deep Pink
- **T7**: `#DC143C` - Crimson
- **T8**: `#8B4513` - Saddle Brown
- **T9**: `#D2691E` - Chocolate
- **T10**: `#CD853F` - Peru
- **T11**: `#DEB887` - Burlywood
- **T12**: `#F0E68C` - Khaki

### **Lumbar Vertebrae (L1-L5)** - Earth Tones to Blue
- **L1**: `#808000` - Olive
- **L2**: `#556B2F` - Dark Olive Green
- **L3**: `#228B22` - Forest Green
- **L4**: `#008080` - Teal
- **L5**: `#4682B4` - Steel Blue

### **Difference Mode Colors**
- **False Positive (Removed)**: `#FF4444` - Red - Voxels present in raw but removed in post-processed
- **False Negative (Added)**: `#4444FF` - Blue - Voxels absent in raw but added in post-processed

## 🛠️ Technology Stack

### **Frontend Technologies**
- **HTML5**: Semantic markup and structure
- **CSS3**: Modern styling with flexbox, gradients, and animations
- **JavaScript ES6+**: Modular code with async/await, arrow functions, and destructuring
- **Three.js r128**: Industry-standard WebGL 3D rendering library

### **Backend Processing**
- **Python 3.12**: Core processing language
- **PyVista 0.46.4**: High-level 3D visualization and mesh processing
- **nibabel 5.3.2**: NIfTI medical imaging file I/O
- **scikit-image 0.23.2**: Image processing algorithms (marching cubes, morphology)
- **scipy 1.13.1**: Scientific computing (Gaussian filters, ndimage operations)
- **numpy 1.26.4**: Numerical array operations

## 📁 Complete Project Structure

```
Vertebrae_Seg/
├── index.html                      # Main web application
├── app.js                          # Three.js viewer logic and controls
│
├── export_all_for_web.py           # Master export script (raw + cleaned + difference)
├── verify_difference_data.py       # Quality assurance and verification
│
├── post_processing.ipynb           # Interactive analysis notebook
├── main.ipynb                      # Development and testing notebook
│
├── web_data/                       # Generated mesh data for web viewer
│   ├── BDMAP_00000006/            # Patient 06 - Raw predictions
│   │   ├── metadata.json          # Vertebrae colors and file paths
│   │   ├── C1.json, C2.json, ... L5.json  # Individual vertebra meshes
│   │
│   ├── BDMAP_00000006_cleaned/    # Patient 06 - Post-processed
│   │   ├── metadata.json
│   │   ├── C1.json, C2.json, ... L5.json
│   │
│   ├── BDMAP_00000006_difference/ # Patient 06 - Difference analysis
│   │   ├── metadata.json
│   │   ├── C1_removed.json, C1_added.json, ...
│   │
│   └── BDMAP_00000031/...         # Additional patients
│
├── BDMAP_00000006/                 # Patient 06 source data
│   ├── combined_labels.nii.gz     # Raw SuPreM predictions
│   └── combined_labels_CLEANED.nii.gz  # Post-processed output
│
├── BDMAP_00000031/                 # Patient 31 source data
│   └── ...
│
├── assest/                         # Images and static resources
└── README.md                       # This file
```

## 👤 Author & Contact

**Nikhileswara Rao Sulake**  

- 🌐 Personal Website: [nikhil-rao20.github.io](https://nikhil-rao20.github.io)
- 💻 GitHub: [@nikhil-rao20](https://github.com/nikhil-rao20)
- 📧 Email: [nikhil01446@gmail.com](mailto:nikhil01446@gmail.com)

## 🙏 Acknowledgments

- **BodyMaps Program** at Johns Hopkins University for research support and resources
- **SuPreM Segmentation Model** team for providing the baseline vertebrae segmentation
- **PyVista Community** for exceptional 3D visualization tools and documentation


## 🔬 Research Context

This tool was developed to support vertebrae segmentation research as a part of my initial task for research assistant position in the BodyMaps Program, which aims to advance automated analysis of medical imaging for clinical applications. The visualization capabilities enable detailed quality assessment of automated segmentation algorithms and facilitate the development of improved post-processing techniques.

---

**Built with ❤️ for medical imaging research and clinical applications**
