# Quick Start Guide

## Quick Setup (5 minutes)

### Step 1: Install Dependencies

**Frontend:**
```bash
npm install
```

**Backend:**
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application

**Option A: Use the startup script (macOS/Linux)**
```bash
./start.sh
```

**Option B: Run manually**

Terminal 1 - Backend:
```bash
cd backend
python app.py
```

Terminal 2 - Frontend:
```bash
npm start
```

### Step 3: Use the App

1. Open `http://localhost:3000` in your browser
2. Upload a newspaper image
3. Click "Parse Layout"
4. View the results!

## First Run Notes

- The first time you run the backend, it will download the pre-trained model (this may take a few minutes)
- The model will be cached for future use
- Processing time depends on your hardware (GPU recommended for faster processing)

## Troubleshooting

**Backend won't start:**
- Make sure Python 3.8+ is installed
- Install dependencies: `pip install -r requirements.txt`
- Check if port 5000 is available

**Frontend won't start:**
- Make sure Node.js 14+ is installed
- Install dependencies: `npm install`
- Check if port 3000 is available

**Model loading errors:**
- Ensure you have internet connection (for first-time model download)
- Check available disk space (models can be several GB)
- Try restarting the backend server

## Need Help?

Check the main [README.md](README.md) for more detailed information.

