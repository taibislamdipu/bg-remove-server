import os
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
from rembg import remove
from io import BytesIO
from flask_cors import CORS
import piexif

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://192.168.20.22:3000"]) 

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
API_KEY = "1234"  # Set your API key here

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/api/v1/remove-background', methods=['POST'])
def remove_background():
    if 'image_file' not in request.files:
        return {'error': 'No file part'}, 400

    # Check if the API key is provided in the request headers
    if 'x-api-key' not in request.headers:
        return {'error': 'API key required'}, 401

    if request.headers['x-api-key'] != API_KEY:
        return {'error': 'Invalid API key'}, 401

    file = request.files['image_file']
    
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Check and correct orientation
        orientation = 1  # default orientation
        exif_data = piexif.load(file_path)
        if '0th' in exif_data and piexif.ImageIFD.Orientation in exif_data['0th']:
            orientation = exif_data['0th'][piexif.ImageIFD.Orientation]

        # Open the image using rembg
        with open(file_path, 'rb') as f:
            input_image_bytes = f.read()

        # Remove the background
        output_image_bytes = remove(input_image_bytes)

        # Create output file
        output_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.png')
        with open(output_image_path, 'wb') as f:
            f.write(output_image_bytes)

        # Clean up the saved file
        os.remove(file_path)

        return send_file(output_image_path, mimetype='image/png')

    return {'error': 'Invalid file'}, 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))  
    app.run(debug=True, host='0.0.0.0', port=port)
