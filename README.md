# arw2jpg

Simple CLI tool to convert Sony ARW raw files to high-quality JPEGs.

## Installation

```bash
pip install rawpy Pillow
```

Or with uv:

```bash
uv pip install rawpy Pillow
```

## Usage

```bash
# Convert all ARW files in a directory (outputs to input_dir/jpegs/)
python arw2jpg.py /path/to/arw/files

# Specify output directory
python arw2jpg.py /path/to/arw/files -o /path/to/output

# Adjust quality (1-100, default: 100)
python arw2jpg.py /path/to/arw/files -q 95

# Control parallelism
python arw2jpg.py /path/to/arw/files -w 8
```

## Options

| Option | Description |
|--------|-------------|
| `input` | Input directory containing ARW files |
| `-o, --output` | Output directory (default: `input/jpegs`) |
| `-q, --quality` | JPEG quality 1-100 (default: 100) |
| `-w, --workers` | Parallel workers (default: min(4, CPU count)) |

## Quality Settings

- AHD demosaicing algorithm
- Camera white balance preserved
- 4:4:4 chroma subsampling (no color loss)
- Optimized Huffman tables
- Light noise reduction

## License

MIT
