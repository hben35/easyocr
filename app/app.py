from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import io
from PIL import Image
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS

# Initialize EasyOCR reader with GPU
reader = easyocr.Reader(['fr'], detector='dbnet18')

@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "No image provided"}), 400

        # Handle base64 image
        image_data = data['image']
        if image_data.startswith('data:image/jpeg;base64,'):
            image_data = image_data.replace('data:image/jpeg;base64,', '')
        elif image_data.startswith('data:image/png;base64,'):
            image_data = image_data.replace('data:image/png;base64,', '')

        # Decode the base64 image
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))

        # Convert RGBA to RGB if necessary
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        image_path = "./temp_image.jpg"
        image.save(image_path)

        # Get parameters from URL or set defaults
        batch_size = request.args.get('batch_size', default=16, type=int)
        workers = request.args.get('workers', default=4, type=int)
        decoder = request.args.get('decoder', default=None, type=str)
        beamWidth = request.args.get('beamWidth', default=None, type=int)
        width_ths = request.args.get('width_ths', default=None, type=float)
        text_threshold = request.args.get('text_threshold', default=0.7, type=float)
        low_text = request.args.get('low_text', default=0.4, type=float)
        link_threshold = request.args.get('link_threshold', default=0.4, type=float)
        mag_ratio = request.args.get('mag_ratio', default=1.0, type=float)

        # Create parameters dictionary
        params = {
            'batch_size': batch_size,
            'workers': workers,
            'text_threshold': text_threshold,
            'low_text': low_text,
            'link_threshold': link_threshold,
            'mag_ratio': mag_ratio
        }
        if decoder:
            params['decoder'] = decoder
        if beamWidth:
            params['beamWidth'] = beamWidth
        if width_ths:
            params['width_ths'] = width_ths

        # Read text from the image with specified parameters
        try:
            result = reader.readtext(image_path, **params)
        except Exception as e:
            print(f"Error with parameters: {e}")
            return jsonify({"error": str(e)}), 500

        # Check if result is empty and log appropriate messages
        if not result:
            return jsonify({"error": "No text detected"}), 200

        # Convert results to serializable types
        serializable_result = []
        for item in result:
            if len(item) == 3 and len(item[0]) == 4:  # Ensure bbox has 4 points and item has 3 elements
                serializable_result.append({
                    "bbox": [[int(coord) for coord in point] for point in item[0]],
                    "text": item[1],
                    "confidence": float(item[2])
                })

        return jsonify(serializable_result)

    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
