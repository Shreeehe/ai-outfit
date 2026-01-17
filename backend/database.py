# database.py - Database setup for FastAPI
import sqlite3
from contextlib import contextmanager
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'wardrobe.db')

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db():
    """Context manager for database connection"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database tables"""
    with get_db() as conn:
        c = conn.cursor()
        
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
                image_hash TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS outfits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                top_id INTEGER,
                bottom_id INTEGER,
                shoes_id INTEGER,
                dress_id INTEGER,
                outerwear_id INTEGER,
                occasion TEXT,
                weather_temp REAL,
                weather_condition TEXT,
                worn_at TEXT
            )
        ''')
        
        # Migration for existing DB
        try:
            c.execute('ALTER TABLE outfits ADD COLUMN outerwear_id INTEGER')
        except sqlite3.OperationalError:
            pass
            
        try:
            c.execute('ALTER TABLE clothes ADD COLUMN image_hash TEXT')
        except sqlite3.OperationalError:
            pass
            
        conn.commit()

# Initialize on import
init_db()
