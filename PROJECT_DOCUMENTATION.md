# AI Outfit - Feature Documentation
## Project Overview & Android Conversion Proposal

**Document Version:** 1.0  
**Date:** January 9, 2026  
**Current Platform:** Python Streamlit (Web)  
**Target Platform:** Native Android (Kotlin/Jetpack Compose)

---

## 📋 Executive Summary

AI Outfit is an intelligent wardrobe management and outfit recommendation system that uses AI (CLIP model) to classify clothing items and suggest weather-appropriate, color-coordinated outfits based on user preferences and occasion.

### Key Value Propositions
- 🤖 **AI-Powered Classification** - Automatically identifies clothing type, color, pattern, and formality
- 🌤️ **Weather-Aware Suggestions** - Recommends outfits based on current weather conditions
- 🧠 **Learning System** - Learns user preferences from outfit ratings over time
- 🧺 **Laundry Tracking** - Knows which items are unavailable for suggestions

---

## 🎯 Feature List

### 1. Home Dashboard
| Feature | Description | Priority |
|---------|-------------|----------|
| Weather Display | Shows current temperature, condition, feels-like | High |
| Quick Stats | Total clothes, outfits logged, favorites, never worn count | Medium |
| Forgotten Items | Alerts for items not worn in 30+ days | Medium |

### 2. Add Clothes (AI Classification)
| Feature | Description | Priority |
|---------|-------------|----------|
| Camera Capture | Take photo directly in-app | High |
| Gallery Upload | Select existing photos | High |
| AI Classification | Auto-detect: type, color, pattern, formality | High |
| Manual Correction | User can override AI predictions | High |
| Color Picker | Select primary & secondary colors | Medium |
| Formality Selector | Casual, Business-Casual, Formal, Athletic | High |
| Pattern Selection | Solid, Striped, Checkered, Floral, Printed | Medium |
| Weight/Season | Light, Medium, Heavy (for weather matching) | Medium |

### 3. Wardrobe Management
| Feature | Description | Priority |
|---------|-------------|----------|
| Grid View | Display all clothes in responsive grid | High |
| Filter by Type | Top, Bottom, Dress, Shoes, Outerwear | High |
| Sort Options | Newest, Most Worn, Least Worn | Medium |
| Favorite Toggle | Mark items as favorites (❤️) | Medium |
| Laundry Toggle | Mark items as in laundry (🧺) | High |
| Delete Item | Remove from wardrobe with confirmation | High |
| Wear Count | Display how many times each item worn | Low |

### 4. Outfit Suggestions (Recommendation Engine)
| Feature | Description | Priority |
|---------|-------------|----------|
| Occasion Selection | Casual, Work, Gym, Date, Home | High |
| Weather Integration | Fetches live weather data | High |
| Multiple Suggestions | Generate 1-6 outfit options | High |
| Score Display | Each outfit rated 0-100 | Medium |
| Wear Logging | Log selected outfit to history | High |
| Rating System | Rate outfits 1-5 stars | Medium |

### 5. Laundry Basket
| Feature | Description | Priority |
|---------|-------------|----------|
| View Laundry Items | See all items marked as in laundry | High |
| Mark Individual Clean | Return single item to wardrobe | High |
| Mark All Clean | Bulk action for all items | Medium |

### 6. Insights & Analytics
| Feature | Description | Priority |
|---------|-------------|----------|
| Wardrobe Stats | Total items, by type breakdown | Medium |
| Outfit Stats | Total outfits logged | Medium |
| AI Learning Stats | Ratings given, average rating | Low |
| Color Palette | Visual display of wardrobe colors | Low |
| Alerts | Never worn items, underused items | Medium |

### 7. Outfit History
| Feature | Description | Priority |
|---------|-------------|----------|
| Chronological List | Past outfits with dates | Medium |
| Weather Context | Weather when outfit was worn | Low |
| Visual Display | Thumbnails of each outfit item | Medium |

---

## 🧠 AI/ML Components

### Clothing Classifier (CLIP Model)
```
Model: openai/clip-vit-base-patch32
Size: ~350MB (requires optimization for mobile)

Classification Outputs:
├── Clothing Type Detection
│   └── t-shirt, shirt, jeans, dress, sneakers, etc.
├── Formality Analysis
│   └── casual, business-casual, formal, athletic
├── Pattern Recognition
│   └── solid, striped, checkered, floral, printed
├── Season/Weight Detection
│   └── light, medium, heavy
└── Color Extraction
    └── Primary & secondary hex colors (K-means clustering)
```

### Android Consideration:
- **TensorFlow Lite** conversion required
- Consider **TinyCLIP** (~50MB) for mobile
- On-device inference for privacy

### Outfit Recommender Engine
```
Scoring Algorithm (max 100 points):
├── Weather Score (0-25)
│   └── Temperature + condition matching
├── Color Coordination (0-25)
│   └── Neutral matching, complementary colors
├── Pattern Balance (0-15)
│   └── Avoid multiple busy patterns
├── Variety Score (0-20)
│   └── Prefer less-worn items
└── Style Profile Bonus (-10 to +15)
    └── Based on learned preferences
```

---

## 📊 Database Schema

### Tables

#### `clothes`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| image_path | TEXT | Local file path |
| clothing_type | TEXT | top, bottom, dress, shoes, outerwear |
| color_primary | TEXT | Hex color code |
| color_secondary | TEXT | Optional secondary color |
| pattern | TEXT | solid, striped, etc. |
| formality | TEXT | casual, formal, etc. |
| season_weight | TEXT | light, medium, heavy |
| times_worn | INTEGER | Wear counter |
| last_worn | TEXT | ISO timestamp |
| in_laundry | INTEGER | Boolean (0/1) |
| favorite | INTEGER | Boolean (0/1) |
| created_at | TEXT | ISO timestamp |

#### `outfits` (History)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| top_id | INTEGER | FK to clothes |
| bottom_id | INTEGER | FK to clothes |
| shoes_id | INTEGER | FK to clothes |
| dress_id | INTEGER | FK to clothes |
| occasion | TEXT | casual, work, etc. |
| weather_temp | REAL | Temperature when worn |
| weather_condition | TEXT | Weather condition |
| worn_at | TEXT | ISO timestamp |

#### `style_profile` (AI Learning)
| Column | Type | Description |
|--------|------|-------------|
| preference_type | TEXT | color, formality, pattern, occasion |
| preference_value | TEXT | The specific value |
| weight | REAL | Learned weight (0-5) |

#### `outfit_ratings`
| Column | Type | Description |
|--------|------|-------------|
| outfit_id | INTEGER | FK to outfits |
| rating | INTEGER | 1-5 stars |
| feedback | TEXT | Optional feedback |

---

## 🔌 External APIs

### OpenWeatherMap API
- **Endpoint:** `api.openweathermap.org/data/2.5/weather`
- **Data Used:** Temperature, feels_like, condition, humidity
- **Free Tier:** 60 calls/minute, 1M calls/month
- **API Key Required:** Yes (already configured)

---

## 📱 Android Conversion Recommendations

### Recommended Tech Stack
| Component | Technology |
|-----------|------------|
| Language | Kotlin |
| UI Framework | Jetpack Compose |
| Navigation | Navigation-Compose |
| Local Database | Room (SQLite ORM) |
| AI Inference | TensorFlow Lite |
| Weather API | Retrofit |
| Image Loading | Coil |
| Camera | CameraX |
| State Management | ViewModel + StateFlow |

### Development Phases

#### Phase 1: Core UI (Week 1-2)
- [ ] Project setup with dependencies
- [ ] Navigation with bottom bar
- [ ] Home screen with weather
- [ ] Add clothes screen with camera
- [ ] Wardrobe grid view
- [ ] Outfit suggestion screen

#### Phase 2: AI Integration (Week 3-4)
- [ ] TFLite model conversion
- [ ] On-device classification
- [ ] Color extraction
- [ ] Recommendation engine port

#### Phase 3: Features (Week 5-6)
- [ ] Laundry tracking
- [ ] Outfit history
- [ ] Ratings & learning
- [ ] Insights dashboard

#### Phase 4: Polish (Week 7-8)
- [ ] UI/UX refinement
- [ ] Performance optimization
- [ ] Testing on multiple devices
- [ ] Release build

### Estimated Timeline
- **MVP:** 4-6 weeks
- **Full Feature Parity:** 8-10 weeks
- **Polished Release:** 12 weeks

---

## 📁 Current Project Structure

```
AI OUTFIT IDEA/
├── app.py              # Main Streamlit application
├── classifier.py       # CLIP-based clothing classifier
├── recommender.py      # Outfit recommendation engine
├── weather.py          # Weather API service
├── profile.py          # Style learning system
├── styles.py           # UI styling (not needed for Android)
├── wardrobe.db         # SQLite database
├── wardrobe_images/    # Stored clothing images
└── .venv/              # Python virtual environment
```

---

## 🎬 Demo Screenshots

The current Streamlit app demonstrates:
1. **Home Dashboard** - Weather + stats overview
2. **Add Clothes** - Camera input + AI classification
3. **Wardrobe** - Grid view with filters
4. **Get Outfit** - Occasion-based suggestions
5. **Laundry** - Track dirty clothes
6. **Insights** - Analytics dashboard
7. **History** - Past outfit log

---

## ✅ Conclusion

The AI Outfit application is a fully functional wardrobe management system with:
- **7 main feature screens**
- **AI-powered classification** using CLIP
- **Intelligent recommendation engine** with 5 scoring factors
- **Learning system** that improves with user feedback
- **Weather integration** for context-aware suggestions

The system is ready for Android conversion with all core logic portable to Kotlin.

---

**Prepared by:** AI Outfit Development Team  
**Contact:** [Your Email]  
**Repository:** [Your GitHub Link]
