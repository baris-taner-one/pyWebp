from flask import Flask,send_from_directory, render_template, request, jsonify
import os
from PIL import Image

app = Flask(__name__, template_folder="templates")

def compress_image(input_path, output_path, quality=80):
    # Resmi aç ve yeniden kaydet
    with Image.open(input_path) as img:
        img.save(output_path, quality=quality, optimize=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/converted_images/<path:filename>')
def serve_converted_image(filename):
    return send_from_directory('converted_images', filename)    

@app.route('/convert', methods=['POST'])
def convert_to_webp_api():
    input_folder = 'uploads'
    output_folder = 'converted_images'
    quality = int(request.form.get('quality'))

    if not os.path.exists(input_folder):
        os.makedirs(input_folder)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    original_files = []
    converted_files = []

    # Gelen dosyaları al
    uploaded_files = request.files.getlist('files')
    for uploaded_file in uploaded_files:
        # Dosyayı yükle
        if uploaded_file.filename != '':
            input_path = os.path.join(input_folder, uploaded_file.filename)
            uploaded_file.save(input_path)

            # Dosyayı dönüştür
            filename_no_ext = os.path.splitext(uploaded_file.filename)[0]
            output_path_compressed = os.path.join(output_folder, filename_no_ext + '_compressed.jpg')
            output_path_webp = os.path.join(output_folder, filename_no_ext + '.webp')
            try:
                # Resmi sıkıştır
                compress_image(input_path, output_path_compressed, quality=quality)

                # Sıkıştırılmış resmi webp'ye dönüştür
                with Image.open(output_path_compressed) as img:
                    img.save(output_path_webp, 'webp', quality=quality)

                # Geçici sıkıştırılmış dosyayı temizle
                os.remove(output_path_compressed)

                # Yüklenen orijinal dosya ve dönüştürülen dosyanın yollarını listeye ekle
                original_files.append(os.path.abspath(input_path))
                converted_files.append(os.path.abspath(output_path_webp))
            except Exception as e:
                print(f"Hata: {e}")
                continue

    return jsonify({'message': 'Dönüştürme işlemi tamamlandı.', 'original_files': original_files, 'converted_files': converted_files})

if __name__ == '__main__':
    app.run(debug=True)
