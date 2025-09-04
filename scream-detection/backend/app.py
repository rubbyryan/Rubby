from flask import Flask, request, jsonify
from flask_cors import CORS
import librosa
import numpy as np
import os
from joblib import load
from pydub import AudioSegment
import tempfile
from twilio.rest import Client

app = Flask(__name__)
CORS(app)

# Load the trained model
model = load(r'C:\The_Scream detection\scream-detection\backend\model\scream_model.pkl')

TWILIO_ACCOUNT_SID = 'ACf305e0afe77a0bb02e00b4c34896bdf3'
TWILIO_AUTH_TOKEN = '216ba364fe78883222026cfa9c27e0bc'
TWILIO_FROM_NUMBER = '+19593350391'  # Your Twilio number
EMERGENCY_SMS_NUMBER = '+263786201330'  # The number to receive the SMS

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

def send_emergency_sms(probability):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body="A scream was detected, you might need to check on your daughter Rumbi and see if they are okay.",
        from_=TWILIO_FROM_NUMBER,
        to=EMERGENCY_SMS_NUMBER
    )
    print(f"SMS sent: {message.sid}")

def send_emergency_whatsapp(probability):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body="A scream was detected, you might need to check on your pal and see if they are okay.",
        from_='whatsapp:+14155238886',  # Twilio WhatsApp sandbox number
        to='whatsapp:+263786201330'      # Correct WhatsApp number with country code
    )
    print(f"WhatsApp message sent: {message.sid}")
# --- Environmental Listening / Background Model ---
background_features = None
background_count = 0
BACKGROUND_LEARNING_RATE = 0.01  # Adjust for how quickly the model adapts

def update_background(features):
    global background_features, background_count
    if background_features is None:
        background_features = features.copy()
        background_count = 1
    else:
        background_features = (1 - BACKGROUND_LEARNING_RATE) * background_features + BACKGROUND_LEARNING_RATE * features
        background_count += 1

def is_anomalous(features, threshold=2.0):
    if background_features is None:
        return True  # No background yet, treat as anomaly
    dist = np.linalg.norm(features - background_features)
    return dist > threshold
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    audio_file = request.files['file']
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

            # Update background model with "normal" sounds (low scream probability)
            if scream_prob < 0.2:
                update_background(features)

            # Check if this is an anomaly compared to background
            anomaly = is_anomalous(features)

            # Send SMS/WhatsApp if scream detected with high probability and is anomalous
            if scream_prob > 0.7 and anomaly:
                send_emergency_sms(scream_prob)
                send_emergency_whatsapp(scream_prob)

            return jsonify({
                'is_scream': bool(scream_prob > 0.5),
                'probability': float(scream_prob),
                'threshold': 0.5,
                'anomaly': anomaly,
                'background_count': background_count
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