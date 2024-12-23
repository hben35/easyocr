from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import io
from PIL import Image
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS

# Initialize EasyOCR reader
reader = easyocr.Reader(['fr', 'en'])

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

        # Read text from the image
        result = reader.readtext(image_path, batch_size=8, workers=2)

        # Convert results to serializable types
        serializable_result = [
            {
                "bbox": [[int(coord) for coord in point] for point in item[0]],
                "text": item[1],
                "confidence": float(item[2])
            }
            for item in result
        ]

        return jsonify(serializable_result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
