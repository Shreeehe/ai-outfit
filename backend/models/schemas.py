# models/schemas.py - Pydantic models for API
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ==================== CLOTHES ====================

class ClothingBase(BaseModel):
    clothing_type: str
    color_primary: str
    color_secondary: Optional[str] = None
    pattern: str = "solid"
    formality: str = "casual"
    season_weight: str = "medium"

class ClothingCreate(ClothingBase):
    image_path: str

class ClothingUpdate(BaseModel):
    clothing_type: Optional[str] = None
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None
    pattern: Optional[str] = None
    formality: Optional[str] = None
    season_weight: Optional[str] = None
    in_laundry: Optional[bool] = None
    favorite: Optional[bool] = None

class ClothingResponse(ClothingBase):
    id: int
    image_path: str
    times_worn: int = 0
    last_worn: Optional[str] = None
    in_laundry: bool = False
    favorite: bool = False
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

# ==================== CLASSIFICATION ====================

class ClassificationResult(BaseModel):
    success: bool
    clothing_type: Optional[str] = None
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None
    pattern: Optional[str] = None
    formality: Optional[str] = None
    season_weight: Optional[str] = None
    confidence: Optional[float] = None
    message: Optional[str] = None

# ==================== OUTFITS ====================

class OutfitItem(BaseModel):
    id: int
    image_path: str
    clothing_type: str
    color_primary: Optional[str] = None

class OutfitSuggestion(BaseModel):
    type: str  # 'regular' or 'dress'
    top: Optional[OutfitItem] = None
    bottom: Optional[OutfitItem] = None
    shoes: Optional[OutfitItem] = None
    dress: Optional[OutfitItem] = None
    outerwear: Optional[OutfitItem] = None
    score: float

class OutfitLogRequest(BaseModel):
    top_id: Optional[int] = None
    bottom_id: Optional[int] = None
    shoes_id: Optional[int] = None
    dress_id: Optional[int] = None
    outerwear_id: Optional[int] = None
    occasion: str
    weather_temp: Optional[float] = None
    weather_condition: Optional[str] = None

class OutfitHistoryItem(BaseModel):
    id: int
    occasion: str
    weather_temp: Optional[float] = None
    weather_condition: Optional[str] = None
    worn_at: str
    top_img: Optional[str] = None
    bottom_img: Optional[str] = None
    shoes_img: Optional[str] = None
    dress_img: Optional[str] = None
    outerwear_img: Optional[str] = None

# ==================== WEATHER ====================

class WeatherResponse(BaseModel):
    temp: float
    condition: str
    description: str
    humidity: int
    feels_like: float
    icon: str
    city: str
    emoji: str

# ==================== STATS ====================

class WardrobeStats(BaseModel):
    total: int
    by_type: dict
    in_laundry: int
    favorites: int
    never_worn: int
    total_outfits: int
