import os
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
from rembg import remove
from io import BytesIO
from flask_cors import CORS
from PIL import Image

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://192.168.20.22:3000"])  # Explicitly allow requests from your Next.js frontend

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/remove-background', methods=['POST'])
def remove_background():
    if 'image_file' not in request.files:
        return {'error': 'No file part'}, 400

    file = request.files['image_file']
    
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Open the image using PIL
        with Image.open(file_path) as input_image:
            # Convert the image to a byte array
            input_image_bytes = BytesIO()
            input_image.save(input_image_bytes, format='PNG')
            input_image_bytes = input_image_bytes.getvalue()

            # Remove the background
            output_image_bytes = remove(input_image_bytes)

            # Create an Image object from the byte array
            output_image = Image.open(BytesIO(output_image_bytes))

            # Save the output image to a BytesIO object
            output_buffer = BytesIO()
            output_image.save(output_buffer, format='PNG')
            output_buffer.seek(0)

        # Clean up the saved file
        os.remove(file_path)

        return send_file(output_buffer, mimetype='image/png')

    return {'error': 'Invalid file'}, 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the PORT environment variable if available, otherwise default to port 5000
    app.run(debug=True, host='0.0.0.0', port=port)
