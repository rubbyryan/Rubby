import os
import librosa
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from joblib import dump
import glob

def extract_features(file_path, mfcc=True, spectral_entropy=True):
    """
    Extract audio features from file
    """
    try:
        audio, sample_rate = librosa.load(file_path, res_type='kaiser_fast')
        
        features = []
        
        # MFCCs
        if mfcc:
            mfccs = np.mean(librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40).T, axis=0)
            features.extend(mfccs)
        
        # Spectral Entropy (noise-robust)
        if spectral_entropy:
            spectral = np.abs(librosa.stft(audio))
            spectral_entropy = librosa.feature.spectral_flatness(y=audio)
            features.extend(np.mean(spectral_entropy.T, axis=0))
        
        return features
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def load_data(dataset_path):
    """
    Load dataset and extract features
    """
    scream_files = glob.glob(os.path.join(dataset_path, "scream", "*.wav"))
    non_scream_files = glob.glob(os.path.join(dataset_path, "non_scream", "*.wav"))

    print(f"Found {len(scream_files)} scream files.")
    print(f"Found {len(non_scream_files)} non-scream files.")

    X = []
    y = []

    for file in scream_files:
        features = extract_features(file)
        if features:
            X.append(features)
            y.append(1)  # 1 for scream

    for file in non_scream_files:
        features = extract_features(file)
        if features:
            X.append(features)
            y.append(0)  # 0 for non-scream

    return np.array(X), np.array(y)

def train_model():
    # Replace with your actual dataset path
    dataset_path = r"C:\Users\user\Downloads\Dataset"
    
    print("Loading data...")
    X, y = load_data(dataset_path)
    
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training model...")
    model = make_pipeline(
        StandardScaler(),
        SVC(kernel='rbf', C=10, gamma=0.01, probability=True)
    )
    
    model.fit(X_train, y_train)
    
    print("Evaluating model...")
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Train accuracy: {train_score:.2f}")
    print(f"Test accuracy: {test_score:.2f}")
    
    print("Saving model...")
    dump(model, 'scream_model.pkl')
    
    return model

if __name__ == "__main__":
    train_model()