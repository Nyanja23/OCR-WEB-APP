from flask import Flask, request, render_template, jsonify
import os
from werkzeug.utils import secure_filename
from ocr.service import extract_text_from_file

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_options', methods=['POST'])
def process_options():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})
    
    # Get options
    preprocess_str = request.form.get('preprocess', 'true')
    use_improved = preprocess_str.lower() == 'true'
    lang = request.form.get('language', 'eng')
    
    # Save temp file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    try:
        full_text, page_texts = extract_text_from_file(file_path, use_improved=use_improved, lang=lang)
        char_count = len(full_text)
        word_count = len(full_text.split())
        return jsonify({
            'success': True,
            'extracted_text': full_text,
            'pages': page_texts,  # For frontend preview
            'char_count': char_count,
            'word_count': word_count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(debug=True)