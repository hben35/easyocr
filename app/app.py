from flask import Flask, request, jsonify
import easyocr

app = Flask(__name__)

# Initialiser le lecteur EasyOCR avec les langues nécessaires
reader = easyocr.Reader(['fr', 'en'])

@app.route('/ocr', methods=['POST'])
def ocr():
    image = request.files.get('image')
    if not image:
        return jsonify({"error": "No image provided"}), 400

    image_path = "./temp_image.jpg"
    image.save(image_path)

    # Lire le texte de l'image
    result = reader.readtext(image_path)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
