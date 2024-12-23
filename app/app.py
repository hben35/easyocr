from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import io
from PIL import Image
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS

# Initialize EasyOCR reader with optimized parameters
reader = easyocr.Reader(['fr', 'en'], gpu=True, batch_size=16, workers=4)

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

        # Read text from the image with optimized parameters
        result = reader.readtext(image_path, batch_size=16, workers=4, decoder='beamsearch', beamWidth=5, paragraph=True, low_text=0.4, link_threshold=0.4)

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
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
