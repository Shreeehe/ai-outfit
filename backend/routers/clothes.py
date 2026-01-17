# routers/clothes.py - Clothes CRUD API
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import os
import shutil
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from models.schemas import ClothingResponse, ClothingCreate, ClothingUpdate

router = APIRouter(prefix="/api/clothes", tags=["clothes"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "wardrobe_images")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("", response_model=List[ClothingResponse])
def get_all_clothes(
    clothing_type: Optional[str] = None,
    exclude_laundry: bool = False
):
    """Get all clothes with optional filters"""
    with get_db() as conn:
        c = conn.cursor()
        
        query = "SELECT * FROM clothes WHERE 1=1"
        params = []
        
        if clothing_type:
            query += " AND clothing_type = ?"
            params.append(clothing_type)
        
        if exclude_laundry:
            query += " AND (in_laundry = 0 OR in_laundry IS NULL)"
        
        query += " ORDER BY created_at DESC"
        c.execute(query, params)
        
        clothes = []
        for row in c.fetchall():
            clothes.append({
                "id": row["id"],
                "image_path": row["image_path"],
                "clothing_type": row["clothing_type"],
                "color_primary": row["color_primary"],
                "color_secondary": row["color_secondary"],
                "pattern": row["pattern"] or "solid",
                "formality": row["formality"] or "casual",
                "season_weight": row["season_weight"] or "medium",
                "times_worn": row["times_worn"] or 0,
                "last_worn": row["last_worn"],
                "in_laundry": bool(row["in_laundry"]),
                "favorite": bool(row["favorite"]),
                "created_at": row["created_at"]
            })
        
        return clothes

@router.get("/{item_id}", response_model=ClothingResponse)
def get_clothing(item_id: int):
    """Get single clothing item"""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM clothes WHERE id = ?", (item_id,))
        row = c.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {
            "id": row["id"],
            "image_path": row["image_path"],
            "clothing_type": row["clothing_type"],
            "color_primary": row["color_primary"],
            "color_secondary": row["color_secondary"],
            "pattern": row["pattern"] or "solid",
            "formality": row["formality"] or "casual",
            "season_weight": row["season_weight"] or "medium",
            "times_worn": row["times_worn"] or 0,
            "last_worn": row["last_worn"],
            "in_laundry": bool(row["in_laundry"]),
            "favorite": bool(row["favorite"]),
            "created_at": row["created_at"]
        }

@router.post("", response_model=ClothingResponse)
async def create_clothing(
    file: UploadFile = File(...),
    clothing_type: str = Form(...),
    color_primary: str = Form(...),
    color_secondary: Optional[str] = Form(None),
    pattern: str = Form("solid"),
    formality: str = Form("casual"),
    season_weight: str = Form("medium")
):
    """Upload and create new clothing item"""
    # Read file content for hashing
    contents = await file.read()
    
    # Calculate hash to prevent duplicates
    import hashlib
    file_hash = hashlib.md5(contents).hexdigest()
    
    with get_db() as conn:
        c = conn.cursor()
        
        # Check if hash exists
        c.execute("SELECT * FROM clothes WHERE image_hash = ?", (file_hash,))
        existing = c.fetchone()
        
        if existing:
            # Return existing item instead of creating duplicate
            return {
                "id": existing["id"],
                "image_path": existing["image_path"],
                "clothing_type": existing["clothing_type"],
                "color_primary": existing["color_primary"],
                "color_secondary": existing["color_secondary"],
                "pattern": existing["pattern"] or "solid",
                "formality": existing["formality"] or "casual",
                "season_weight": existing["season_weight"] or "medium",
                "times_worn": existing["times_worn"] or 0,
                "last_worn": existing["last_worn"],
                "in_laundry": bool(existing["in_laundry"]),
                "favorite": bool(existing["favorite"]),
                "created_at": existing["created_at"]
            }
            
        # Save image if new
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_hash[:8]}.jpg"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        with open(filepath, "wb") as f:
            f.write(contents)
        
        c.execute('''
            INSERT INTO clothes (image_path, clothing_type, color_primary, color_secondary,
                               pattern, formality, season_weight, times_worn, in_laundry, favorite, image_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, 0, ?, ?)
        ''', (filepath, clothing_type, color_primary, color_secondary, pattern, formality, season_weight, file_hash, datetime.now().isoformat()))
        conn.commit()
        item_id = c.lastrowid
    
    return get_clothing(item_id)

@router.put("/{item_id}", response_model=ClothingResponse)
def update_clothing(item_id: int, update: ClothingUpdate):
    """Update clothing item"""
    with get_db() as conn:
        c = conn.cursor()
        
        # Build dynamic update query
        updates = []
        params = []
        
        for field, value in update.dict(exclude_unset=True).items():
            if value is not None:
                if field in ["in_laundry", "favorite"]:
                    value = 1 if value else 0
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        params.append(item_id)
        c.execute(f"UPDATE clothes SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
    
    return get_clothing(item_id)

@router.delete("/{item_id}")
def delete_clothing(item_id: int):
    """Delete clothing item"""
    with get_db() as conn:
        c = conn.cursor()
        
        # Get image path first
        c.execute("SELECT image_path FROM clothes WHERE id = ?", (item_id,))
        row = c.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Delete image file
        if row["image_path"] and os.path.exists(row["image_path"]):
            try:
                os.remove(row["image_path"])
            except:
                pass
        
        # Delete from database
        c.execute("DELETE FROM clothes WHERE id = ?", (item_id,))
        conn.commit()
    
    return {"message": "Item deleted"}

@router.post("/{item_id}/laundry")
def toggle_laundry(item_id: int):
    """Toggle laundry status"""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("UPDATE clothes SET in_laundry = NOT in_laundry WHERE id = ?", (item_id,))
        conn.commit()
        
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        
        c.execute("SELECT in_laundry FROM clothes WHERE id = ?", (item_id,))
        row = c.fetchone()
    
    return {"in_laundry": bool(row["in_laundry"])}

@router.post("/{item_id}/favorite")
def toggle_favorite(item_id: int):
    """Toggle favorite status"""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("UPDATE clothes SET favorite = NOT favorite WHERE id = ?", (item_id,))
        conn.commit()
        
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        
        c.execute("SELECT favorite FROM clothes WHERE id = ?", (item_id,))
        row = c.fetchone()
    
    return {"favorite": bool(row["favorite"])}

@router.delete("/clear-all")
def clear_all():
    """Delete all clothes and images (DANGEROUS)"""
    with get_db() as conn:
        c = conn.cursor()
        
        # Get all image paths
        c.execute("SELECT image_path FROM clothes")
        rows = c.fetchall()
        
        # Delete files
        for row in rows:
            if row["image_path"] and os.path.exists(row["image_path"]):
                try:
                    os.remove(row["image_path"])
                except:
                    pass
        
        # Delete from DB
        c.execute("DELETE FROM clothes")
        c.execute("DELETE FROM outfits") # Clear history too
        conn.commit()
    
    return {"message": "All items cleared"}

@router.post("/deduplicate")
def remove_duplicates():
    """Remove duplicate items based on image content hash"""
    import hashlib
    
    removed_count = 0
    with get_db() as conn:
        c = conn.cursor()
        
        # 1. Update hashes for items that don't have them
        c.execute("SELECT id, image_path FROM clothes WHERE image_hash IS NULL")
        rows = c.fetchall()
        
        for row in rows:
            if os.path.exists(row['image_path']):
                with open(row['image_path'], 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                    c.execute("UPDATE clothes SET image_hash = ? WHERE id = ?", (file_hash, row['id']))
        
        conn.commit()
        
        # 2. Find duplicates (keep oldest)
        c.execute('''
            SELECT image_hash, COUNT(*) as count 
            FROM clothes 
            GROUP BY image_hash 
            HAVING count > 1
        ''')
        duplicates = c.fetchall()
        
        for dup in duplicates:
            h = dup['image_hash']
            if not h: continue
            
            # Get all IDs for this hash, ordered by ID (oldest first)
            c.execute("SELECT id, image_path FROM clothes WHERE image_hash = ? ORDER BY id ASC", (h,))
            items = c.fetchall()
            
            # Keep first (index 0), delete others
            to_delete = items[1:]
            
            for item in to_delete:
                # Delete file
                if item['image_path'] and os.path.exists(item['image_path']):
                    try:
                        os.remove(item['image_path'])
                    except:
                        pass
                
                # Delete from DB
                c.execute("DELETE FROM clothes WHERE id = ?", (item['id'],))
                removed_count += 1
        
        conn.commit()
        
    return {"message": f"Removed {removed_count} duplicate items"}
