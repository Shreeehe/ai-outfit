# routers/classify.py - Classification API
from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
from datetime import datetime
from PIL import Image

router = APIRouter(prefix="/api", tags=["classification"])

# Get paths relative to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "wardrobe_images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Add project root to path for imports
import sys
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Mapping from raw clothing types to categories
TYPE_MAP = {
    't-shirt': 'top', 'shirt': 'top', 'blouse': 'top', 'sweater': 'top', 
    'hoodie': 'top', 'polo shirt': 'top', 'tank top': 'top',
    'jeans': 'bottom', 'trousers': 'bottom', 'pants': 'bottom', 
    'shorts': 'bottom', 'skirt': 'bottom',
    'dress': 'dress', 'jumpsuit': 'dress',
    'sneakers': 'shoes', 'formal shoes': 'shoes', 'boots': 'shoes', 
    'sandals': 'shoes', 'slippers': 'shoes',
    'jacket': 'outerwear', 'coat': 'outerwear', 'blazer': 'outerwear', 
    'cardigan': 'outerwear'
}

# Lazy load classifier to avoid slow startup
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        try:
            from classifier import ClothingClassifier
            print("Loading CLIP classifier...")
            _classifier = ClothingClassifier()
            print("CLIP classifier loaded successfully!")
        except Exception as e:
            print(f"Failed to load classifier: {e}")
            raise
    return _classifier

@router.post("/classify")
async def classify_image(file: UploadFile = File(...)):
    """Classify uploaded clothing image"""
    temp_path = None
    
    try:
        # Save file with unique name
        filename = f"classify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        temp_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save uploaded file properly
        contents = await file.read()
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        print(f"Saved image to: {temp_path}")
        print(f"File exists: {os.path.exists(temp_path)}")
        print(f"File size: {os.path.getsize(temp_path)} bytes")
        
        # Verify it's a valid image
        try:
            img = Image.open(temp_path)
            img.verify()
            print(f"Image valid: {img.format} {img.size}")
        except Exception as img_err:
            print(f"Image validation failed: {img_err}")
            return {
                "success": False,
                "message": f"Invalid image file: {str(img_err)}",
                "clothing_type": "top"
            }
        
        # Get classifier and classify
        try:
            classifier = get_classifier()
        except Exception as clf_err:
            print(f"Classifier load error: {clf_err}")
            return {
                "success": False,
                "message": "AI classifier not available",
                "clothing_type": "top"
            }
        
        print("Running classification...")
        result = classifier.classify_full(temp_path)
        print(f"Classification result: {result}")
        
        if result.get('success'):
            raw_type = result.get('clothing_type', 'unknown').lower()
            category = TYPE_MAP.get(raw_type, 'top')
            
            print(f"Raw type: {raw_type} -> Category: {category}")
            
            return {
                "success": True,
                "clothing_type": category,
                "color_primary": result.get('color_primary', '#000000'),
                "color_secondary": result.get('color_secondary'),
                "pattern": result.get('pattern', 'solid'),
                "formality": result.get('formality', 'casual'),
                "season_weight": result.get('season', 'medium'),
                "confidence": result.get('type_confidence'),
                "message": f"Detected: {raw_type}"
            }
        else:
            print(f"Classification failed: {result.get('message')}")
            return {
                "success": False,
                "message": result.get('message', 'Classification failed'),
                "confidence": result.get('confidence'),
                "clothing_type": "top"
            }
    
    except Exception as e:
        print(f"Classification error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": str(e),
            "clothing_type": "top"
        }
    
    finally:
        # Clean up temp file after classification is complete
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
