import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import io
from PIL import Image

app = Flask(__name__)
CORS(app)  # Enable CORS

# Initialize EasyOCR reader
reader = easyocr.Reader(['fr', 'en'])

@app.route('/ocr', methods=['POST'])
def ocr():
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({"error": "No image provided"}), 400

    # Decode base64 image
    image_data = data['image']
    image = Image.open(io.BytesIO(base64.b64decode(image_data)))
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
