# Installation Guide

## Backend Setup
1. Navigate to the project backend:
   ```bash
   cd guardian-ai
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```
2. Launch the backend server:
   ```bash
   python backend/main.py
   ```

## Frontend Setup
1. Open a new terminal session and install Node modules:
   ```bash
   cd guardian-ai/frontend
   npm install
   ```
2. Launch the Vite local dev server:
   ```bash
   npm run dev
   ```
