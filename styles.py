# styles.py - Premium UI Styles for AI Outfit App
"""
Modern, polished styling with:
- Dark glassmorphism theme
- Smooth animations
- Premium card designs
- Interactive elements
"""

def get_app_styles():
    """Return the main app CSS styles"""
    return """
    <style>
    /* ===== GLOBAL STYLES ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #0f0f1a;
        --bg-secondary: #1a1a2e;
        --bg-card: rgba(30, 30, 50, 0.7);
        --bg-glass: rgba(255, 255, 255, 0.05);
        --accent-primary: #6366f1;
        --accent-secondary: #8b5cf6;
        --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        --text-primary: #ffffff;
        --text-secondary: rgba(255, 255, 255, 0.7);
        --text-muted: rgba(255, 255, 255, 0.5);
        --border-color: rgba(255, 255, 255, 0.1);
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --shadow-glow: 0 0 40px rgba(99, 102, 241, 0.3);
    }
    
    /* Dark theme base */
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%) !important;
    }
    
    .stApp > header {
        background: transparent !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 15, 26, 0.95) 0%, rgba(26, 26, 46, 0.95) 100%) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        padding: 12px 16px !important;
        border-radius: 12px !important;
        margin: 4px 0 !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background: var(--bg-glass) !important;
        transform: translateX(4px);
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6, p, span, div {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary);
    }
    
    h1 {
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem !important;
    }
    
    h2, h3 {
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }
    
    /* ===== OUTFIT CARDS ===== */
    .outfit-card {
        background: var(--bg-glass);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 24px;
        margin: 16px 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .outfit-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--accent-gradient);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .outfit-card:hover {
        transform: translateY(-8px);
        box-shadow: var(--shadow-glow);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    .outfit-card:hover::before {
        opacity: 1;
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .option-badge {
        background: var(--accent-gradient);
        color: white;
        padding: 8px 16px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    
    /* Score Bar */
    .score-container {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .score-label {
        color: var(--text-secondary);
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .score-bar {
        width: 120px;
        height: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        overflow: hidden;
    }
    
    .score-fill {
        height: 100%;
        background: var(--accent-gradient);
        border-radius: 10px;
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .score-value {
        color: var(--accent-primary);
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    /* Color Palette Dots */
    .color-palette {
        display: flex;
        gap: 6px;
        margin-top: 8px;
    }
    
    .color-dot {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 2px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.2s ease;
    }
    
    .color-dot:hover {
        transform: scale(1.2);
    }
    
    /* Item Labels */
    .item-label {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.08);
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-top: 8px;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: var(--accent-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: none !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: var(--accent-primary) !important;
    }
    
    /* ===== METRICS ===== */
    [data-testid="stMetric"] {
        background: var(--bg-glass) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-glow);
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
    }
    
    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }
    
    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {
        background: var(--bg-glass) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: 16px !important;
        padding: 40px 20px !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-primary) !important;
        background: rgba(99, 102, 241, 0.05) !important;
    }
    
    /* ===== RATING STARS ===== */
    .rating-container {
        display: flex;
        gap: 8px;
        justify-content: center;
        padding: 16px;
    }
    
    .star {
        font-size: 2rem;
        cursor: pointer;
        transition: all 0.2s ease;
        color: rgba(255, 255, 255, 0.2);
    }
    
    .star:hover,
    .star.active {
        color: #fbbf24;
        transform: scale(1.2);
        text-shadow: 0 0 20px rgba(251, 191, 36, 0.5);
    }
    
    /* ===== LAUNDRY BADGE ===== */
    .laundry-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(245, 158, 11, 0.2);
        color: var(--warning);
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .clean-badge {
        background: rgba(16, 185, 129, 0.2);
        color: var(--success);
    }
    
    /* ===== LOADING SKELETON ===== */
    .skeleton {
        background: linear-gradient(90deg, 
            var(--bg-glass) 25%, 
            rgba(255, 255, 255, 0.1) 50%, 
            var(--bg-glass) 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 12px;
    }
    
    @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    .skeleton-card {
        height: 300px;
        margin: 16px 0;
    }
    
    .skeleton-text {
        height: 20px;
        margin: 8px 0;
        width: 80%;
    }
    
    .skeleton-circle {
        width: 150px;
        height: 150px;
        border-radius: 50%;
    }
    
    /* ===== ANIMATIONS ===== */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .animate-fade-in {
        animation: fadeInUp 0.6s ease-out forwards;
    }
    
    .animate-pulse {
        animation: pulse 2s ease-in-out infinite;
    }
    
    .animate-float {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Stagger animations for lists */
    .stagger-1 { animation-delay: 0.1s; }
    .stagger-2 { animation-delay: 0.2s; }
    .stagger-3 { animation-delay: 0.3s; }
    .stagger-4 { animation-delay: 0.4s; }
    
    /* ===== OCCASION BUTTONS ===== */
    .occasion-btn {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        text-align: center;
        transition: all 0.3s ease !important;
        cursor: pointer;
    }
    
    .occasion-btn:hover {
        background: rgba(99, 102, 241, 0.1) !important;
        border-color: var(--accent-primary) !important;
        transform: translateY(-4px);
    }
    
    .occasion-btn.active {
        background: var(--accent-gradient) !important;
        border-color: transparent !important;
        box-shadow: var(--shadow-glow);
    }
    
    .occasion-icon {
        font-size: 2rem;
        margin-bottom: 8px;
    }
    
    .occasion-label {
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* ===== WEATHER CARD ===== */
    .weather-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 24px;
        margin: 20px 0;
    }
    
    .weather-temp {
        font-size: 3.5rem;
        font-weight: 700;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .weather-icon {
        font-size: 4rem;
        animation: float 3s ease-in-out infinite;
    }
    
    /* ===== IMAGE CONTAINERS ===== */
    .image-container {
        position: relative;
        border-radius: 16px;
        overflow: hidden;
        background: var(--bg-glass);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    .image-container:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    .image-container img {
        border-radius: 16px;
        transition: all 0.3s ease;
    }
    
    /* ===== SUCCESS/ERROR STATES ===== */
    .success-message {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 16px;
        color: var(--success);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .error-message {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        padding: 16px;
        color: var(--error);
    }
    
    /* ===== STYLE PROFILE ===== */
    .profile-stat {
        background: var(--bg-glass);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
    }
    
    .profile-stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .profile-stat-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 8px;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--accent-primary);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-secondary);
    }
    
    /* ===== DIVIDERS ===== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 24px 0;
    }
    
    /* ===== INFO/WARNING BOXES ===== */
    .stAlert {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
    }
    </style>
    """


def get_loading_skeleton():
    """Return loading skeleton HTML"""
    return """
    <div class="animate-fade-in">
        <div class="skeleton skeleton-card"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text" style="width: 60%;"></div>
    </div>
    """


def get_outfit_card(option_num, score, items_html):
    """Generate an outfit card HTML"""
    return f"""
    <div class="outfit-card animate-fade-in stagger-{option_num}">
        <div class="card-header">
            <span class="option-badge">✨ Option {option_num}</span>
            <div class="score-container">
                <span class="score-label">Match</span>
                <div class="score-bar">
                    <div class="score-fill" style="width: {min(score, 100)}%;"></div>
                </div>
                <span class="score-value">{min(score, 100):.0f}%</span>
            </div>
        </div>
        <div class="outfit-items">
            {items_html}
        </div>
    </div>
    """


def get_color_palette_html(colors):
    """Generate color palette dots HTML"""
    dots = ""
    for color in colors:
        if color:
            dots += f'<div class="color-dot" style="background-color: {color};" title="{color}"></div>'
    return f'<div class="color-palette">{dots}</div>'


def get_rating_stars_html(outfit_id, current_rating=0):
    """Generate interactive rating stars HTML"""
    stars = ""
    for i in range(1, 6):
        active = "active" if i <= current_rating else ""
        stars += f'<span class="star {active}" data-rating="{i}">★</span>'
    
    return f"""
    <div class="rating-container" id="rating-{outfit_id}">
        {stars}
    </div>
    """


def get_laundry_badge(in_laundry=False):
    """Generate laundry status badge HTML"""
    if in_laundry:
        return '<span class="laundry-badge">🧺 In Laundry</span>'
    else:
        return '<span class="laundry-badge clean-badge">✓ Clean</span>'


def get_weather_card_html(temp, condition, emoji, feels_like, humidity):
    """Generate weather card HTML"""
    return f"""
    <div class="weather-card animate-fade-in">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="weather-temp">{temp:.0f}°C</div>
                <div style="color: var(--text-secondary); font-size: 1.1rem;">
                    Feels like {feels_like:.0f}°C • {condition}
                </div>
                <div style="color: var(--text-muted); margin-top: 8px;">
                    💧 {humidity}% humidity
                </div>
            </div>
            <div class="weather-icon">{emoji}</div>
        </div>
    </div>
    """


def get_home_hero_html(total_clothes, total_outfits):
    """Generate home page hero section HTML"""
    return f"""
    <div class="animate-fade-in" style="text-align: center; padding: 40px 0;">
        <div style="font-size: 5rem; margin-bottom: 20px;" class="animate-float">👔</div>
        <h1 style="font-size: 3rem; margin-bottom: 10px;">AI Outfit Assistant</h1>
        <p style="color: var(--text-secondary); font-size: 1.2rem; margin-bottom: 40px;">
            Your personal stylist powered by AI
        </p>
        
        <div style="display: flex; justify-content: center; gap: 40px; margin-top: 40px;">
            <div class="profile-stat">
                <div class="profile-stat-value">{total_clothes}</div>
                <div class="profile-stat-label">Items in Wardrobe</div>
            </div>
            <div class="profile-stat">
                <div class="profile-stat-value">{total_outfits}</div>
                <div class="profile-stat-label">Outfits Created</div>
            </div>
            <div class="profile-stat">
                <div class="profile-stat-value">AI</div>
                <div class="profile-stat-label">Powered Matching</div>
            </div>
        </div>
    </div>
    """
