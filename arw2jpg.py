#!/usr/bin/env python3
"""
arw2jpg - Convert Sony ARW files to high-quality JPEGs.

Uses rawpy for RAW processing with high-quality demosaicing and Pillow for 
JPEG encoding with maximum quality settings (no chroma subsampling).
"""

import argparse
import os
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

try:
    import rawpy
except ImportError:
    print("Error: rawpy not found. Install with: pip install rawpy")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow not found. Install with: pip install Pillow")
    sys.exit(1)


def convert_arw_to_jpeg(arw_path: Path, output_dir: Path, quality: int) -> tuple[str, bool, str]:
    """Convert a single ARW file to JPEG."""
    try:
        output_path = output_dir / f"{arw_path.stem}.jpg"
        
        with rawpy.imread(str(arw_path)) as raw:
            rgb = raw.postprocess(
                use_camera_wb=True,
                use_auto_wb=False,
                half_size=False,
                no_auto_bright=False,
                output_bps=8,
                demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,
                output_color=rawpy.ColorSpace.sRGB,
                dcb_enhance=True,
                fbdd_noise_reduction=rawpy.FBDDNoiseReductionMode.Light,
            )
        
        img = Image.fromarray(rgb)
        img.save(
            output_path,
            "JPEG",
            quality=quality,
            subsampling=0,
            optimize=True,
        )
        
        return (arw_path.name, True, output_path.name)
    except Exception as e:
        return (arw_path.name, False, str(e))


def main():
    parser = argparse.ArgumentParser(
        prog="arw2jpg",
        description="Convert Sony ARW files to high-quality JPEGs",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input directory containing ARW files",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output directory for JPEGs (default: input_dir/jpegs)",
    )
    parser.add_argument(
        "-q", "--quality",
        type=int,
        default=100,
        choices=range(1, 101),
        metavar="1-100",
        help="JPEG quality (default: 100)",
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=None,
        help="Number of parallel workers (default: CPU count, max 4)",
    )
    
    args = parser.parse_args()
    
    input_dir = args.input.resolve()
    if not input_dir.is_dir():
        print(f"Error: {input_dir} is not a directory")
        sys.exit(1)
    
    output_dir = (args.output or input_dir / "jpegs").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    arw_files = list(input_dir.glob("*.ARW")) + list(input_dir.glob("*.arw"))
    if not arw_files:
        print(f"No ARW files found in {input_dir}")
        sys.exit(1)
    
    max_workers = args.workers or min(4, os.cpu_count() or 1)
    
    print(f"Input:   {input_dir}")
    print(f"Output:  {output_dir}")
    print(f"Files:   {len(arw_files)}")
    print(f"Quality: {args.quality}")
    print(f"Workers: {max_workers}")
    print("-" * 50)
    
    successful = 0
    failed = 0
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(convert_arw_to_jpeg, f, output_dir, args.quality): f
            for f in arw_files
        }
        
        for future in as_completed(futures):
            filename, success, message = future.result()
            if success:
                successful += 1
                print(f"✓ {filename} -> {message}")
            else:
                failed += 1
                print(f"✗ {filename}: {message}")
    
    print("-" * 50)
    print(f"Done: {successful} converted, {failed} failed")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
