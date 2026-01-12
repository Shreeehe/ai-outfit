# profile.py - Style Profile Manager
"""
Learns user preferences over time based on:
- Outfit ratings
- Wear history
- Color preferences
- Formality preferences
"""

import sqlite3
from datetime import datetime
from collections import defaultdict

class StyleProfileManager:
    def __init__(self, db_path='wardrobe.db'):
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create style profile tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Style preferences table
        c.execute('''
            CREATE TABLE IF NOT EXISTS style_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_type TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                updated_at TEXT,
                UNIQUE(preference_type, preference_value)
            )
        ''')
        
        # Outfit ratings table
        c.execute('''
            CREATE TABLE IF NOT EXISTS outfit_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                outfit_id INTEGER,
                rating INTEGER NOT NULL,
                feedback TEXT,
                created_at TEXT,
                FOREIGN KEY (outfit_id) REFERENCES outfits(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def rate_outfit(self, outfit_id, rating, feedback=None):
        """
        Save an outfit rating and learn from it
        
        Args:
            outfit_id: ID from outfits table
            rating: 1-5 stars
            feedback: Optional text feedback
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Save the rating
        c.execute('''
            INSERT INTO outfit_ratings (outfit_id, rating, feedback, created_at)
            VALUES (?, ?, ?, ?)
        ''', (outfit_id, rating, feedback, datetime.now().isoformat()))
        
        # Get outfit details
        c.execute('''
            SELECT top_id, bottom_id, shoes_id, occasion
            FROM outfits WHERE id = ?
        ''', (outfit_id,))
        outfit = c.fetchone()
        
        if outfit:
            top_id, bottom_id, shoes_id, occasion = outfit
            
            # Get item details and learn from them
            item_ids = [id for id in [top_id, bottom_id, shoes_id] if id]
            
            for item_id in item_ids:
                c.execute('SELECT color_primary, formality, pattern FROM clothes WHERE id = ?', (item_id,))
                item = c.fetchone()
                if item:
                    color, formality, pattern = item
                    
                    # Weight adjustment based on rating (-2 to +2)
                    weight_change = (rating - 3) * 0.5  # Rating 5 = +1.0, Rating 1 = -1.0
                    
                    # Update color preference
                    if color:
                        self._update_preference('color', color, weight_change, c)
                    
                    # Update formality preference
                    if formality:
                        self._update_preference('formality', formality, weight_change, c)
                    
                    # Update pattern preference
                    if pattern:
                        self._update_preference('pattern', pattern, weight_change, c)
            
            # Update occasion preference
            if occasion:
                weight_change = (rating - 3) * 0.3
                self._update_preference('occasion', occasion, weight_change, c)
        
        conn.commit()
        conn.close()
    
    def _update_preference(self, pref_type, pref_value, weight_change, cursor):
        """Update or insert a preference with weight change"""
        cursor.execute('''
            INSERT INTO style_profile (preference_type, preference_value, weight, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(preference_type, preference_value) 
            DO UPDATE SET 
                weight = MAX(0.0, MIN(5.0, weight + ?)),
                updated_at = ?
        ''', (pref_type, pref_value, 1.0 + weight_change, datetime.now().isoformat(),
              weight_change, datetime.now().isoformat()))
    
    def get_preferences(self):
        """
        Get all learned preferences
        
        Returns:
            dict: {
                'colors': {'#ff0000': 1.5, '#0000ff': 0.8, ...},
                'formality': {'casual': 2.0, 'formal': 1.0, ...},
                'patterns': {'solid': 1.8, 'striped': 0.5, ...},
                'occasions': {'work': 1.5, 'casual': 2.0, ...}
            }
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT preference_type, preference_value, weight FROM style_profile')
        rows = c.fetchall()
        conn.close()
        
        preferences = {
            'colors': {},
            'formality': {},
            'patterns': {},
            'occasions': {}
        }
        
        type_map = {
            'color': 'colors',
            'formality': 'formality',
            'pattern': 'patterns',
            'occasion': 'occasions'
        }
        
        for pref_type, pref_value, weight in rows:
            key = type_map.get(pref_type, pref_type)
            if key in preferences:
                preferences[key][pref_value] = weight
        
        return preferences
    
    def get_favorite_colors(self, limit=5):
        """Get top N favorite colors by weight"""
        prefs = self.get_preferences()
        colors = prefs.get('colors', {})
        sorted_colors = sorted(colors.items(), key=lambda x: x[1], reverse=True)
        return sorted_colors[:limit]
    
    def get_formality_distribution(self):
        """Get formality preference distribution as percentages"""
        prefs = self.get_preferences()
        formality = prefs.get('formality', {})
        
        if not formality:
            return {'casual': 33, 'business-casual': 33, 'formal': 34}
        
        total = sum(formality.values())
        if total == 0:
            return {'casual': 33, 'business-casual': 33, 'formal': 34}
        
        return {k: (v / total) * 100 for k, v in formality.items()}
    
    def apply_style_bonus(self, outfit, preferences=None):
        """
        Calculate bonus score for an outfit based on learned preferences
        
        Args:
            outfit: Outfit dict with items
            preferences: Optional pre-fetched preferences
            
        Returns:
            int: Bonus score (can be negative)
        """
        if preferences is None:
            preferences = self.get_preferences()
        
        bonus = 0
        
        # Get items to check
        items = []
        if outfit.get('type') == 'regular':
            items = [outfit.get('top'), outfit.get('bottom')]
            if outfit.get('shoes'):
                items.append(outfit['shoes'])
        elif outfit.get('dress'):
            items = [outfit.get('dress')]
            if outfit.get('shoes'):
                items.append(outfit['shoes'])
        
        for item in items:
            if not item:
                continue
            
            # Color bonus
            color = item.get('color_primary')
            if color and color in preferences.get('colors', {}):
                weight = preferences['colors'][color]
                bonus += (weight - 1.0) * 10  # -10 to +40 based on weight
            
            # Formality bonus
            formality = item.get('formality')
            if formality and formality in preferences.get('formality', {}):
                weight = preferences['formality'][formality]
                bonus += (weight - 1.0) * 8
            
            # Pattern bonus
            pattern = item.get('pattern')
            if pattern and pattern in preferences.get('patterns', {}):
                weight = preferences['patterns'][pattern]
                bonus += (weight - 1.0) * 5
        
        return int(bonus)
    
    def get_stats(self):
        """Get profile statistics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Total ratings
        c.execute('SELECT COUNT(*) FROM outfit_ratings')
        total_ratings = c.fetchone()[0]
        
        # Average rating
        c.execute('SELECT AVG(rating) FROM outfit_ratings')
        avg_rating = c.fetchone()[0] or 0
        
        # Rating distribution
        c.execute('SELECT rating, COUNT(*) FROM outfit_ratings GROUP BY rating')
        distribution = dict(c.fetchall())
        
        conn.close()
        
        return {
            'total_ratings': total_ratings,
            'average_rating': round(avg_rating, 1),
            'distribution': distribution
        }
    
    def reset_profile(self):
        """Reset all learned preferences"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM style_profile')
        conn.commit()
        conn.close()


# Quick feedback tags for rating
FEEDBACK_TAGS = [
    "Perfect fit! 👌",
    "Great colors 🎨",
    "Very comfortable 😊",
    "Got compliments! ⭐",
    "Too formal 👔",
    "Too casual 👕",
    "Colors clashed 🚫",
    "Too warm 🥵",
    "Too cold 🥶",
    "Didn't feel right 😐"
]
