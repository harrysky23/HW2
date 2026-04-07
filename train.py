import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import os

# Configuration
DATA_FILE = "base_data.csv"
MODEL_FILE = "model.pkl"

def train_model():
    print(f"Loading data from {DATA_FILE}...")
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found. Cannot train model.")
        return False
        
    df = pd.read_csv(DATA_FILE)
    
    if len(df) == 0:
        print("Dataset is empty. Cannot train.")
        return False
        
    print(f"Training on {len(df)} samples...")
    X = df['text']
    y = df['label']
    
    # Create an ML Pipeline with TF-IDF Vectorizer and Logistic Regression
    # We use TF-IDF because it's an excellent baseline for text classification
    # Logistic Regression gives us probabilties (confidence scores) effortlessly.
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=5000)),
        ('clf', LogisticRegression(random_state=42))
    ])
    
    # Train the model
    pipeline.fit(X, y)
    
    # Evaluate briefly (accuracy on training set just for log verification)
    score = pipeline.score(X, y)
    print(f"Training Accuracy: {score * 100:.2f}%")
    
    # Serialize the trained model to disk
    joblib.dump(pipeline, MODEL_FILE)
    print(f"Model successfully saved to {MODEL_FILE}")
    return True

if __name__ == "__main__":
    print("--- Initial Model Training ---")
    train_model()
