# routers/stats.py - Statistics API
from fastapi import APIRouter
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from models.schemas import WardrobeStats

router = APIRouter(prefix="/api", tags=["stats"])

@router.get("/stats", response_model=WardrobeStats)
def get_wardrobe_stats():
    """Get wardrobe statistics"""
    with get_db() as conn:
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM clothes')
        total = c.fetchone()[0]
        
        c.execute('SELECT clothing_type, COUNT(*) FROM clothes GROUP BY clothing_type')
        by_type = dict(c.fetchall())
        
        c.execute('SELECT COUNT(*) FROM clothes WHERE in_laundry = 1')
        in_laundry = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM clothes WHERE favorite = 1')
        favorites = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM clothes WHERE times_worn = 0 OR times_worn IS NULL')
        never_worn = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM outfits')
        total_outfits = c.fetchone()[0]
    
    return WardrobeStats(
        total=total,
        by_type=by_type,
        in_laundry=in_laundry,
        favorites=favorites,
        never_worn=never_worn,
        total_outfits=total_outfits
    )

@router.delete("/clear-all")
def clear_all_data():
    """Clear all data (for testing)"""
    with get_db() as conn:
        c = conn.cursor()
        
        # Get image paths
        c.execute('SELECT image_path FROM clothes')
        for row in c.fetchall():
            if row['image_path'] and os.path.exists(row['image_path']):
                try:
                    os.remove(row['image_path'])
                except:
                    pass
        
        c.execute('DELETE FROM clothes')
        c.execute('DELETE FROM outfits')
        conn.commit()
    
    return {"message": "All data cleared"}
