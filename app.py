# app.py - AI Outfit Suggestion App (Fixed Version)
"""
Simple Streamlit app with useful features:
- Add clothes with AI classification
- View wardrobe with filters
- Get outfit suggestions
- Laundry tracking
- Outfit history
- Wardrobe insights

FIXED: Database column mapping, laundry toggle, times_worn tracking
"""

import streamlit as st
import sqlite3
from datetime import datetime, timedelta
from classifier import ClothingClassifier
from recommender import OutfitRecommender
from weather import WeatherService
from profile import StyleProfileManager
import os

# Page config
st.set_page_config(
    page_title="AI Outfit",
    page_icon="👔",
    layout="wide"
)

# Database path
DB_PATH = 'wardrobe.db'

# Initialize services (cached for performance)
@st.cache_resource
def get_classifier():
    return ClothingClassifier()

@st.cache_resource
def get_weather_service():
    return WeatherService()

def get_weather():
    """Get weather with emoji (uses DEFAULT_CITY from .env)"""
    ws = get_weather_service()
    weather = ws.get_weather()  # Uses default city from env
    weather['emoji'] = ws.get_weather_icon_emoji(weather.get('condition', 'Clear'))
    return weather

recommender = OutfitRecommender(DB_PATH)
profile_manager = StyleProfileManager(DB_PATH)

# ==================== DATABASE FUNCTIONS ====================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This returns dict-like rows
    return conn

def init_db():
    """Initialize database with proper schema"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create clothes table with correct schema
    c.execute('''
        CREATE TABLE IF NOT EXISTS clothes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            clothing_type TEXT NOT NULL,
            color_primary TEXT,
            color_secondary TEXT,
            pattern TEXT DEFAULT 'solid',
            formality TEXT DEFAULT 'casual',
            season_weight TEXT DEFAULT 'medium',
            times_worn INTEGER DEFAULT 0,
            last_worn TEXT,
            in_laundry INTEGER DEFAULT 0,
            favorite INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add missing columns to existing tables (migration)
    migrations = [
        ('times_worn', 'INTEGER DEFAULT 0'),
        ('last_worn', 'TEXT'),
        ('in_laundry', 'INTEGER DEFAULT 0'),
        ('favorite', 'INTEGER DEFAULT 0'),
        ('season_weight', 'TEXT DEFAULT "medium"'),
        ('pattern', 'TEXT DEFAULT "solid"')
    ]
    
    for col_name, col_type in migrations:
        try:
            c.execute(f'ALTER TABLE clothes ADD COLUMN {col_name} {col_type}')
        except sqlite3.OperationalError:
            pass  # Column already exists
    
    # Initialize NULL values to defaults
    c.execute('UPDATE clothes SET times_worn = 0 WHERE times_worn IS NULL')
    c.execute('UPDATE clothes SET in_laundry = 0 WHERE in_laundry IS NULL')
    c.execute('UPDATE clothes SET favorite = 0 WHERE favorite IS NULL')
    c.execute('UPDATE clothes SET pattern = "solid" WHERE pattern IS NULL')
    c.execute('UPDATE clothes SET season_weight = "medium" WHERE season_weight IS NULL')
    
    # Create outfits table
    c.execute('''
        CREATE TABLE IF NOT EXISTS outfits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            top_id INTEGER,
            bottom_id INTEGER,
            shoes_id INTEGER,
            dress_id INTEGER,
            occasion TEXT,
            weather_temp REAL,
            weather_condition TEXT,
            worn_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_wardrobe_stats():
    """Get wardrobe statistics"""
    conn = get_db()
    c = conn.cursor()
    stats = {}
    
    c.execute('SELECT COUNT(*) FROM clothes')
    stats['total'] = c.fetchone()[0]
    
    c.execute('SELECT clothing_type, COUNT(*) FROM clothes GROUP BY clothing_type')
    stats['by_type'] = dict(c.fetchall())
    
    c.execute('SELECT COUNT(*) FROM clothes WHERE in_laundry = 1')
    stats['in_laundry'] = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM clothes WHERE favorite = 1')
    stats['favorites'] = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM clothes WHERE times_worn = 0 OR times_worn IS NULL')
    stats['never_worn'] = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM outfits')
    stats['total_outfits'] = c.fetchone()[0]
    
    conn.close()
    return stats

def get_clothes(clothing_type=None, exclude_laundry=False):
    """Get all clothes with proper filtering"""
    conn = get_db()
    c = conn.cursor()
    
    query = 'SELECT * FROM clothes WHERE 1=1'
    params = []
    
    if clothing_type and clothing_type != "All":
        query += ' AND clothing_type = ?'
        params.append(clothing_type)
    
    if exclude_laundry:
        query += ' AND (in_laundry = 0 OR in_laundry IS NULL)'
    
    query += ' ORDER BY created_at DESC'
    c.execute(query, params)
    
    # Convert to proper dict using column names
    clothes = []
    for row in c.fetchall():
        clothes.append({
            'id': row['id'],
            'image_path': row['image_path'],
            'clothing_type': row['clothing_type'],
            'color_primary': row['color_primary'],
            'color_secondary': row['color_secondary'],
            'pattern': row['pattern'] or 'solid',
            'formality': row['formality'] or 'casual',
            'season_weight': row['season_weight'] or 'medium',
            'times_worn': row['times_worn'] or 0,
            'last_worn': row['last_worn'],
            'in_laundry': row['in_laundry'] or 0,
            'favorite': row['favorite'] or 0,
            'created_at': row['created_at']
        })
    
    conn.close()
    return clothes

def set_laundry(item_id, in_laundry):
    """Set laundry status explicitly"""
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE clothes SET in_laundry = ? WHERE id = ?', (1 if in_laundry else 0, item_id))
    conn.commit()
    conn.close()

def set_favorite(item_id, favorite):
    """Set favorite status explicitly"""
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE clothes SET favorite = ? WHERE id = ?', (1 if favorite else 0, item_id))
    conn.commit()
    conn.close()

def delete_clothing(item_id):
    """Delete a clothing item"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT image_path FROM clothes WHERE id = ?', (item_id,))
    row = c.fetchone()
    if row and row['image_path'] and os.path.exists(row['image_path']):
        try:
            os.remove(row['image_path'])
        except:
            pass
    c.execute('DELETE FROM clothes WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

def save_clothing(image_path, data):
    """Save a new clothing item"""
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO clothes (image_path, clothing_type, color_primary, color_secondary, 
                           pattern, formality, season_weight, times_worn, in_laundry, favorite, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, 0, ?)
    ''', (
        image_path, 
        data['type'], 
        data['color_primary'], 
        data.get('color_secondary'),
        data.get('pattern', 'solid'), 
        data['formality'], 
        data.get('season_weight', 'medium'),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def log_outfit(outfit, occasion, weather):
    """Log a worn outfit and update times_worn"""
    conn = get_db()
    c = conn.cursor()
    
    # Get item IDs from outfit
    top_id = outfit.get('top', {}).get('id') if outfit.get('type') == 'regular' else None
    bottom_id = outfit.get('bottom', {}).get('id') if outfit.get('type') == 'regular' else None
    shoes_id = outfit.get('shoes', {}).get('id') if outfit.get('shoes') else None
    dress_id = outfit.get('dress', {}).get('id') if outfit.get('type') == 'dress' else None
    
    # Insert outfit record
    c.execute('''
        INSERT INTO outfits (top_id, bottom_id, shoes_id, dress_id, occasion, weather_temp, weather_condition, worn_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (top_id, bottom_id, shoes_id, dress_id, occasion, 
          weather.get('temp'), weather.get('condition'), datetime.now().isoformat()))
    
    outfit_id = c.lastrowid
    
    # Update times_worn for each item
    now = datetime.now().isoformat()
    for item_id in [top_id, bottom_id, shoes_id, dress_id]:
        if item_id:
            c.execute('''
                UPDATE clothes 
                SET times_worn = COALESCE(times_worn, 0) + 1, last_worn = ? 
                WHERE id = ?
            ''', (now, item_id))
    
    conn.commit()
    conn.close()
    return outfit_id

def get_outfit_history(limit=10):
    """Get outfit history with images"""
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT o.*, 
               t.image_path as top_img, 
               b.image_path as bottom_img,
               s.image_path as shoes_img, 
               d.image_path as dress_img
        FROM outfits o
        LEFT JOIN clothes t ON o.top_id = t.id
        LEFT JOIN clothes b ON o.bottom_id = b.id
        LEFT JOIN clothes s ON o.shoes_id = s.id
        LEFT JOIN clothes d ON o.dress_id = d.id
        ORDER BY o.worn_at DESC 
        LIMIT ?
    ''', (limit,))
    
    history = []
    for row in c.fetchall():
        history.append({
            'id': row['id'],
            'top_id': row['top_id'],
            'bottom_id': row['bottom_id'],
            'shoes_id': row['shoes_id'],
            'dress_id': row['dress_id'],
            'occasion': row['occasion'],
            'weather_temp': row['weather_temp'],
            'weather_condition': row['weather_condition'],
            'worn_at': row['worn_at'],
            'top_img': row['top_img'],
            'bottom_img': row['bottom_img'],
            'shoes_img': row['shoes_img'],
            'dress_img': row['dress_img']
        })
    
    conn.close()
    return history

def get_forgotten_items():
    """Get items not worn in 30+ days"""
    conn = get_db()
    c = conn.cursor()
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
    
    c.execute('''
        SELECT * FROM clothes 
        WHERE (last_worn < ? OR last_worn IS NULL) 
        AND (in_laundry = 0 OR in_laundry IS NULL)
        ORDER BY times_worn ASC 
        LIMIT 5
    ''', (thirty_days_ago,))
    
    items = []
    for row in c.fetchall():
        items.append({
            'id': row['id'],
            'image_path': row['image_path'],
            'clothing_type': row['clothing_type'],
            'times_worn': row['times_worn'] or 0,
            'last_worn': row['last_worn']
        })
    
    conn.close()
    return items

# ==================== INITIALIZE ====================
init_db()

# ==================== SIDEBAR ====================
st.sidebar.title("👔 AI Outfit")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "➕ Add Clothes", "👕 Wardrobe", "✨ Get Outfit", "🧺 Laundry", "📊 Insights", "📜 History"]
)

# Quick stats in sidebar
stats = get_wardrobe_stats()
st.sidebar.divider()
st.sidebar.metric("Total Clothes", stats['total'])
st.sidebar.metric("In Laundry", stats['in_laundry'])

# ==================== HOME PAGE ====================
if page == "🏠 Home":
    st.title("👔 AI Outfit - Home")
    
    # Weather
    weather = get_weather()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Temperature", f"{weather.get('temp', '--')}°C")
    with col2:
        st.metric("Condition", weather.get('condition', 'Unknown'))
    with col3:
        st.metric("Feels Like", f"{weather.get('feels_like', '--')}°C")
    
    st.divider()
    
    # Quick stats
    st.subheader("📊 Quick Stats")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Clothes", stats['total'])
    with col2:
        st.metric("Outfits Logged", stats['total_outfits'])
    with col3:
        st.metric("Favorites", stats['favorites'])
    with col4:
        st.metric("Never Worn", stats['never_worn'])
    
    st.divider()
    
    # Forgotten items
    forgotten = get_forgotten_items()
    if forgotten:
        st.subheader("🔔 Not Worn in 30+ Days")
        cols = st.columns(min(len(forgotten), 5))
        for i, item in enumerate(forgotten[:5]):
            with cols[i]:
                if item['image_path'] and os.path.exists(item['image_path']):
                    st.image(item['image_path'], caption=item['clothing_type'].title(), use_column_width=True)

# ==================== ADD CLOTHES ====================
elif page == "➕ Add Clothes":
    st.title("➕ Add Clothes")
    
    upload_method = st.radio("Upload Method", ["📷 Camera", "📁 File Upload"], horizontal=True)
    
    if upload_method == "📷 Camera":
        uploaded_file = st.camera_input("Take a photo")
    else:
        uploaded_file = st.file_uploader("Choose an image", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        os.makedirs('wardrobe_images', exist_ok=True)
        image_path = f"wardrobe_images/{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        with open(image_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image_path, caption="Preview", use_column_width=True)
        
        with col2:
            with st.spinner("🤖 AI analyzing..."):
                classifier = get_classifier()
                result = classifier.classify_full(image_path)
            
            if result.get('success'):
                st.success(f"✅ Detected: {result.get('clothing_type', 'Unknown').title()}")
                
                # Map to category
                type_map = {
                    't-shirt': 'top', 'shirt': 'top', 'blouse': 'top', 'sweater': 'top', 'hoodie': 'top',
                    'jeans': 'bottom', 'trousers': 'bottom', 'pants': 'bottom', 'shorts': 'bottom', 'skirt': 'bottom',
                    'dress': 'dress', 'jumpsuit': 'dress',
                    'sneakers': 'shoes', 'formal shoes': 'shoes', 'boots': 'shoes', 'sandals': 'shoes',
                    'jacket': 'outerwear', 'coat': 'outerwear', 'blazer': 'outerwear', 'cardigan': 'outerwear'
                }
                detected_type = type_map.get(result.get('clothing_type', '').lower(), 'top')
                detected_formality = result.get('formality', 'casual')
                detected_pattern = result.get('pattern', 'solid')
                detected_color = result.get('color_primary', '#000000')
            else:
                st.warning(f"⚠️ {result.get('message', 'Could not classify')}")
                detected_type = 'top'
                detected_formality = 'casual'
                detected_pattern = 'solid'
                detected_color = '#000000'
            
            st.subheader("Confirm Details")
            
            type_options = ["top", "bottom", "dress", "shoes", "outerwear"]
            clothing_type = st.selectbox("Type", type_options, 
                                        index=type_options.index(detected_type) if detected_type in type_options else 0)
            
            col_a, col_b = st.columns(2)
            with col_a:
                color_primary = st.color_picker("Primary Color", detected_color)
            with col_b:
                color_secondary = st.color_picker("Secondary Color", '#ffffff')
            
            formality_options = ["casual", "business-casual", "formal", "athletic"]
            formality = st.selectbox("Formality", formality_options,
                                    index=formality_options.index(detected_formality) if detected_formality in formality_options else 0)
            
            pattern_options = ["solid", "striped", "checkered", "floral", "printed"]
            pattern = st.selectbox("Pattern", pattern_options,
                                  index=pattern_options.index(detected_pattern) if detected_pattern in pattern_options else 0)
            
            season_weight = st.selectbox("Weight", ["light", "medium", "heavy"], index=1)
            
            if st.button("💾 Save to Wardrobe", type="primary"):
                save_clothing(image_path, {
                    'type': clothing_type,
                    'color_primary': color_primary,
                    'color_secondary': color_secondary if color_secondary != '#ffffff' else None,
                    'formality': formality,
                    'pattern': pattern,
                    'season_weight': season_weight
                })
                st.success("✅ Saved to wardrobe!")
                st.balloons()

# ==================== WARDROBE ====================
elif page == "👕 Wardrobe":
    st.title("👕 My Wardrobe")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_type = st.selectbox("Filter by Type", ["All", "top", "bottom", "dress", "shoes", "outerwear"])
    with col2:
        show_laundry = st.checkbox("Include items in laundry", value=False)
    with col3:
        sort_by = st.selectbox("Sort by", ["Newest", "Most Worn", "Least Worn"])
    
    # Get clothes with proper filtering
    clothes = get_clothes(
        clothing_type=filter_type if filter_type != "All" else None, 
        exclude_laundry=not show_laundry
    )
    
    # Sort
    if sort_by == "Most Worn":
        clothes.sort(key=lambda x: x.get('times_worn', 0) or 0, reverse=True)
    elif sort_by == "Least Worn":
        clothes.sort(key=lambda x: x.get('times_worn', 0) or 0)
    
    if not clothes:
        st.info("No clothes found. Add some!")
    else:
        st.caption(f"Showing {len(clothes)} items")
        
        cols = st.columns(4)
        for i, item in enumerate(clothes):
            with cols[i % 4]:
                if item['image_path'] and os.path.exists(item['image_path']):
                    st.image(item['image_path'], use_column_width=True)
                
                st.write(f"**{item['clothing_type'].title()}**")
                
                # Status indicators
                status_parts = [f"Worn {item.get('times_worn', 0)}x"]
                if item.get('in_laundry'):
                    status_parts.append("🧺 In Laundry")
                if item.get('favorite'):
                    status_parts.append("❤️")
                st.caption(" | ".join(status_parts))
                
                # Action buttons
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    fav_label = "💔" if item.get('favorite') else "❤️"
                    if st.button(fav_label, key=f"fav_{item['id']}", help="Toggle Favorite"):
                        set_favorite(item['id'], not item.get('favorite'))
                        st.rerun()
                with col_b:
                    laundry_label = "✅" if item.get('in_laundry') else "🧺"
                    if st.button(laundry_label, key=f"laundry_{item['id']}", help="Toggle Laundry"):
                        set_laundry(item['id'], not item.get('in_laundry'))
                        st.rerun()
                with col_c:
                    if st.button("🗑️", key=f"del_{item['id']}", help="Delete"):
                        delete_clothing(item['id'])
                        st.rerun()
                
                st.divider()

# ==================== GET OUTFIT ====================
elif page == "✨ Get Outfit":
    st.title("✨ Get Outfit Suggestions")
    
    weather = get_weather()
    st.info(f"🌤️ Weather: {weather.get('temp')}°C, {weather.get('condition')} (Feels like {weather.get('feels_like')}°C)")
    
    col1, col2 = st.columns(2)
    with col1:
        occasion = st.selectbox("Occasion", ["casual", "work", "gym", "date", "home"])
    with col2:
        num_suggestions = st.slider("Number of suggestions", 1, 6, 4)
    
    if st.button("✨ Generate Outfits", type="primary"):
        with st.spinner("Finding perfect outfits..."):
            suggestions = recommender.get_suggestions(occasion, weather, num_suggestions)
        
        if not suggestions:
            st.warning("Not enough clothes. Add at least 1 top, 1 bottom, and 1 pair of shoes!")
        else:
            st.success(f"Found {len(suggestions)} suggestions!")
            
            for idx, (outfit, score) in enumerate(suggestions):
                with st.expander(f"Option {idx + 1} - Score: {int(score)}/100", expanded=(idx == 0)):
                    
                    if outfit.get('type') == 'regular':
                        cols = st.columns(3)
                        if outfit.get('top') and outfit['top'].get('image_path') and os.path.exists(outfit['top']['image_path']):
                            with cols[0]:
                                st.image(outfit['top']['image_path'], caption="👕 Top", use_column_width=True)
                        if outfit.get('bottom') and outfit['bottom'].get('image_path') and os.path.exists(outfit['bottom']['image_path']):
                            with cols[1]:
                                st.image(outfit['bottom']['image_path'], caption="👖 Bottom", use_column_width=True)
                        if outfit.get('shoes') and outfit['shoes'].get('image_path') and os.path.exists(outfit['shoes']['image_path']):
                            with cols[2]:
                                st.image(outfit['shoes']['image_path'], caption="👟 Shoes", use_column_width=True)
                    
                    elif outfit.get('type') == 'dress':
                        cols = st.columns(2)
                        if outfit.get('dress') and outfit['dress'].get('image_path') and os.path.exists(outfit['dress']['image_path']):
                            with cols[0]:
                                st.image(outfit['dress']['image_path'], caption="👗 Dress", use_column_width=True)
                        if outfit.get('shoes') and outfit['shoes'].get('image_path') and os.path.exists(outfit['shoes']['image_path']):
                            with cols[1]:
                                st.image(outfit['shoes']['image_path'], caption="👠 Shoes", use_column_width=True)
                    
                    if st.button(f"👍 Wear This", key=f"wear_{idx}"):
                        outfit_id = log_outfit(outfit, occasion, weather)
                        st.success("✅ Outfit logged! Have a great day!")

# ==================== LAUNDRY ====================
elif page == "🧺 Laundry":
    st.title("🧺 Laundry Basket")
    
    # Get ALL clothes and filter for laundry items
    all_clothes = get_clothes(exclude_laundry=False)
    laundry_items = [item for item in all_clothes if item.get('in_laundry')]
    
    if not laundry_items:
        st.info("🧺 Laundry basket is empty!")
        st.caption("Mark items as 'in laundry' from the Wardrobe page")
    else:
        st.write(f"**{len(laundry_items)} items** in laundry")
        
        if st.button("✅ Mark All as Clean", type="primary"):
            for item in laundry_items:
                set_laundry(item['id'], False)
            st.success("All items marked clean!")
            st.rerun()
        
        st.divider()
        
        cols = st.columns(4)
        for i, item in enumerate(laundry_items):
            with cols[i % 4]:
                if item['image_path'] and os.path.exists(item['image_path']):
                    st.image(item['image_path'], use_column_width=True)
                st.write(f"**{item['clothing_type'].title()}**")
                if st.button("✅ Mark Clean", key=f"clean_{item['id']}"):
                    set_laundry(item['id'], False)
                    st.rerun()
                st.divider()

# ==================== INSIGHTS ====================
elif page == "📊 Insights":
    st.title("📊 Wardrobe Insights")
    
    stats = get_wardrobe_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Items", stats['total'])
    with col2:
        st.metric("Outfits Worn", stats['total_outfits'])
    with col3:
        st.metric("Favorites", stats['favorites'])
    with col4:
        st.metric("In Laundry", stats['in_laundry'])
    
    st.divider()
    
    st.subheader("Items by Type")
    if stats.get('by_type'):
        for item_type, count in stats['by_type'].items():
            progress_val = min(count / max(stats['total'], 1), 1.0)
            st.progress(progress_val, text=f"{item_type.title()}: {count}")
    else:
        st.info("No items yet")
    
    st.divider()
    
    st.subheader("AI Learning Stats")
    try:
        profile_stats = profile_manager.get_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Outfits Rated", profile_stats.get('total_ratings', 0))
        with col2:
            avg_rating = profile_stats.get('average_rating', 0)
            st.metric("Average Rating", f"{avg_rating:.1f}/5" if avg_rating else "N/A")
    except:
        st.caption("No ratings yet")
    
    if stats['never_worn'] > 0:
        st.warning(f"⚠️ {stats['never_worn']} items have never been worn!")
    
    # ===== TESTING TOOLS =====
    st.divider()
    st.subheader("🧪 Testing Tools")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear All Clothes", type="secondary"):
            st.session_state['confirm_clear_clothes'] = True
    
    with col2:
        if st.button("🗑️ Clear All Data", type="secondary"):
            st.session_state['confirm_clear_all'] = True
    
    # Confirmation for clear clothes
    if st.session_state.get('confirm_clear_clothes'):
        st.warning("⚠️ This will delete ALL clothes and their images!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Delete All Clothes", type="primary"):
                conn = get_db()
                c = conn.cursor()
                # Get all image paths
                c.execute('SELECT image_path FROM clothes')
                for row in c.fetchall():
                    if row['image_path'] and os.path.exists(row['image_path']):
                        try:
                            os.remove(row['image_path'])
                        except:
                            pass
                # Delete all clothes
                c.execute('DELETE FROM clothes')
                conn.commit()
                conn.close()
                st.session_state['confirm_clear_clothes'] = False
                st.success("All clothes deleted!")
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state['confirm_clear_clothes'] = False
                st.rerun()
    
    # Confirmation for clear all
    if st.session_state.get('confirm_clear_all'):
        st.error("⚠️ This will delete ALL data: clothes, outfits, and preferences!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Delete Everything", type="primary"):
                conn = get_db()
                c = conn.cursor()
                # Delete images
                c.execute('SELECT image_path FROM clothes')
                for row in c.fetchall():
                    if row['image_path'] and os.path.exists(row['image_path']):
                        try:
                            os.remove(row['image_path'])
                        except:
                            pass
                # Clear all tables
                c.execute('DELETE FROM clothes')
                c.execute('DELETE FROM outfits')
                try:
                    c.execute('DELETE FROM style_profile')
                except:
                    pass
                try:
                    c.execute('DELETE FROM outfit_ratings')
                except:
                    pass
                conn.commit()
                conn.close()
                st.session_state['confirm_clear_all'] = False
                st.success("All data cleared!")
                st.rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_all"):
                st.session_state['confirm_clear_all'] = False
                st.rerun()

# ==================== HISTORY ====================
elif page == "📜 History":
    st.title("📜 Outfit History")
    
    history = get_outfit_history(20)
    
    if not history:
        st.info("No outfit history yet. Wear some outfits!")
    else:
        for outfit in history:
            worn_date = None
            if outfit.get('worn_at'):
                try:
                    worn_date = datetime.fromisoformat(outfit['worn_at'])
                except:
                    pass
            
            date_str = worn_date.strftime("%B %d, %Y at %I:%M %p") if worn_date else "Unknown"
            occasion = outfit.get('occasion', 'casual') or 'casual'
            
            with st.expander(f"📅 {date_str} • {occasion.title()}"):
                cols = st.columns(3)
                
                if outfit.get('top_img') and os.path.exists(outfit['top_img']):
                    with cols[0]:
                        st.image(outfit['top_img'], caption="Top", use_column_width=True)
                
                if outfit.get('bottom_img') and os.path.exists(outfit['bottom_img']):
                    with cols[1]:
                        st.image(outfit['bottom_img'], caption="Bottom", use_column_width=True)
                
                if outfit.get('shoes_img') and os.path.exists(outfit['shoes_img']):
                    with cols[2]:
                        st.image(outfit['shoes_img'], caption="Shoes", use_column_width=True)
                
                if outfit.get('dress_img') and os.path.exists(outfit['dress_img']):
                    st.image(outfit['dress_img'], caption="Dress", use_column_width=True)
                
                temp = outfit.get('weather_temp', '--')
                condition = outfit.get('weather_condition', 'Unknown')
                st.caption(f"Weather: {temp}°C, {condition}")
