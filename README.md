# 📰 Newspaper Layout Parser

**Repository Name:** `newspaper-layout-parser` or `document-layout-analyzer`

A full-stack web application for analyzing and parsing newspaper document layouts using deep learning. Upload newspaper images and get detailed layout analysis with element detection, bounding boxes, and classification using state-of-the-art computer vision models.

## Description

Newspaper Layout Parser is a React + Flask application that leverages [Layout-Parser](https://github.com/Layout-Parser/layout-parser) and Detectron2 to automatically detect and classify layout elements in newspaper images. The application identifies text blocks, titles, figures, tables, and other document components, providing visual annotations and detailed metadata for each detected element.

**Key Features:**
- 🖼️ Drag-and-drop image upload interface
- 🔍 Deep learning-based layout detection (Detectron2/PubLayNet)
- 📊 Visual annotations with bounding boxes
- 📋 Detailed element classification and confidence scores
- 🎨 Clean, minimalist black and white UI
- ⚡ Real-time processing with Flask backend

## Features

- 🖼️ Upload newspaper images via drag-and-drop or file selection
- 🔍 Automatic layout detection using deep learning models
- 📊 Visual annotation of detected layout elements
- 📋 Detailed information about each detected element (type, confidence, coordinates)
- 🎨 Modern, responsive UI

## Prerequisites

- **Node.js** (v14 or higher) and npm
- **Python** (v3.8 or higher) and pip
- **CUDA-capable GPU** (optional, but recommended for faster processing)

## Installation

### 1. Install Frontend Dependencies

```bash
npm install
```

### 2. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

**Note:** If you want to use Detectron2-based models, you may need additional setup. See the [Layout-Parser installation guide](https://github.com/Layout-Parser/layout-parser/blob/main/installation.md) for details.

## Running the Application

### 1. Start the Backend Server

In one terminal window:

```bash
cd backend
python app.py
```

The backend will start on `http://localhost:5000`. The first run may take some time as it downloads the pre-trained model.

### 2. Start the React Frontend

In another terminal window:

```bash
npm start
```

The frontend will start on `http://localhost:3000` and automatically open in your browser.

## Usage

1. Open the application in your browser (usually `http://localhost:3000`)
2. Click the upload area or drag and drop a newspaper image
3. Click "Parse Layout" to analyze the image
4. View the annotated image and detailed layout information

## How It Works

### Architecture Overview

The application follows a client-server architecture:

1. **Frontend (React)**: Provides the user interface for image upload and result visualization
2. **Backend (Flask)**: Handles image processing and layout detection using deep learning models
3. **ML Pipeline**: Uses Layout-Parser library with Detectron2 models for accurate layout detection

### Model Selection & Loading

The backend automatically selects the best available model in this order:

1. **Detectron2 Models** (Most Accurate):
   - `lp://detectron2/PubLayNet/faster_rcnn_R_50_FPN_3x/config` - Faster R-CNN model
   - `lp://detectron2/PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config` - Mask R-CNN model
   - These models are trained on PubLayNet dataset and provide high accuracy for complex layouts

2. **EfficientDet Model** (Fallback):
   - `lp://efficientdet/PubLayNet` - Lightweight model, faster but less accurate

**Model Accuracy Comparison:**
- **Detectron2**: Slower but much more accurate for complex newspaper layouts (recommended)
- **EfficientDet**: Fast and lightweight, good for simple documents

The model is loaded once at startup and reused for all requests, ensuring fast response times after the initial load.

### Image Processing Pipeline

When an image is uploaded, the following steps occur:

1. **Image Reception**: Flask receives the image via multipart/form-data
2. **Image Preprocessing**:
   - Convert to RGB format
   - Resize if image exceeds 2000px on any dimension (maintains aspect ratio)
   - Convert PIL Image to NumPy array for model processing
3. **Layout Detection**:
   - Pass preprocessed image to the loaded model
   - Model detects layout elements with bounding boxes and confidence scores
4. **Post-Processing**:
   - Filter elements by confidence threshold (>0.15)
   - Sort by confidence score (highest first)
   - Extract metadata (type, coordinates, confidence)
5. **Visualization**:
   - Draw bounding boxes on the original image
   - Color-code by element type (Text, Title, Figure, Table, List)
   - Add labels with element type and confidence score
6. **Response Generation**:
   - Convert annotated image to base64
   - Package layout data and annotated image in JSON response

### Detection Process

The layout detection model identifies and classifies document elements:

**Detected Element Types:**
- **Text**: Body text blocks and paragraphs
- **Title**: Headlines and section titles
- **Figure**: Images, photos, and illustrations
- **Table**: Tabular data structures
- **List**: Bulleted or numbered lists

**Detection Parameters:**
- **Confidence Threshold**: 0.15 (configurable in `backend/app.py`)
  - Lower threshold = more elements detected (may include false positives)
  - Higher threshold = fewer but more confident detections
- **Non-Maximum Suppression**: Applied automatically by the model to remove overlapping detections

### Response Format

The API returns a JSON response with:

```json
{
  "success": true,
  "layout": [
    {
      "type": "Text",
      "score": 0.95,
      "block": {
        "x_1": 100,
        "y_1": 200,
        "x_2": 500,
        "y_2": 400,
        "width": 400,
        "height": 200
      }
    }
  ],
  "image_with_layout": "base64_encoded_image",
  "element_count": 15
}
```

### Model Installation & Accuracy

**For Best Accuracy (Recommended):**

Install Detectron2 for significantly better detection accuracy:

```bash
# macOS (CPU)
pip install 'git+https://github.com/facebookresearch/detectron2.git@v0.4#egg=detectron2'

# Linux
pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch2.1/index.html
```

After installation, restart the backend. It will automatically use Detectron2 models.

**Note:** Detectron2 requires Pillow < 10.0.0 (already configured in requirements.txt)

### Performance Considerations

- **First Request**: Slow (model loading and downloading if not cached)
- **Subsequent Requests**: Fast (model stays in memory)
- **Image Size**: Large images are automatically resized for optimal performance
- **Hardware**: GPU acceleration significantly speeds up processing (if available)
- **Model Size**: Detectron2 models are ~330MB, EfficientDet is ~47MB

### Current Optimizations

1. **Image Preprocessing**: Automatic resizing of large images (max 2000px)
2. **Confidence Filtering**: Removes low-confidence detections (threshold: 0.15)
3. **Model Caching**: Model loaded once and reused for all requests
4. **Efficient Model Selection**: Tries most accurate models first, falls back if unavailable

## API Endpoints

- `GET /api/health` - Health check endpoint
- `POST /api/parse-layout` - Upload an image and get layout analysis
  - **Request:** multipart/form-data with `image` field
  - **Response:** JSON with layout data and annotated image

## Project Structure

```
layout parser/
├── backend/
│   └── app.py              # Flask API server
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/
│   │   ├── LayoutParser.js # Main component
│   │   └── LayoutParser.css
│   ├── App.js              # App component
│   ├── App.css
│   ├── index.js            # Entry point
│   └── index.css
├── package.json            # Frontend dependencies
├── requirements.txt        # Backend dependencies
└── README.md
```

## Configuration

You can configure the API URL by setting the `REACT_APP_API_URL` environment variable:

```bash
REACT_APP_API_URL=http://localhost:5000 npm start
```

## Troubleshooting

### Model Loading Issues

If you encounter issues loading the model:

1. **Internet Connection**: Models are downloaded on first use (~330MB for Detectron2, ~47MB for EfficientDet)
2. **Disk Space**: Ensure sufficient space (models are cached in `~/.cache/`)
3. **Pillow Version**: Detectron2 requires Pillow < 10.0.0 (already in requirements.txt)
4. **Model Path**: The backend automatically tries multiple models - check logs for specific errors

**Manual Model Selection:**
If you want to force a specific model, modify `backend/app.py`:
```python
# In get_model() function, change the model_paths list order
model_paths = [
    'lp://efficientdet/PubLayNet',  # Put preferred model first
    # ... other models
]
```

### Detection Accuracy Issues

If detection results are inaccurate:

1. **Install Detectron2**: Much more accurate than EfficientDet for complex layouts
2. **Image Quality**: Ensure images are clear, well-lit, and not heavily compressed
3. **Confidence Threshold**: Adjust in `backend/app.py` (currently 0.15)
   - Lower (0.1-0.15): More elements detected, may include false positives
   - Higher (0.3-0.5): Fewer but more confident detections
4. **Image Size**: Very large images are auto-resized - ensure important details are visible
5. **Model Type**: Check backend logs to confirm which model is being used

### CORS Issues

If you see CORS errors, make sure:
- The backend is running on port 5000
- Flask-CORS is properly installed
- The frontend is making requests to the correct URL

### Performance

- First request may be slow as the model loads
- Processing time depends on image size and hardware
- Using a GPU significantly speeds up processing

## Technologies Used

- **Frontend:** React, Axios
- **Backend:** Flask, Flask-CORS
- **Layout Detection:** Layout-Parser with Detectron2 (Faster R-CNN / Mask R-CNN) or EfficientDet
- **ML Framework:** Detectron2 (Facebook Research)
- **Image Processing:** Pillow, OpenCV, NumPy
- **Deep Learning:** PyTorch, TorchVision

## License

This project uses Layout-Parser which is licensed under Apache-2.0.

## Contributing

Feel free to submit issues and enhancement requests!

## References

- [Layout-Parser GitHub](https://github.com/Layout-Parser/layout-parser)
- [Layout-Parser Documentation](https://layout-parser.github.io/)

