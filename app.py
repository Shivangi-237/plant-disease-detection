from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from model import predict_disease
import os

import model
print("MODEL MODULE CONTAINS:", dir(model))


app = Flask(__name__)

# ─── Configuration ────────────────────────────────────────────────────────────
app.config['UPLOAD_FOLDER']     = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # limit to 5MB
ALLOWED_EXTENSIONS              = {'png', 'jpg', 'jpeg'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# ──────────────────────────────────────────────────────────────────────────────

def allowed_file(filename):
    return (
        '.' in filename and 
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

@app.route('/')
def index():
    # Serve your upload form from templates/index.html
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def upload_and_predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        try:
            pred_class = predict_disease(filepath)
        except Exception:
            os.remove(filepath)
            return jsonify({'error': 'Prediction failed'}), 500
        os.remove(filepath)
        return jsonify({'prediction': pred_class})
    else:
        return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    print("▶️ Starting Flask server…")
    app.run(debug=True)
