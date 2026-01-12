# recommender.py
import sqlite3
from datetime import datetime
import random

class OutfitRecommender:
    def __init__(self, db_path='wardrobe.db'):
        self.db_path = db_path
    
    def get_suggestions(self, occasion, weather, num_suggestions=4):
        """
        Main function: Generate outfit suggestions
        
        Args:
            occasion: 'gym', 'work', 'casual', 'date', 'home'
            weather: dict with 'temp', 'condition', etc.
            num_suggestions: number of outfits to return
        
        Returns:
            List of (outfit, score) tuples
        """
        # Get all clothes from database
        clothes = self._get_all_clothes()
        
        if len(clothes) < 2:
            return []  # Not enough clothes
        
        # STEP 1: Filter by occasion
        suitable = self._filter_by_occasion(clothes, occasion)
        
        if not suitable['tops'] or not suitable['bottoms']:
            # Check if we have dresses at least
            if not suitable['dresses']:
                return []  # Can't make outfit
        
        # STEP 2: Filter by weather
        suitable = self._filter_by_weather(suitable, weather)
        
        # STEP 3: Create all possible combinations
        all_combos = self._create_combinations(suitable)
        
        if not all_combos:
            return []
        
        # STEP 4: Score each combination
        scored_outfits = self._score_outfits(all_combos, weather, occasion)
        
        # STEP 5: Return top N, ensuring variety
        return self._select_diverse_outfits(scored_outfits, num_suggestions)
    
    def _get_all_clothes(self):
        """Fetch all clothes from database (excluding items in laundry)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Exclude items that are in laundry
        c.execute('SELECT * FROM clothes WHERE in_laundry = 0 OR in_laundry IS NULL')
        clothes = c.fetchall()
        conn.close()
        
        # Convert to list of dicts for easier handling
        clothes_list = []
        for item in clothes:
            clothes_list.append({
                'id': item[0],
                'image_path': item[1],
                'type': item[2],
                'color_primary': item[3],
                'color_secondary': item[4],
                'pattern': item[5],
                'formality': item[6],
                'season': item[7],
                'created_at': item[8],
                'times_worn': item[9] if len(item) > 9 else 0
            })
        
        return clothes_list
    
    def _filter_by_occasion(self, clothes, occasion):
        """Filter clothes suitable for occasion"""
        
        # Define which formality levels work for each occasion
        occasion_rules = {
            'gym': ['athletic', 'casual'],
            'work': ['business', 'business-casual', 'formal'],
            'casual': ['casual', 'business-casual'],
            'date': ['business-casual', 'formal', 'casual'],
            'home': ['casual', 'athletic'],
            'party': ['formal', 'business-casual', 'casual'],
            'formal': ['formal', 'business']
        }
        
        suitable_formality = occasion_rules.get(occasion, ['casual'])
        
        # Separate into categories
        tops = [c for c in clothes 
                if c['type'] == 'top' and c['formality'] in suitable_formality]
        
        bottoms = [c for c in clothes 
                   if c['type'] == 'bottom' and c['formality'] in suitable_formality]
        
        shoes = [c for c in clothes 
                 if c['type'] == 'shoes' and c['formality'] in suitable_formality]
        
        dresses = [c for c in clothes 
                   if c['type'] == 'dress' and c['formality'] in suitable_formality]
        
        outerwear = [c for c in clothes 
                     if c['type'] == 'outerwear' and c['formality'] in suitable_formality]
        
        return {
            'tops': tops,
            'bottoms': bottoms,
            'shoes': shoes,
            'dresses': dresses,
            'outerwear': outerwear
        }
    
    def _filter_by_weather(self, suitable, weather):
        """Filter by weather appropriateness"""
        temp = weather['temp']
        condition = weather['condition']
        
        # Temperature-based filtering
        if temp < 18:  # Cold
            # Remove light items
            suitable['tops'] = [c for c in suitable['tops'] if c['season'] != 'light']
            suitable['bottoms'] = [c for c in suitable['bottoms'] if c['season'] != 'light']
            
        elif temp > 32:  # Hot
            # Remove heavy items
            suitable['tops'] = [c for c in suitable['tops'] if c['season'] != 'heavy']
            suitable['bottoms'] = [c for c in suitable['bottoms'] if c['season'] != 'heavy']
        
        # Rain condition
        if 'Rain' in condition:
            # Prefer closed shoes
            suitable['shoes'] = [c for c in suitable['shoes'] if 'sandal' not in c['image_path'].lower()]
        
        return suitable
    
    def _create_combinations(self, suitable):
        """Create all possible outfit combinations"""
        combos = []
        
        # Regular outfits (top + bottom + shoes)
        for top in suitable['tops']:
            for bottom in suitable['bottoms']:
                # Add with shoes if available
                if suitable['shoes']:
                    for shoe in suitable['shoes']:
                        combos.append({
                            'top': top,
                            'bottom': bottom,
                            'shoes': shoe,
                            'type': 'regular'
                        })
                else:
                    # No shoes in wardrobe
                    combos.append({
                        'top': top,
                        'bottom': bottom,
                        'shoes': None,
                        'type': 'regular'
                    })
        
        # Dress outfits (just dress + shoes)
        for dress in suitable['dresses']:
            if suitable['shoes']:
                for shoe in suitable['shoes']:
                    combos.append({
                        'dress': dress,
                        'shoes': shoe,
                        'type': 'dress'
                    })
            else:
                combos.append({
                    'dress': dress,
                    'shoes': None,
                    'type': 'dress'
                })
        
        return combos
    
    def _score_outfits(self, outfits, weather, occasion):
        """Score each outfit based on multiple factors"""
        scored = []
        
        for outfit in outfits:
            score = 50  # Base score
            
            # Weather match (up to +30 points)
            score += self._score_weather(outfit, weather)
            
            # Color coordination (up to +20 points)
            score += self._score_colors(outfit)
            
            # Variety - not recently worn (up to +20 points)
            score += self._score_variety(outfit)
            
            # Pattern balance (up to +10 points)
            score += self._score_patterns(outfit)
            
            # Random factor for variety (+0 to +10)
            score += random.randint(0, 10)
            
            scored.append((outfit, score))
        
        # Sort by score (highest first)
        return sorted(scored, key=lambda x: x[1], reverse=True)
    
    def _score_weather(self, outfit, weather):
        """Score based on weather appropriateness"""
        score = 0
        temp = weather['temp']
        
        items = []
        if outfit['type'] == 'regular':
            items = [outfit['top'], outfit['bottom']]
        else:  # dress
            items = [outfit['dress']]
        
        for item in items:
            season = item['season']
            
            if temp < 18:  # Cold weather
                if season == 'heavy':
                    score += 15
                elif season == 'medium':
                    score += 8
                else:  # light in cold weather
                    score -= 10
                    
            elif temp > 32:  # Hot weather
                if season == 'light':
                    score += 15
                elif season == 'medium':
                    score += 8
                else:  # heavy in hot weather
                    score -= 10
                    
            else:  # Moderate weather (18-32°C)
                if season == 'medium':
                    score += 10
                else:
                    score += 5
        
        return score
    
    def _score_colors(self, outfit):
        """Score color coordination"""
        score = 0
        
        # Get colors from outfit items
        if outfit['type'] == 'regular':
            top_color = outfit['top']['color_primary']
            bottom_color = outfit['bottom']['color_primary']
        else:
            # Dress outfits always coordinate with themselves
            return 15
        
        top_neutral = self._is_neutral_color(top_color)
        bottom_neutral = self._is_neutral_color(bottom_color)
        
        if top_neutral or bottom_neutral:
            score += 15  # One neutral = safe combo
        
        if top_neutral and bottom_neutral:
            score += 5  # Both neutral = classic
        
        # Same color (monochrome)
        if self._colors_similar(top_color, bottom_color):
            score += 10
        
        # High contrast (light + dark)
        if self._high_contrast(top_color, bottom_color):
            score += 8
        
        return score
    
    def _score_variety(self, outfit):
        """Score based on times worn (less worn = better)"""
        score = 0
        
        items = []
        if outfit['type'] == 'regular':
            items = [outfit['top'], outfit['bottom']]
            if outfit['shoes']:
                items.append(outfit['shoes'])
        else:
            items = [outfit['dress']]
            if outfit['shoes']:
                items.append(outfit['shoes'])
        
        for item in items:
            times_worn = item.get('times_worn', 0) or 0
            
            if times_worn == 0:
                score += 10  # Never worn - bonus!
            elif times_worn < 3:
                score += 5   # Rarely worn
            elif times_worn < 10:
                score += 0   # Normal
            else:
                score -= 5   # Worn a lot
        
        return score
    
    def _score_patterns(self, outfit):
        """Score pattern mixing"""
        score = 0
        
        if outfit['type'] == 'dress':
            return 5  # Dresses are self-contained
        
        top_pattern = outfit['top']['pattern']
        bottom_pattern = outfit['bottom']['pattern']
        
        # Both solid = safe
        if top_pattern == 'solid' and bottom_pattern == 'solid':
            score += 10
        
        # One solid, one pattern = good
        elif top_pattern == 'solid' or bottom_pattern == 'solid':
            score += 8
        
        # Both patterned = risky (small penalty)
        else:
            score -= 5
        
        return score
    
    def _select_diverse_outfits(self, scored_outfits, num):
        """Select top N outfits ensuring diversity"""
        if len(scored_outfits) <= num:
            return scored_outfits
        
        selected = []
        used_items = set()
        
        # First pass: select highest scoring without repeating items
        for outfit, score in scored_outfits:
            if len(selected) >= num:
                break
            
            # Get item IDs in this outfit
            outfit_items = set()
            if outfit['type'] == 'regular':
                outfit_items.add(outfit['top']['id'])
                outfit_items.add(outfit['bottom']['id'])
                if outfit['shoes']:
                    outfit_items.add(outfit['shoes']['id'])
            else:
                outfit_items.add(outfit['dress']['id'])
                if outfit['shoes']:
                    outfit_items.add(outfit['shoes']['id'])
            
            # Check if any items already used
            if not outfit_items & used_items:  # No overlap
                selected.append((outfit, score))
                used_items.update(outfit_items)
        
        # If we don't have enough, relax the constraint
        if len(selected) < num:
            for outfit, score in scored_outfits:
                if len(selected) >= num:
                    break
                if (outfit, score) not in selected:
                    selected.append((outfit, score))
        
        return selected[:num]
    
    # Helper functions
    def _is_neutral_color(self, color):
        """Check if color is neutral"""
        if not color:
            return True
        neutrals = ['#000000', '#ffffff', '#808080', '#d3d3d3', 
                   '#a9a9a9', '#2f4f4f', '#696969']
        return color.lower() in neutrals or self._color_distance(color, '#808080') < 50
    
    def _colors_similar(self, color1, color2, threshold=30):
        """Check if two colors are similar"""
        if not color1 or not color2:
            return False
        return self._color_distance(color1, color2) < threshold
    
    def _high_contrast(self, color1, color2):
        """Check if colors have high contrast"""
        if not color1 or not color2:
            return False
        return self._color_distance(color1, color2) > 150
    
    def _color_distance(self, color1, color2):
        """Calculate distance between two hex colors"""
        try:
            r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
            r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
            
            return ((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2) ** 0.5
        except:
            return 100  # Default moderate distance
