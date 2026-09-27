"""
Script to package the Chrome Extension as a ZIP file for download.
Run this script to create/update the extension ZIP in static/downloads/
"""

import os
import zipfile
import shutil
from pathlib import Path
import base64

def create_simple_icon(size):
    """
    Create a simple PNG icon of the specified size.
    Returns bytes of a valid PNG image with purple background and white "K".
    """
    # This is a valid PNG image data structure
    # We'll create a simple solid color PNG for each size
    # Using a base64 encoded minimal PNG and scaling concept
    
    # For each size, we'll create a proper PNG using a template approach
    # Since we can't use PIL easily, we'll use a simple approach:
    # Create a valid PNG with the correct dimensions
    
    # Minimal valid PNG structure for a solid color image
    # Header
    png_header = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk (13 bytes data + 4 byte CRC)
    width = size.to_bytes(4, 'big')
    height = size.to_bytes(4, 'big')
    ihdr_data = (
        width + height +  # width, height
        b'\x08\x02' +  # bit depth 8, color type 2 (RGB)
        b'\x00\x00\x00'  # compression, filter, interlace
    )
    ihdr_crc = b'\x00\x00\x00\x00'  # Placeholder CRC (we'll calculate properly)
    ihdr_chunk = b'IHDR' + ihdr_data + ihdr_crc
    
    # IDAT chunk - RGB data (simple purple color: #667eea = RGB(102, 126, 234))
    # Each pixel is 3 bytes (RGB), each row has a filter byte (0 = none)
    row_size = size * 3 + 1  # width * 3 bytes + 1 filter byte
    idat_data = b'\x78\x9c'  # zlib header (no compression for simplicity)
    # For simplicity, we'll use a pre-encoded small PNG and let the system handle scaling
    # Actually, let's use a better approach - generate actual PNG bytes
    
    # Simpler approach: Create proper PNG bytes using struct
    import struct
    
    # PNG signature
    png_data = png_header
    
    # IHDR chunk
    ihdr_length = struct.pack('>I', 13)
    ihdr_type = b'IHDR'
    ihdr_content = struct.pack('>II', size, size) + b'\x08\x02\x00\x00\x00'
    ihdr_crc_value = 0xABCDEF01  # Placeholder, will be recalculated if needed
    ihdr_crc_bytes = struct.pack('>I', ihdr_crc_value & 0xFFFFFFFF)
    png_data += ihdr_length + ihdr_type + ihdr_content + ihdr_crc_bytes
    
    # For a proper implementation, we'd need zlib compression for IDAT
    # For now, let's use a working approach: embed a valid small PNG and scale it
    # Actually, the simplest working solution is to create proper PNG files
    
    # Let's use a different approach: create a minimal working PNG
    # We'll create a 1x1 pixel PNG and let Chrome scale it (not ideal but works)
    # Better: use the generate_icons.py script if available, or create proper icons
    
    # For production, we should use proper icon generation
    # For now, let's try to run the generate script or create minimal icons
    
    # Create a valid small PNG programmatically
    # This is a minimal valid 16x16 PNG (purple background)
    # We'll generate proper PNG data
    try:
        # Try to use PIL if available
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (size, size), color=(102, 126, 234))
        draw = ImageDraw.Draw(img)
        
        # Draw border
        border_color = (118, 75, 162)
        draw.rectangle([0, 0, size-1, size-1], outline=border_color, width=max(1, size//16))
        
        # Draw "K" letter
        try:
            font_size = int(size * 0.6)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        text = "K"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size - text_width) // 2, (size - text_height) // 2 - bbox[1])
        draw.text(position, text, fill=(255, 255, 255), font=font)
        
        import io
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    except ImportError:
        # PIL not available, create a minimal valid PNG using base64
        # This is a valid 1x1 purple PNG (will be scaled by browser)
        minimal_png = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGA60e6kgAAAABJRU5ErkJggg=='
        )
        # For proper icons, we'd need to generate actual sized PNGs
        # But this minimal PNG will at least prevent the error
        return minimal_png

def ensure_icons_exist(extension_dir):
    """Ensure icon files exist, create them if they don't"""
    icons_dir = extension_dir / "icons"
    icons_dir.mkdir(exist_ok=True)
    
    sizes = [16, 48, 128]
    all_exist = all((icons_dir / f"icon{size}.png").exists() for size in sizes)
    
    if not all_exist:
        print("Icons not found, generating them...")
        try:
            # Try to run the generate_icons.py script
            import subprocess
            import sys
            script_path = extension_dir / "generate_icons.py"
            if script_path.exists():
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    cwd=str(extension_dir),
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print("Icons generated successfully using generate_icons.py")
                    return
                else:
                    print(f"generate_icons.py failed: {result.stderr}")
        except Exception as e:
            print(f"Could not run generate_icons.py: {e}")
        
        # Fallback: create simple icons
        print("Creating simple placeholder icons...")
        for size in sizes:
            icon_path = icons_dir / f"icon{size}.png"
            if not icon_path.exists():
                icon_data = create_simple_icon(size)
                icon_path.write_bytes(icon_data)
                print(f"  Created icon{size}.png")

def package_extension():
    """Package the Chrome Extension into a ZIP file"""
    
    # Paths
    project_root = Path(__file__).parent.parent
    extension_dir = project_root / "chrome_extension"
    output_dir = project_root / "backend" / "static" / "downloads"
    zip_path = output_dir / "kyron-extension.zip"
    
    # Ensure icons exist before packaging
    ensure_icons_exist(extension_dir)
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Files to include (exclude unnecessary files)
    exclude_files = {
        'README.md',
        'CHROME_EXTENSION_SETUP.md',
        'create_icons.ps1',
        'generate_icons.py',
        '__pycache__',
        '.git',
        '.gitignore'
    }
    
    exclude_extensions = {'.pyc', '.py', '.ps1', '.md'}
    
    # Include icons directory if it exists
    include_dirs = {'icons'}
    
    print("Packaging Chrome Extension...")
    print(f"Source: {extension_dir}")
    print(f"Output: {zip_path}")
    
    # Remove old ZIP if exists
    if zip_path.exists():
        zip_path.unlink()
        print("Removed old ZIP file")
    
    # Create ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through extension directory
        for root, dirs, files in os.walk(extension_dir):
            # Filter out excluded directories (but keep include_dirs)
            dirs[:] = [d for d in dirs if d not in exclude_files or d in include_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip excluded files
                if file in exclude_files or file_path.suffix in exclude_extensions:
                    continue
                
                # Get relative path for ZIP
                rel_path = file_path.relative_to(extension_dir)
                
                # Add file to ZIP
                zipf.write(file_path, rel_path)
                print(f"  Added: {rel_path}")
    
    # Get file size
    file_size = zip_path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"\n[SUCCESS] Extension packaged successfully!")
    print(f"  File: {zip_path}")
    print(f"  Size: {file_size_mb:.2f} MB ({file_size:,} bytes)")
    
    return zip_path

if __name__ == "__main__":
    try:
        package_extension()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

