from flask import Flask, request, jsonify
from flask_cors import CORS
import layoutparser as lp
from PIL import Image
import io
import base64
import numpy as np
import cv2

app = Flask(__name__)
CORS(app)

# Initialize the layout model
# Using a pre-trained model from LayoutParser
# You can change this to other models like 'lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config'
model = None

def get_model():
    """Lazy load the model to avoid loading on import"""
    global model
    if model is None:
        # Try Detectron2 models first (more accurate for complex layouts)
        model_paths = [
            # Detectron2 models - more accurate for complex newspaper layouts
            'lp://detectron2/PubLayNet/faster_rcnn_R_50_FPN_3x/config',
            'lp://detectron2/PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
            # Fallback to EfficientDet if Detectron2 not available
            'lp://efficientdet/PubLayNet',
        ]
        
        for model_path in model_paths:
            try:
                print(f"Trying to load model: {model_path}")
                model = lp.AutoLayoutModel(model_path)
                if model is not None:
                    print(f"Model loaded successfully! Type: {type(model)}")
                    break
                else:
                    print(f"Model returned None for: {model_path}")
            except Exception as e:
                print(f"Error loading {model_path}: {e}")
                continue
        
        if model is None:
            raise RuntimeError("Failed to load any model. Please check your internet connection and dependencies.")
    
    return model

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Layout Parser API is running'})

@app.route('/api/parse-layout', methods=['POST'])
def parse_layout():
    """Parse layout from uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert PIL Image to numpy array (RGB)
        image_np = np.array(image.convert('RGB'))
        
        # Preprocess image for better detection
        # Resize if image is too large (models work better with reasonable sizes)
        height, width = image_np.shape[:2]
        max_dimension = 2000
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image_np = cv2.resize(image_np, (new_width, new_height), interpolation=cv2.INTER_AREA)
            print(f"Resized image from {width}x{height} to {new_width}x{new_height}")
        
        # Get model and detect layout
        layout_model = get_model()
        if layout_model is None:
            return jsonify({'error': 'Model failed to load. Please check server logs.'}), 500
        
        print(f"Detecting layout for image of size: {image_np.shape}")
        
        # Use lower confidence threshold for better detection of all elements
        # and enable additional detection parameters for complex layouts
        try:
            # Try with confidence threshold parameter if supported
            layout = layout_model.detect(image_np, return_response=True)
            # Some models return a response object, extract layout from it
            if hasattr(layout, 'layout'):
                layout = layout.layout
        except:
            # Fallback to standard detection
            layout = layout_model.detect(image_np)
        
        # Filter by confidence score - adjust threshold based on model type
        # Lower threshold catches more elements but may include false positives
        # Higher threshold is more accurate but may miss some elements
        confidence_threshold = 0.15  # Lower threshold for better recall
        
        original_count = len(layout)
        filtered_layout = lp.Layout([block for block in layout if block.score > confidence_threshold])
        
        print(f"Detected {original_count} layout elements (filtered to {len(filtered_layout)} with confidence > {confidence_threshold})")
        
        # Sort by confidence score (highest first) for better visualization
        filtered_layout = lp.Layout(sorted(filtered_layout, key=lambda x: x.score, reverse=True))
        
        # Use filtered layout for better accuracy
        layout = filtered_layout
        
        # Convert layout to JSON-serializable format
        layout_data = []
        for element in layout:
            layout_data.append({
                'type': str(element.type),
                'score': float(element.score),
                'block': {
                    'x_1': float(element.block.x_1),
                    'y_1': float(element.block.y_1),
                    'x_2': float(element.block.x_2),
                    'y_2': float(element.block.y_2),
                    'width': float(element.block.width),
                    'height': float(element.block.height)
                }
            })
        
        # Create annotated image
        annotated_image = image_np.copy()
        
        # Color mapping for different element types
        color_map = {
            'Text': (0, 255, 0),      # Green
            'Title': (255, 0, 0),     # Blue
            'Figure': (0, 0, 255),    # Red
            'Table': (255, 165, 0),   # Orange
            'List': (255, 0, 255),    # Magenta
        }
        
        # Draw bounding boxes on the image with color coding
        for element in layout:
            x_1, y_1, x_2, y_2 = element.block.coordinates
            x_1, y_1, x_2, y_2 = int(x_1), int(y_1), int(x_2), int(y_2)
            
            # Get color based on element type
            element_type = str(element.type)
            color = color_map.get(element_type, (255, 255, 0))  # Yellow default
            
            # Draw rectangle with thicker lines for better visibility
            cv2.rectangle(annotated_image, (x_1, y_1), (x_2, y_2), color, 3)
            
            # Add label with background for better readability
            label = f"{element_type} ({element.score:.2f})"
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            # Draw background rectangle for text
            cv2.rectangle(
                annotated_image,
                (x_1, y_1 - text_height - 10),
                (x_1 + text_width, y_1),
                color,
                -1
            )
            # Draw text in white
            cv2.putText(
                annotated_image, label,
                (x_1, y_1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
            )
        
        # Convert annotated image to base64
        annotated_pil = Image.fromarray(annotated_image)
        buffer = io.BytesIO()
        annotated_pil.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'layout': layout_data,
            'image_with_layout': image_base64,
            'element_count': len(layout_data)
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Layout Parser API...")
    print("Loading model (this may take a moment on first run)...")
    # Pre-load the model
    try:
        loaded_model = get_model()
        if loaded_model is not None:
            print(f"Model pre-loaded successfully! Type: {type(loaded_model)}")
        else:
            print("Warning: Model is None after loading")
    except Exception as e:
        print(f"Warning: Could not pre-load model: {e}")
        import traceback
        traceback.print_exc()
        print("Model will be loaded on first request")
    
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

