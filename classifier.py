# classifier.py - Clothing Classifier using TinyCLIP (Lightweight)
"""
Uses TinyCLIP for faster, smaller model (~50MB vs 350MB for CLIP)
Suitable for cloud deployment and mobile devices
"""

from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

class ClothingClassifier:
    def __init__(self):
        print("Loading TinyCLIP model (lightweight)...")
        # TinyCLIP - much smaller than regular CLIP
        model_name = "wkcn/TinyCLIP-ViT-39M-16-Text-19M-YFCC15M"
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        
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
    
    def is_clothing(self, image_path, threshold=0.5):
        """
        First check: Is this actually clothing?
        Returns: (is_clothing: bool, confidence: float, detected_category: str)
        """
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
    
    def classify_full(self, image_path, min_confidence=0.3):
        """
        Full classification with validation
        Returns: dict with results or error
        """
        # STEP 1: Check if it's clothing
        is_clothing, clothing_conf, detected = self.is_clothing(image_path)
        
        if not is_clothing:
            return {
                'success': False,
                'error': 'not_clothing',
                'message': f'This looks like {detected}, not clothing!',
                'confidence': clothing_conf
            }
        
        # STEP 2: Classify clothing details
        image = Image.open(image_path).convert('RGB')
        
        # Get clothing type
        clothing_type, type_conf = self._classify(image, self.clothing_types)
        
        # Get other attributes
        formality, _ = self._classify(image, list(self.formality_levels.keys()))
        formality = self.formality_levels[formality]
        
        pattern, _ = self._classify(image, list(self.patterns.keys()))
        pattern = self.patterns[pattern]
        
        season, _ = self._classify(image, list(self.seasons.keys()))
        season = self.seasons[season]
        
        # Extract colors
        colors = self._extract_colors(image_path)
        
        return {
            'success': True,
            'clothing_type': clothing_type,
            'type_confidence': type_conf,
            'formality': formality,
            'pattern': pattern,
            'season': season,
            'color_primary': colors[0],
            'color_secondary': colors[1] if len(colors) > 1 else colors[0]
        }
    
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
        from sklearn.cluster import KMeans
        import numpy as np
        
        image = Image.open(image_path).convert('RGB')
        image = image.resize((100, 100))
        
        pixels = np.array(image).reshape(-1, 3)
        
        # Filter out very dark/light pixels
        mask = (pixels.sum(axis=1) > 30) & (pixels.sum(axis=1) < 730)
        pixels = pixels[mask] if mask.sum() > 10 else pixels
        
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        colors = kmeans.cluster_centers_.astype(int)
        hex_colors = ['#{:02x}{:02x}{:02x}'.format(r, g, b) 
                     for r, g, b in colors]
        
        return hex_colors


# Test
if __name__ == "__main__":
    classifier = ClothingClassifier()
    result = classifier.classify_full("test_image.jpg")
    print(result)