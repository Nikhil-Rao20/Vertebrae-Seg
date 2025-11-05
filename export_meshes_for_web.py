"""
Export vertebrae meshes for web viewing
Uses PyVista's high-quality rendering settings
"""
import os
import json
import numpy as np
import nibabel as nib
import pyvista as pv
from skimage import measure

# Vertebrae color mapping (matching notebook)
VERTEBRAE_COLORS = {
    1: '#FF0000', 2: '#FF4500', 3: '#FF8C00', 4: '#FFD700', 5: '#ADFF2F', 6: '#00FF00', 7: '#00CED1',
    8: '#1E90FF', 9: '#0000FF', 10: '#8A2BE2', 11: '#9400D3', 12: '#FF00FF', 13: '#FF1493', 14: '#DC143C',
    15: '#8B4513', 16: '#D2691E', 17: '#CD853F', 18: '#DEB887', 19: '#F0E68C',
    20: '#808000', 21: '#556B2F', 22: '#228B22', 23: '#008080', 24: '#4682B4'
}

VERTEBRAE_NAMES = {
    1: 'C1', 2: 'C2', 3: 'C3', 4: 'C4', 5: 'C5', 6: 'C6', 7: 'C7',
    8: 'T1', 9: 'T2', 10: 'T3', 11: 'T4', 12: 'T5', 13: 'T6',
    14: 'T7', 15: 'T8', 16: 'T9', 17: 'T10', 18: 'T11', 19: 'T12',
    20: 'L1', 21: 'L2', 22: 'L3', 23: 'L4', 24: 'L5'
}

def process_vertebra(labels, label_value):
    """Process single vertebra with PyVista quality settings"""
    mask = (labels == label_value).astype(np.uint8)
    
    # Extract surface mesh using marching cubes
    verts, faces, normals, values = measure.marching_cubes(mask, level=0.5)
    
    # Convert to PyVista format
    faces_vtk = np.hstack([np.full((faces.shape[0], 1), 3), faces]).astype(np.int64)
    mesh = pv.PolyData(verts, faces_vtk)
    
    # Apply PyVista smoothing (matching notebook settings)
    mesh = mesh.smooth(n_iter=50, relaxation_factor=0.1)
    mesh = mesh.decimate(target_reduction=0.6)  # Less aggressive decimation
    
    # Extract processed mesh data directly from numpy arrays
    verts = mesh.points.tolist()
    
    # Extract faces properly
    faces = []
    for i in range(mesh.n_cells):
        cell = mesh.get_cell(i)
        if cell.n_points == 3:
            point_ids = [int(cell.point_ids[j]) for j in range(3)]
            faces.append(point_ids)
    
    return {
        'vertices': verts,
        'faces': faces
    }

def process_patient(patient_id):
    """Process all vertebrae for one patient"""
    print(f"\n{'='*60}")
    print(f"Processing: {patient_id}")
    print(f"{'='*60}")
    
    nii_path = f"{patient_id}/combined_labels.nii.gz"
    if not os.path.exists(nii_path):
        print(f"❌ File not found: {nii_path}")
        return None
    
    # Load data
    nii = nib.load(nii_path)
    labels = nii.get_fdata().astype(np.uint8)
    print(f"Data shape: {labels.shape}")
    
    # Create output directory
    output_dir = f"web_data/{patient_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each vertebra
    patient_data = {'vertebrae': {}}
    unique_labels = sorted(set(np.unique(labels)) - {0})
    
    for label_value in unique_labels:
        name = VERTEBRAE_NAMES.get(label_value, f"Label_{label_value}")
        print(f"  {name} (label {label_value})...", end=' ', flush=True)
        
        try:
            mesh_data = process_vertebra(labels, label_value)
            
            # Save individual mesh
            mesh_file = f"{output_dir}/{name}.json"
            with open(mesh_file, 'w') as f:
                json.dump(mesh_data, f)
            
            patient_data['vertebrae'][name] = {
                'label': int(label_value),
                'color': VERTEBRAE_COLORS.get(label_value, '#CCCCCC'),
                'file': f"web_data/{patient_id}/{name}.json",
                'vertices': len(mesh_data['vertices'])
            }
            print(f"✓ ({len(mesh_data['vertices'])} vertices)")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Save patient metadata
    metadata_file = f"{output_dir}/metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(patient_data, f, indent=2)
    
    print(f"\n✓ Completed {patient_id} - {len(patient_data['vertebrae'])} vertebrae")
    return patient_data

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  Vertebrae Mesh Export for Web (PyVista Quality)          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    os.makedirs("web_data", exist_ok=True)
    
    patients = ["BDMAP_00000006", "BDMAP_00000031"]
    all_data = {}
    
    for patient_id in patients:
        data = process_patient(patient_id)
        if data:
            all_data[patient_id] = data
    
    # Save combined index
    with open("web_data/patients.json", 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print("\n" + "="*60)
    print("✓ Export complete! Files saved to: web_data/")
    print("="*60)

if __name__ == "__main__":
    main()
