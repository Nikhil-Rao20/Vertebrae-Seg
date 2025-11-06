"""
Export ALL meshes for web viewing: Raw, Cleaned, and Difference
Uses proper physical spacing to ensure meshes overlay correctly
"""
import os
import json
import numpy as np
import nibabel as nib
from skimage import measure
from pathlib import Path
import time

# Vertebrae color mapping
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

DIFFERENCE_COLORS = {
    'removed': '#FF4444',  # Red
    'added': '#4444FF',    # Blue
}


def create_mesh_from_mask(mask, spacing, step_size=1):
    """Create mesh with proper physical spacing"""
    if mask.sum() == 0:
        return None, None
    
    try:
        # CRITICAL: Use spacing to convert voxel coords to physical coords
        verts, faces, normals, values = measure.marching_cubes(
            mask,
            level=0.5,
            spacing=spacing,  # Physical spacing in mm
            step_size=step_size
        )
        return verts, faces
    except Exception as e:
        print(f"  ⚠️ Marching cubes failed: {e}")
        return None, None


def export_raw_meshes(patient_id):
    """Export raw prediction meshes"""
    print(f"\n{'='*70}")
    print(f"📦 Exporting RAW meshes: {patient_id}")
    print(f"{'='*70}")
    
    nii_path = f"{patient_id}/combined_labels.nii.gz"
    nii = nib.load(nii_path)
    labels = nii.get_fdata().astype(np.uint8)
    spacing = tuple(float(x) for x in nii.header.get_zooms())
    
    print(f"Shape: {labels.shape}, Spacing: {spacing}")
    
    output_dir = f"web_data/{patient_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    metadata = {'vertebrae': {}}
    unique_labels = sorted(set(np.unique(labels)) - {0})
    
    for label_value in unique_labels:
        name = VERTEBRAE_NAMES.get(int(label_value), f"Label_{int(label_value)}")
        print(f"  {name}...", end=' ', flush=True)
        
        mask = (labels == label_value).astype(np.uint8)
        verts, faces = create_mesh_from_mask(mask, spacing)
        
        if verts is not None:
            mesh_file = f"{output_dir}/{name}.json"
            with open(mesh_file, 'w') as f:
                json.dump({'vertices': verts.tolist(), 'faces': faces.tolist()}, f)
            
            metadata['vertebrae'][name] = {
                'label': int(label_value),
                'color': VERTEBRAE_COLORS.get(int(label_value), '#CCCCCC'),
                'file': f"web_data/{patient_id}/{name}.json",
                'vertices': len(verts)
            }
            print(f"✓ ({len(verts):,} vertices)")
        else:
            print(f"❌ Failed")
    
    with open(f"{output_dir}/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Raw meshes exported: {len(metadata['vertebrae'])} vertebrae\n")
    return metadata


def export_cleaned_meshes(patient_id):
    """Export cleaned (post-processed) prediction meshes"""
    print(f"\n{'='*70}")
    print(f"🧹 Exporting CLEANED meshes: {patient_id}")
    print(f"{'='*70}")
    
    nii_path = f"{patient_id}/combined_labels_CLEANED.nii.gz"
    nii = nib.load(nii_path)
    labels = nii.get_fdata().astype(np.uint8)
    spacing = tuple(float(x) for x in nii.header.get_zooms())
    
    print(f"Shape: {labels.shape}, Spacing: {spacing}")
    
    output_dir = f"web_data/{patient_id}_cleaned"
    os.makedirs(output_dir, exist_ok=True)
    
    metadata = {'vertebrae': {}}
    unique_labels = sorted(set(np.unique(labels)) - {0})
    
    for label_value in unique_labels:
        name = VERTEBRAE_NAMES.get(int(label_value), f"Label_{int(label_value)}")
        print(f"  {name}...", end=' ', flush=True)
        
        mask = (labels == label_value).astype(np.uint8)
        verts, faces = create_mesh_from_mask(mask, spacing)
        
        if verts is not None:
            mesh_file = f"{output_dir}/{name}.json"
            with open(mesh_file, 'w') as f:
                json.dump({'vertices': verts.tolist(), 'faces': faces.tolist()}, f)
            
            metadata['vertebrae'][name] = {
                'label': int(label_value),
                'color': VERTEBRAE_COLORS.get(int(label_value), '#CCCCCC'),
                'file': f"web_data/{patient_id}_cleaned/{name}.json",
                'vertices': len(verts)
            }
            print(f"✓ ({len(verts):,} vertices)")
        else:
            print(f"❌ Failed")
    
    with open(f"{output_dir}/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Cleaned meshes exported: {len(metadata['vertebrae'])} vertebrae\n")
    return metadata


def export_difference_meshes(patient_id):
    """Export difference meshes (removed/added parts)"""
    print(f"\n{'='*70}")
    print(f"🔀 Exporting DIFFERENCE meshes: {patient_id}")
    print(f"{'='*70}")
    
    # Load both raw and cleaned
    raw_img = nib.load(f"{patient_id}/combined_labels.nii.gz")
    cleaned_img = nib.load(f"{patient_id}/combined_labels_CLEANED.nii.gz")
    
    raw_data = raw_img.get_fdata()
    cleaned_data = cleaned_img.get_fdata()
    spacing = tuple(float(x) for x in raw_img.header.get_zooms())
    
    print(f"Shape: {raw_data.shape}, Spacing: {spacing}")
    
    output_dir = f"web_data/{patient_id}_difference"
    os.makedirs(output_dir, exist_ok=True)
    
    metadata = {
        'patient_id': patient_id,
        'visualization_type': 'difference',
        'description': 'Difference between raw and post-processed predictions',
        'shape': list(raw_data.shape),
        'spacing': list(spacing),
        'colors': DIFFERENCE_COLORS,
        'vertebrae': {}
    }
    
    unique_labels = sorted(set(np.unique(cleaned_data)) - {0})
    
    total_removed = 0
    total_added = 0
    
    for label_num in unique_labels:
        name = VERTEBRAE_NAMES.get(int(label_num), f"Label_{int(label_num)}")
        print(f"  {name}...", end=' ', flush=True)
        
        raw_mask = (raw_data == label_num).astype(np.uint8)
        cleaned_mask = (cleaned_data == label_num).astype(np.uint8)
        
        removed_mask = (raw_mask == 1) & (cleaned_mask == 0)
        added_mask = (cleaned_mask == 1) & (raw_mask == 0)
        
        removed_voxels = int(removed_mask.sum())
        added_voxels = int(added_mask.sum())
        
        total_removed += removed_voxels
        total_added += added_voxels
        
        vertebra_info = {
            'name': name,
            'label': int(label_num),
            'raw_voxels': int(raw_mask.sum()),
            'cleaned_voxels': int(cleaned_mask.sum()),
            'removed_voxels': removed_voxels,
            'added_voxels': added_voxels,
            'meshes': {}
        }
        
        # Export removed mesh
        if removed_voxels > 0:
            verts, faces = create_mesh_from_mask(removed_mask, spacing)
            if verts is not None:
                mesh_file = f"{output_dir}/{name}_removed.json"
                with open(mesh_file, 'w') as f:
                    json.dump({'vertices': verts.tolist(), 'faces': faces.tolist(), 'color': DIFFERENCE_COLORS['removed']}, f)
                
                vertebra_info['meshes']['removed'] = {
                    'file': f"web_data/{patient_id}_difference/{name}_removed.json",
                    'color': DIFFERENCE_COLORS['removed'],
                    'vertices': len(verts),
                    'faces': len(faces),
                    'voxels': removed_voxels
                }
        
        # Export added mesh
        if added_voxels > 0:
            verts, faces = create_mesh_from_mask(added_mask, spacing)
            if verts is not None:
                mesh_file = f"{output_dir}/{name}_added.json"
                with open(mesh_file, 'w') as f:
                    json.dump({'vertices': verts.tolist(), 'faces': faces.tolist(), 'color': DIFFERENCE_COLORS['added']}, f)
                
                vertebra_info['meshes']['added'] = {
                    'file': f"web_data/{patient_id}_difference/{name}_added.json",
                    'color': DIFFERENCE_COLORS['added'],
                    'vertices': len(verts),
                    'faces': len(faces),
                    'voxels': added_voxels
                }
        
        metadata['vertebrae'][name] = vertebra_info
        print(f"✓ (R:{removed_voxels}, A:{added_voxels})")
    
    with open(f"{output_dir}/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Difference meshes exported")
    print(f"  Total removed: {total_removed:,} voxels")
    print(f"  Total added: {total_added:,} voxels\n")
    return metadata


def main():
    start_time = time.time()
    
    print("\n" + "="*70)
    print("🚀 EXPORT ALL MESHES FOR WEB (WITH PROPER SPACING)")
    print("="*70)
    print("\nThis will export:")
    print("  1. Raw predictions")
    print("  2. Cleaned (post-processed) predictions")
    print("  3. Difference meshes (removed/added parts)")
    print("\nAll meshes will use physical spacing for proper overlay!")
    print("="*70)
    
    os.makedirs("web_data", exist_ok=True)
    
    patients = ['BDMAP_00000006', 'BDMAP_00000031']
    
    for patient_id in patients:
        try:
            export_raw_meshes(patient_id)
            export_cleaned_meshes(patient_id)
            export_difference_meshes(patient_id)
        except Exception as e:
            print(f"\n❌ Error processing {patient_id}: {e}")
            import traceback
            traceback.print_exc()
    
    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"✅ ALL DONE! Total time: {elapsed:.1f}s")
    print(f"{'='*70}\n")
    print("📁 Output: web_data/")
    print("   - BDMAP_00000006/ (raw)")
    print("   - BDMAP_00000006_cleaned/ (cleaned)")
    print("   - BDMAP_00000006_difference/ (difference)")
    print("   - BDMAP_00000031/ (raw)")
    print("   - BDMAP_00000031_cleaned/ (cleaned)")
    print("   - BDMAP_00000031_difference/ (difference)")
    print("\n🌐 Now refresh your website to see the corrected overlay!")


if __name__ == '__main__':
    main()
