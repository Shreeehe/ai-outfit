# classifier.py - Fast CLIP-based Clothing Classifier
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from sklearn.cluster import KMeans
import numpy as np

class ClothingClassifier:
    def __init__(self, use_gpu=True):
        print("Loading CLIP model...")
        
        # Use GPU if available
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # Set to eval mode for faster inference
        self.model.eval()
        
        print("CLIP model loaded!")
        
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
    
    def _resize_image(self, image, max_size=512):
        """Resize image for faster processing"""
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.LANCZOS)
        return image
    
    def classify_full(self, image_path):
        """Full classification with validation"""
        try:
            # Load and resize image for speed
            image = Image.open(image_path).convert('RGB')
            image = self._resize_image(image, max_size=384)  # Smaller = faster
            
            # Quick clothing detection + type classification in one pass
            with torch.no_grad():
                # Classify clothing type
                clothing_type, type_conf = self._classify(image, self.clothing_types)
                
                # If very low confidence, might not be clothing
                if type_conf < 0.15:
                    return {
                        'success': False,
                        'error': 'not_clothing',
                        'message': 'Could not detect clothing in image',
                        'confidence': type_conf
                    }
                
                # Get other attributes in parallel-ish (still sequential but fast)
                formality, _ = self._classify(image, list(self.formality_levels.keys()))
                formality = self.formality_levels[formality]
                
                pattern, _ = self._classify(image, list(self.patterns.keys()))
                pattern = self.patterns[pattern]
                
                season, _ = self._classify(image, list(self.seasons.keys()))
                season = self.seasons[season]
            
            # Extract colors (fast, no GPU needed)
            colors = self._extract_colors(image)
            
            print(f"Detected: {clothing_type} ({type_conf:.2f})")
            
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
            
        except Exception as e:
            print(f"Classification error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': 'classification_error',
                'message': str(e),
                'confidence': 0
            }
    
    def _classify(self, image, labels):
        """Classify image against a list of labels - GPU accelerated"""
        text_labels = [f"a photo of {label}" for label in labels]
        
        inputs = self.processor(
            text=text_labels,
            images=image,
            return_tensors="pt",
            padding=True
        )
        
        # Move to GPU
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        best_idx = probs.argmax().item()
        confidence = probs[best_idx].item()
        
        return labels[best_idx], confidence
    
    def _extract_colors(self, image):
        """Extract dominant colors using K-means - CPU is fine"""
        # Resize for speed
        small_img = image.resize((50, 50))
        pixels = np.array(small_img).reshape(-1, 3)
        
        # Filter out very light and very dark pixels
        mask = (pixels.sum(axis=1) > 30) & (pixels.sum(axis=1) < 730)
        filtered_pixels = pixels[mask]
        
        if len(filtered_pixels) < 2:
            return ['#808080', '#808080']
        
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        kmeans.fit(filtered_pixels)
        
        colors = kmeans.cluster_centers_.astype(int)
        hex_colors = ['#{:02x}{:02x}{:02x}'.format(r, g, b) for r, g, b in colors]
        
        return hex_colors


# Test
if __name__ == "__main__":
    classifier = ClothingClassifier()
    print("Classifier ready for testing!")
