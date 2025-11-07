"""
Post-Processing Pipeline for Vertebrae Segmentation

Input Structure:
    PATIENT_ID/
    ├── combined_labels.nii.gz
    └── segmentations/
        ├── vertebrae_C1.nii.gz
        ├── vertebrae_C2.nii.gz
        └── ... (24 files total)

Output Structure:
    PATIENT_ID_post_processed/
    ├── combined_labels.nii.gz          (post-processed)
    └── segmentations/
        ├── vertebrae_C1.nii.gz         (post-processed)
        ├── vertebrae_C2.nii.gz         (post-processed)
        └── ... (24 files total)

Usage:
    python postprocessing_vertebrae.py BDMAP_00000006 BDMAP_00000031
"""

import os
import sys
import time
import numpy as np
import nibabel as nib
from pathlib import Path
from scipy.ndimage import binary_closing, binary_opening, binary_fill_holes
from scipy.ndimage import gaussian_filter, label as ndimage_label

def morphological_clean(mask, closing_size=3, opening_size=2):
    """
    Remove noise and small fragments using morphological operations
    """
    # Fill small holes
    cleaned = binary_fill_holes(mask)
    
    # Closing: connect nearby regions, fill small gaps
    structure_close = np.ones((closing_size, closing_size, closing_size))
    cleaned = binary_closing(cleaned, structure=structure_close)
    
    # Opening: remove small noise/fragments
    structure_open = np.ones((opening_size, opening_size, opening_size))
    cleaned = binary_opening(cleaned, structure=structure_open)
    
    return cleaned.astype(np.uint8)


def keep_largest_component(mask):
    """
    Remove fragments by keeping only the largest connected component
    """
    labeled_array, num_features = ndimage_label(mask)
    
    if num_features <= 1:
        return mask
    
    # Find largest component by volume
    sizes = np.array([np.sum(labeled_array == i) for i in range(1, num_features + 1)])
    largest_component_label = np.argmax(sizes) + 1
    
    # Keep only largest
    cleaned = (labeled_array == largest_component_label).astype(np.uint8)
    
    return cleaned


def smooth_mask(mask, sigma=1.5):
    """
    Apply Gaussian smoothing to reduce surface irregularities
    """
    # Convert to float for smoothing
    smoothed = gaussian_filter(mask.astype(float), sigma=sigma)
    
    # Re-threshold at 0.5 to get binary mask
    smoothed = (smoothed > 0.5).astype(np.uint8)
    
    return smoothed


def process_single_vertebra_mask(mask):
    """
    Complete 4-phase post-processing pipeline for a single vertebra mask
    """
    original_volume = np.sum(mask)
    
    # Phase 1: Morphological cleaning
    cleaned = morphological_clean(mask, closing_size=3, opening_size=2)
    
    # Phase 2: Keep largest component
    cleaned = keep_largest_component(cleaned)
    
    # Phase 3: Gaussian smoothing
    cleaned = smooth_mask(cleaned, sigma=1.5)
    
    # Phase 4: Re-apply largest component after smoothing
    cleaned = keep_largest_component(cleaned)
    
    # Calculate statistics
    final_volume = np.sum(cleaned)
    labeled_array, num_components = ndimage_label(cleaned)
    
    stats = {
        'original_volume': int(original_volume),
        'final_volume': int(final_volume),
        'volume_change': int(final_volume - original_volume),
        'num_components': int(num_components)
    }
    
    return cleaned, stats


def process_combined_labels(labels):
    """
    Process combined labels file containing multiple vertebrae
    """
    unique_labels = sorted(set(np.unique(labels)) - {0})
    cleaned_labels = np.zeros_like(labels)
    all_stats = {}
    
    print(f"      Found {len(unique_labels)} unique labels: {unique_labels}")
    
    for label_value in unique_labels:
        # Extract mask for this label
        mask = (labels == label_value).astype(np.uint8)
        
        # Process this vertebra
        cleaned_mask, stats = process_single_vertebra_mask(mask)
        
        # Store back with original label value
        cleaned_labels[cleaned_mask == 1] = label_value
        all_stats[f"label_{label_value}"] = stats
    
    return cleaned_labels, all_stats


def process_single_vertebra_file(nii_img):
    """
    Process a single vertebra file (binary mask with values 0 and 1)
    """
    data = nii_img.get_fdata()
    
    # Convert to binary (in case values are not exactly 0 and 1)
    mask = (data > 0).astype(np.uint8)
    
    # Process the mask
    cleaned_mask, stats = process_single_vertebra_mask(mask)
    
    # Create new NIfTI image with cleaned data
    cleaned_nii = nib.Nifti1Image(cleaned_mask, nii_img.affine, nii_img.header)
    
    return cleaned_nii, stats


def process_patient(patient_folder):
    """
    Process all NIfTI files for a single patient
    """
    patient_path = Path(patient_folder)
    
    if not patient_path.exists():
        print(f"❌ Error: Patient folder not found: {patient_path}")
        return False
    
    # Create output folder
    output_folder = Path(f"{patient_path.name}_post_processed")
    output_folder.mkdir(exist_ok=True)
    
    # Create segmentations subfolder
    output_seg_folder = output_folder / "segmentations"
    output_seg_folder.mkdir(exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"Processing Patient: {patient_path.name}")
    print(f"{'='*70}")
    print(f"Input:  {patient_path}")
    print(f"Output: {output_folder}")
    print(f"{'='*70}\n")
    
    combined_file = patient_path / "combined_labels.nii.gz"
    
    if combined_file.exists():
        print(f"[1/25] Processing: combined_labels.nii.gz")
        start_time = time.time()
        
        try:
            # Load NIfTI file
            nii_img = nib.load(combined_file)
            labels = nii_img.get_fdata().astype(np.uint8)
            
            print(f"      Shape: {labels.shape}")
            
            # Process combined labels
            cleaned_labels, all_stats = process_combined_labels(labels)
            
            # Save processed file
            output_file = output_folder / "combined_labels.nii.gz"
            cleaned_nii = nib.Nifti1Image(cleaned_labels, nii_img.affine, nii_img.header)
            nib.save(cleaned_nii, output_file)
            
            elapsed = time.time() - start_time
            print(f"      ✓ Saved to: {output_file.name}")
            print(f"      Time: {elapsed:.2f}s\n")
            
        except Exception as e:
            print(f"      ❌ Error: {e}\n")
    else:
        print(f"[1/25] ⚠️ Warning: combined_labels.nii.gz not found\n")
    seg_folder = patient_path / "segmentations"
    
    if not seg_folder.exists():
        print(f"❌ Error: segmentations folder not found: {seg_folder}")
        return False
    
    # Get all .nii.gz files
    nii_files = sorted(seg_folder.glob("*.nii.gz"))
    
    if len(nii_files) == 0:
        print(f"❌ Error: No .nii.gz files found in segmentations folder")
        return False
    
    print(f"Found {len(nii_files)} vertebrae files in segmentations/\n")
    
    # Process each file
    for idx, nii_file in enumerate(nii_files, start=2):
        print(f"[{idx}/25] Processing: segmentations/{nii_file.name}")
        start_time = time.time()
        
        try:
            # Load NIfTI file
            nii_img = nib.load(nii_file)
            
            # Process single vertebra
            cleaned_nii, stats = process_single_vertebra_file(nii_img)
            
            # Save processed file
            output_file = output_seg_folder / nii_file.name
            nib.save(cleaned_nii, output_file)
            
            elapsed = time.time() - start_time
            print(f"      Volume: {stats['original_volume']:,} → {stats['final_volume']:,} voxels")
            print(f"      Components: {stats['num_components']}")
            print(f"      ✓ Saved to: segmentations/{output_file.name}")
            print(f"      Time: {elapsed:.2f}s\n")
            
        except Exception as e:
            print(f"      ❌ Error: {e}\n")
    
    print(f"{'='*70}")
    print(f"✓ Patient {patient_path.name} completed!")
    print(f"{'='*70}\n")
    
    return True


# ══════════════════════════════════════════════════════════════════════════
# MAIN FUNCTION
# ══════════════════════════════════════════════════════════════════════════

def main():
    """
    Main function to process multiple patients
    """
    if len(sys.argv) < 2:
        print("Usage: python postprocessing_vertebrae.py PATIENT1 PATIENT2 ...")
        print("\nExample:")
        print("  python postprocessing_vertebrae.py BDMAP_00000006 BDMAP_00000031")
        print("\nThis will create:")
        print("  - BDMAP_00000006_post_processed/")
        print("  - BDMAP_00000031_post_processed/")
        sys.exit(1)
    
    patient_folders = sys.argv[1:]
    
    print("\n" + "="*70)
    print("VERTEBRAE SEGMENTATION POST-PROCESSING PIPELINE")
    print("="*70)
    print(f"\nPatients to process: {len(patient_folders)}")
    for pf in patient_folders:
        print(f"  - {pf}")
    print("\n" + "="*70)
    
    # Process each patient
    overall_start = time.time()
    success_count = 0
    
    for patient_folder in patient_folders:
        try:
            success = process_patient(patient_folder)
            if success:
                success_count += 1
        except Exception as e:
            print(f"\n❌ Fatal error processing {patient_folder}: {e}\n")
            import traceback
            traceback.print_exc()
    
    overall_elapsed = time.time() - overall_start
    
    # Final summary
    print("\n" + "="*70)
    print("PROCESSING COMPLETE")
    print("="*70)
    print(f"Patients processed successfully: {success_count}/{len(patient_folders)}")
    print(f"Total time: {overall_elapsed:.2f}s")
    print(f"Average time per patient: {overall_elapsed/len(patient_folders):.2f}s")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
