# routers/outfits.py - Outfit suggestions and history API
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db
from models.schemas import OutfitSuggestion, OutfitLogRequest, OutfitHistoryItem

router = APIRouter(prefix="/api/outfits", tags=["outfits"])

# Lazy load recommender
_recommender = None

def get_recommender():
    global _recommender
    if _recommender is None:
        parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, parent_dir)
        from recommender import OutfitRecommender
        db_path = os.path.join(parent_dir, 'wardrobe.db')
        _recommender = OutfitRecommender(db_path)
    return _recommender

@router.get("/suggest", response_model=List[OutfitSuggestion])
def get_outfit_suggestions(
    occasion: str = Query("casual", description="Occasion: casual, work, gym, date, home"),
    temp: float = Query(28, description="Temperature in Celsius"),
    condition: str = Query("Clear", description="Weather condition"),
    num: int = Query(4, ge=1, le=6, description="Number of suggestions")
):
    """Get outfit suggestions based on occasion and weather"""
    weather = {"temp": temp, "condition": condition}
    
    recommender = get_recommender()
    suggestions = recommender.get_suggestions(occasion, weather, num)
    
    results = []
    for outfit, score in suggestions:
        suggestion = OutfitSuggestion(
            type=outfit.get('type', 'regular'),
            score=score
        )
        
        if outfit.get('top'):
            suggestion.top = {
                "id": outfit['top']['id'],
                "image_path": outfit['top']['image_path'],
                "clothing_type": outfit['top']['type'],
                "color_primary": outfit['top'].get('color_primary')
            }
        
        if outfit.get('bottom'):
            suggestion.bottom = {
                "id": outfit['bottom']['id'],
                "image_path": outfit['bottom']['image_path'],
                "clothing_type": outfit['bottom']['type'],
                "color_primary": outfit['bottom'].get('color_primary')
            }
        
        if outfit.get('shoes'):
            suggestion.shoes = {
                "id": outfit['shoes']['id'],
                "image_path": outfit['shoes']['image_path'],
                "clothing_type": outfit['shoes']['type'],
                "color_primary": outfit['shoes'].get('color_primary')
            }
        
        if outfit.get('dress'):
            suggestion.dress = {
                "id": outfit['dress']['id'],
                "image_path": outfit['dress']['image_path'],
                "clothing_type": outfit['dress']['type'],
                "color_primary": outfit['dress'].get('color_primary')
            }
            
        # Add support for outerwear
        if outfit.get('outerwear'):
             suggestion.outerwear = {
                "id": outfit['outerwear']['id'],
                "image_path": outfit['outerwear']['image_path'],
                "clothing_type": outfit['outerwear']['type'],
                "color_primary": outfit['outerwear'].get('color_primary')
            }
        
        results.append(suggestion)
    
    return results

@router.post("/log")
def log_outfit(outfit: OutfitLogRequest):
    """Log a worn outfit"""
    with get_db() as conn:
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO outfits (top_id, bottom_id, shoes_id, dress_id, outerwear_id, occasion, weather_temp, weather_condition, worn_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            outfit.top_id, outfit.bottom_id, outfit.shoes_id, outfit.dress_id, outfit.outerwear_id,
            outfit.occasion, outfit.weather_temp, outfit.weather_condition,
            datetime.now().isoformat()
        ))
        
        outfit_id = c.lastrowid
        
        # Update times_worn for each item
        now = datetime.now().isoformat()
        for item_id in [outfit.top_id, outfit.bottom_id, outfit.shoes_id, outfit.dress_id, outfit.outerwear_id]:
            if item_id:
                c.execute('''
                    UPDATE clothes SET times_worn = COALESCE(times_worn, 0) + 1, last_worn = ?
                    WHERE id = ?
                ''', (now, item_id))
        
        conn.commit()
    
    return {"id": outfit_id, "message": "Outfit logged successfully"}

@router.get("/history", response_model=List[OutfitHistoryItem])
def get_outfit_history(limit: int = Query(10, ge=1, le=50)):
    """Get outfit history"""
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT o.*, 
                   t.image_path as top_img, 
                   b.image_path as bottom_img,
                   s.image_path as shoes_img, 
                   d.image_path as dress_img,
                   w.image_path as outerwear_img
            FROM outfits o
            LEFT JOIN clothes t ON o.top_id = t.id
            LEFT JOIN clothes b ON o.bottom_id = b.id
            LEFT JOIN clothes s ON o.shoes_id = s.id
            LEFT JOIN clothes d ON o.dress_id = d.id
            LEFT JOIN clothes w ON o.outerwear_id = w.id
            ORDER BY o.worn_at DESC 
            LIMIT ?
        ''', (limit,))
        
        history = []
        for row in c.fetchall():
            history.append(OutfitHistoryItem(
                id=row['id'],
                occasion=row['occasion'] or 'casual',
                weather_temp=row['weather_temp'],
                weather_condition=row['weather_condition'],
                worn_at=row['worn_at'] or '',
                top_img=row['top_img'],
                bottom_img=row['bottom_img'],
                shoes_img=row['shoes_img'],
                dress_img=row['dress_img'],
                outerwear_img=row['outerwear_img']
            ))
        
        return history
