from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import struct
import traceback

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def extract_images(pur_file_path):
    try:
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
        print(f"✅ 추출 완료: {count}장")
        return count
    except Exception as e:
        print("❌ extract_images 에러:", e)
        traceback.print_exc()
        return 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        print("📥 업로드 요청 들어옴")
        for f in os.listdir(OUTPUT_FOLDER):
            os.remove(os.path.join(OUTPUT_FOLDER, f))
        file = request.files['pureref']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        print(f"📁 저장된 파일 경로: {filepath}")
        count = extract_images(filepath)
        if count == 0:
            print("⚠️ 이미지 추출 0장")
            return jsonify([]), 200
        images = [f'/output_images/image_{i:03}.png' for i in range(count)]
        return jsonify(images)
    except Exception as e:
        print("❌ 업로드 처리 중 에러:", e)
        traceback.print_exc()
        return "Upload failed", 500

@app.route('/output_images/<path:filename>')
def serve_image(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)