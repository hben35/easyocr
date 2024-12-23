from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr

app = Flask(__name__)
CORS(app)  # Add this line to enable CORS

# Initialize the EasyOCR reader
reader = easyocr.Reader(['fr', 'en'])

@app.route('/ocr', methods=['POST'])
def ocr():
    image = request.files.get('image')
    if not image:
        return jsonify({"error": "No image provided"}), 400

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
