# AI Outfit Idea

AI Outfit Idea is an intelligent wardrobe management application that uses machine learning to categorize clothing and generate personalized outfit recommendations based on weather and occasion.

## Features

- **Automated Classification**: Uses OpenAI CLIP model to automatically detect clothing type, color, pattern, and seasonality.
- **Smart Recommendations**: Generates outfit combinations (Top + Bottom + Shoes, or Dress + Shoes) tailored to current weather conditions.
- **Duplicate Prevention**: Content-hashing ensures no duplicate images are added to the wardrobe.
- **Wardrobe Analytics**: Tracks usage frequency and favorite items.

## Prerequisites

- Python 3.8 or higher
- Node.js and npm

## Installation

### 1. Backend Setup

Navigate to the project root directory and set up the Python environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

## Running the Application

You need to run both the backend and frontend servers simultaneously.

### 1. Start Backend Server

From the project root (with virtual environment activated):

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000.

### 2. Start Frontend Application

From the frontend directory:

```bash
npm run dev
```

The application will be accessible at http://localhost:5173.

## Usage Guide

1.  **Add Clothes**: Upload images of your clothing. The AI will automatically fill in details. Click "Save" to add them to your closet.
2.  **Get Recommendations**: On the Home page, select an occasion (e.g., Casual, Work) to see outfit suggestions based on the current weather.
3.  **Manage Wardrobe**: View your collection in the "Closet" tab. Use individual item deletion or the cleanup tool to remove duplicates.
