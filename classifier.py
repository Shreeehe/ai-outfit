# classifier.py - Clothing Classifier (Cloud-Compatible with Fallback)
"""
Uses TinyCLIP when available, falls back to manual mode on cloud
"""

from PIL import Image

# Try to import transformers - may fail on Python 3.13
CLIP_AVAILABLE = False
try:
    from transformers import CLIPProcessor, CLIPModel
    import torch
    CLIP_AVAILABLE = True
except Exception as e:
    print(f"⚠️ CLIP not available: {e}")
    print("Running in MANUAL mode - no AI classification")

class ClothingClassifier:
    def __init__(self):
        self.ai_enabled = False
        
        if CLIP_AVAILABLE:
            try:
                print("Loading TinyCLIP model...")
                model_name = "wkcn/TinyCLIP-ViT-39M-16-Text-19M-YFCC15M"
                self.model = CLIPModel.from_pretrained(model_name)
                self.processor = CLIPProcessor.from_pretrained(model_name)
                self.ai_enabled = True
                print("✅ AI classification enabled")
            except Exception as e:
                print(f"⚠️ Failed to load model: {e}")
        else:
            print("📝 Manual classification mode")
        
        self.clothing_types = [
            "t-shirt", "shirt", "blouse", "sweater", "hoodie",
            "jeans", "trousers", "pants", "shorts", "skirt",
            "dress", "jumpsuit",
            "sneakers", "formal shoes", "boots", "sandals", "slippers",
            "jacket", "coat", "blazer", "cardigan"
        ]
        
        self.formality_levels = {
            "casual clothing": "casual",
            "business casual outfit": "business-casual",
            "formal attire": "formal",
            "athletic wear": "athletic"
        }
        
        self.patterns = {
            "solid colored": "solid",
            "striped": "striped",
            "checkered": "checkered",
            "floral print": "floral",
            "graphic print": "printed"
        }
        
        self.seasons = {
            "lightweight summer clothing": "light",
            "medium weight clothing": "medium",
            "heavy winter clothing": "heavy"
        }
    
    def classify_full(self, image_path, min_confidence=0.3):
        """
        Full classification - uses AI if available, otherwise returns defaults
        """
        if not self.ai_enabled:
            # Return default values for manual correction
            colors = self._extract_colors(image_path)
            return {
                'success': True,
                'ai_enabled': False,
                'clothing_type': 'top',  # Default
                'type_confidence': 0,
                'formality': 'casual',
                'pattern': 'solid',
                'season': 'medium',
                'color_primary': colors[0],
                'color_secondary': colors[1] if len(colors) > 1 else colors[0],
                'message': 'AI not available - please select type manually'
            }
        
        # AI classification
        try:
            # Check if it's clothing
            is_clothing, clothing_conf, detected = self.is_clothing(image_path)
            
            if not is_clothing:
                return {
                    'success': False,
                    'ai_enabled': True,
                    'error': 'not_clothing',
                    'message': f'This looks like {detected}, not clothing!',
                    'confidence': clothing_conf
                }
            
            # Classify clothing details
            image = Image.open(image_path).convert('RGB')
            
            clothing_type, type_conf = self._classify(image, self.clothing_types)
            
            formality, _ = self._classify(image, list(self.formality_levels.keys()))
            formality = self.formality_levels[formality]
            
            pattern, _ = self._classify(image, list(self.patterns.keys()))
            pattern = self.patterns[pattern]
            
            season, _ = self._classify(image, list(self.seasons.keys()))
            season = self.seasons[season]
            
            colors = self._extract_colors(image_path)
            
            return {
                'success': True,
                'ai_enabled': True,
                'clothing_type': clothing_type,
                'type_confidence': type_conf,
                'formality': formality,
                'pattern': pattern,
                'season': season,
                'color_primary': colors[0],
                'color_secondary': colors[1] if len(colors) > 1 else colors[0]
            }
        except Exception as e:
            colors = self._extract_colors(image_path)
            return {
                'success': True,
                'ai_enabled': False,
                'clothing_type': 'top',
                'formality': 'casual',
                'pattern': 'solid',
                'season': 'medium',
                'color_primary': colors[0],
                'color_secondary': colors[1] if len(colors) > 1 else colors[0],
                'message': f'AI error: {e} - please select type manually'
            }
    
    def is_clothing(self, image_path, threshold=0.5):
        """Check if image contains clothing"""
        if not self.ai_enabled:
            return True, 1.0, "clothing"
            
        image = Image.open(image_path).convert('RGB')
        
        labels = [
            "a photo of clothing",
            "a photo of a person wearing clothes",
            "a photo of an object",
            "a photo of furniture",
            "a photo of food",
            "a photo of an animal"
        ]
        
        inputs = self.processor(
            text=labels,
            images=image,
            return_tensors="pt",
            padding=True
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        best_idx = probs.argmax().item()
        best_conf = probs[best_idx].item()
        best_label = labels[best_idx]
        
        is_clothing_item = best_idx in [0, 1]
        
        return is_clothing_item, best_conf, best_label
    
    def _classify(self, image, labels):
        """Helper to classify against a list of labels"""
        text_labels = [f"a photo of {label}" for label in labels]
        
        inputs = self.processor(
            text=text_labels,
            images=image,
            return_tensors="pt",
            padding=True
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        best_idx = probs.argmax().item()
        confidence = probs[best_idx].item()
        
        return labels[best_idx], confidence
    
    def _extract_colors(self, image_path):
        """Extract dominant colors using K-means"""
        try:
            from sklearn.cluster import KMeans
            import numpy as np
            
            image = Image.open(image_path).convert('RGB')
            image = image.resize((100, 100))
            
            pixels = np.array(image).reshape(-1, 3)
            
            mask = (pixels.sum(axis=1) > 30) & (pixels.sum(axis=1) < 730)
            pixels = pixels[mask] if mask.sum() > 10 else pixels
            
            kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            colors = kmeans.cluster_centers_.astype(int)
            hex_colors = ['#{:02x}{:02x}{:02x}'.format(r, g, b) 
                         for r, g, b in colors]
            
            return hex_colors
        except Exception:
            return ['#000000', '#ffffff']