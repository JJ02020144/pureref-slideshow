from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import struct

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def extract_images(pur_file_path):
    with open(pur_file_path, 'rb') as f:
        data = f.read()

    index = 0
    count = 0
    while True:
        start = data.find(b'\x89PNG', index)
        if start == -1:
            break
        end = data.find(b'IEND\xaeB`\x82', start)
        if end == -1:
            break
        end += 8
        img_data = data[start:end]
        img_path = os.path.join(OUTPUT_FOLDER, f'image_{count:03}.png')
        with open(img_path, 'wb') as img_file:
            img_file.write(img_data)
        index = end
        count += 1
    return count

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    for f in os.listdir(OUTPUT_FOLDER):
        os.remove(os.path.join(OUTPUT_FOLDER, f))
    file = request.files['pureref']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    count = extract_images(filepath)
    images = [f'/output_images/image_{i:03}.png' for i in range(count)]
    return jsonify(images)

@app.route('/output_images/<path:filename>')
def serve_image(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)