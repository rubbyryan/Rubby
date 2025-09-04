from flask import Flask, request, jsonify
from flask_cors import CORS
import librosa
import numpy as np
import os
from joblib import load
from pydub import AudioSegment
import tempfile

app = Flask(__name__)
CORS(app)

# Load the trained model
model = load(r'backend/model/scream_model.pkl')

def extract_features(audio_path, mfcc=True, spectral_entropy=True):
    """
    Extract features from audio file
    """
    try:
        audio, sample_rate = librosa.load(audio_path, res_type='kaiser_fast')
        
        features = []
        
        # MFCCs
        if mfcc:
            mfccs = np.mean(librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40).T, axis=0)
            features.extend(mfccs)
        
        # Spectral Entropy (noise-robust)
        if spectral_entropy:
            spectral_entropy = librosa.feature.spectral_flatness(y=audio)
            features.extend(np.mean(spectral_entropy.T, axis=0))
        
        return np.array(features).reshape(1, -1)
    except Exception as e:
        print(f"Error processing audio: {e}")
        return None

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    audio_file = request.files['file']
    
    # Save to temporary file
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp:
            temp_path = temp.name
            audio_file.save(temp_path)
            
            # Convert to WAV if needed
            if not audio_file.filename.lower().endswith('.wav'):
                sound = AudioSegment.from_file(temp_path)
                sound.export(temp_path, format="wav")
            
            # Extract features
            features = extract_features(temp_path)
            if features is None:
                return jsonify({'error': 'Error processing audio'}), 400
            
            # Make prediction
            prediction = model.predict_proba(features)
            scream_prob = prediction[0][1]  # Probability of being a scream
            
            return jsonify({
                'is_scream': bool(scream_prob > 0.5),
                'probability': float(scream_prob),
                'threshold': 0.5
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)