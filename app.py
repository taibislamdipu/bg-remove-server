import os
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
from rembg import remove
from io import BytesIO
from flask_cors import CORS

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

        with open(file_path, 'rb') as image_file:
            input_image = image_file.read()
            output_image = remove(input_image)

        os.remove(file_path)

        output_buffer = BytesIO(output_image)
        output_buffer.seek(0)
        return send_file(output_buffer, mimetype='image/png')

    return {'error': 'Invalid file'}, 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)  # Listen on port 80
