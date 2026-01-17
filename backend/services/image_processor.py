# services/image_processor.py - Image processing utilities
from PIL import Image
import os
from io import BytesIO

def remove_background_and_crop(image_path, output_path=None):
    """
    Remove background from clothing image and auto-crop to content.
    
    Args:
        image_path: Path to input image
        output_path: Optional output path. If None, overwrites input.
    
    Returns:
        Path to processed image
    """
    try:
        from rembg import remove
        
        # Read image
        with open(image_path, 'rb') as f:
            input_data = f.read()
        
        print(f"Processing image: {image_path}")
        
        # Remove background
        output_data = remove(input_data)
        
        # Open as PIL Image
        img = Image.open(BytesIO(output_data)).convert('RGBA')
        
        # Get bounding box of non-transparent content
        bbox = img.getbbox()
        
        if bbox:
            # Add some padding
            padding = 10
            left = max(0, bbox[0] - padding)
            top = max(0, bbox[1] - padding)
            right = min(img.width, bbox[2] + padding)
            bottom = min(img.height, bbox[3] + padding)
            
            # Crop to content
            img = img.crop((left, top, right, bottom))
        
        # Create white background
        background = Image.new('RGB', img.size, (255, 255, 255))
        
        # Paste using alpha as mask
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[3])
        else:
            background.paste(img)
        
        # Save
        save_path = output_path or image_path
        background.save(save_path, 'JPEG', quality=95)
        
        print(f"Saved processed image: {save_path}")
        return save_path
        
    except Exception as e:
        print(f"Background removal failed: {e}")
        import traceback
        traceback.print_exc()
        # Return original path if processing fails
        return image_path


def resize_image(image_path, max_size=800):
    """Resize image if too large"""
    try:
        img = Image.open(image_path)
        
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            img.save(image_path, quality=95)
            print(f"Resized image to {new_size}")
        
        return image_path
    except Exception as e:
        print(f"Resize failed: {e}")
        return image_path
