"""
Verify Difference Data Calculation
Check if the difference meshes are being calculated correctly
"""

import nibabel as nib
import numpy as np
from pathlib import Path

def verify_difference_for_patient(patient_id):
    """
    Verify that difference calculation is correct
    """
    print(f"\n{'='*70}")
    print(f"Verifying Difference Data for: {patient_id}")
    print(f"{'='*70}")
    
    # Load both raw and cleaned
    raw_file = f"{patient_id}/combined_labels.nii.gz"
    cleaned_file = f"{patient_id}/combined_labels_CLEANED.nii.gz"
    
    print(f"\n📂 Loading files:")
    print(f"   Raw:     {raw_file}")
    print(f"   Cleaned: {cleaned_file}")
    
    raw_img = nib.load(raw_file)
    cleaned_img = nib.load(cleaned_file)
    
    raw_data = raw_img.get_fdata()
    cleaned_data = cleaned_img.get_fdata()
    
    print(f"\n✅ Loaded:")
    print(f"   Raw shape:     {raw_data.shape}")
    print(f"   Cleaned shape: {cleaned_data.shape}")
    print(f"   Shapes match:  {raw_data.shape == cleaned_data.shape}")
    
    # Check each vertebra
    print(f"\n{'='*70}")
    print(f"Analyzing Difference for Each Vertebra")
    print(f"{'='*70}")
    print(f"{'Vertebra':<10} {'Raw':<10} {'Cleaned':<10} {'Removed':<10} {'Added':<10} {'% Change':<10}")
    print(f"{'-'*70}")
    
    vertebrae_names = {
        1: 'C1', 2: 'C2', 3: 'C3', 4: 'C4', 5: 'C5', 6: 'C6', 7: 'C7',
        8: 'T1', 9: 'T2', 10: 'T3', 11: 'T4', 12: 'T5', 13: 'T6',
        14: 'T7', 15: 'T8', 16: 'T9', 17: 'T10', 18: 'T11', 19: 'T12',
        20: 'L1', 21: 'L2', 22: 'L3', 23: 'L4', 24: 'L5'
    }
    
    total_raw = 0
    total_cleaned = 0
    total_removed = 0
    total_added = 0
    
    for label_num in sorted(vertebrae_names.keys()):
        name = vertebrae_names[label_num]
        
        # Extract masks
        raw_mask = (raw_data == label_num)
        cleaned_mask = (cleaned_data == label_num)
        
        # Count voxels
        raw_count = raw_mask.sum()
        cleaned_count = cleaned_mask.sum()
        
        # Calculate differences
        removed_voxels = ((raw_mask) & (~cleaned_mask)).sum()
        added_voxels = ((cleaned_mask) & (~raw_mask)).sum()
        
        # Calculate percentage change
        if raw_count > 0:
            pct_change = ((cleaned_count - raw_count) / raw_count) * 100
        else:
            pct_change = 0
        
        total_raw += raw_count
        total_cleaned += cleaned_count
        total_removed += removed_voxels
        total_added += added_voxels
        
        print(f"{name:<10} {int(raw_count):<10} {int(cleaned_count):<10} {int(removed_voxels):<10} {int(added_voxels):<10} {pct_change:>6.1f}%")
    
    print(f"{'-'*70}")
    print(f"{'TOTAL':<10} {int(total_raw):<10} {int(total_cleaned):<10} {int(total_removed):<10} {int(total_added):<10}")
    
    # Overall statistics
    print(f"\n{'='*70}")
    print(f"Overall Statistics")
    print(f"{'='*70}")
    print(f"Total voxels removed:     {int(total_removed):,} ({100*total_removed/total_raw:.2f}% of raw)")
    print(f"Total voxels added:       {int(total_added):,} ({100*total_added/total_cleaned:.2f}% of cleaned)")
    print(f"Net change:               {int(total_cleaned - total_raw):,} voxels")
    print(f"Overall change:           {100*(total_cleaned - total_raw)/total_raw:.2f}%")
    
    # Sanity checks
    print(f"\n{'='*70}")
    print(f"Sanity Checks")
    print(f"{'='*70}")
    
    # Check 1: Removed + Added should explain the difference
    expected_cleaned = total_raw - total_removed + total_added
    check1 = (expected_cleaned == total_cleaned)
    print(f"✓ Removed/Added math correct: {check1}")
    if not check1:
        print(f"  Expected: {expected_cleaned:,}, Got: {int(total_cleaned):,}")
    
    # Check 2: If post-processing only removes (no hole filling), added should be small
    if total_added > total_removed * 0.5:
        print(f"⚠️ WARNING: Added voxels ({total_added:,}) are more than 50% of removed ({total_removed:,})")
        print(f"   This suggests significant hole-filling or reconstruction, not just cleaning")
    else:
        print(f"✓ Added voxels ({total_added:,}) << Removed voxels ({total_removed:,}) - Expected for cleaning")
    
    # Check 3: Look at spatial distribution
    print(f"\n{'='*70}")
    print(f"Spatial Analysis")
    print(f"{'='*70}")
    
    # Create difference masks for ALL vertebrae combined
    all_raw_mask = (raw_data > 0)
    all_cleaned_mask = (cleaned_data > 0)
    
    all_removed = (all_raw_mask) & (~all_cleaned_mask)
    all_added = (all_cleaned_mask) & (~all_raw_mask)
    
    print(f"Combined (all vertebrae):")
    print(f"  Raw voxels:     {int(all_raw_mask.sum()):,}")
    print(f"  Cleaned voxels: {int(all_cleaned_mask.sum()):,}")
    print(f"  Removed voxels: {int(all_removed.sum()):,}")
    print(f"  Added voxels:   {int(all_added.sum()):,}")
    
    print(f"\n{'='*70}\n")


def main():
    patients = ['BDMAP_00000006', 'BDMAP_00000031']
    
    for patient_id in patients:
        try:
            verify_difference_for_patient(patient_id)
        except Exception as e:
            print(f"\n❌ Error processing {patient_id}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
