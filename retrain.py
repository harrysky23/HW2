import pandas as pd
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Configuration
BASE_DATA_FILE = "base_data.csv"
FEEDBACK_DATA_FILE = "feedback_data.csv"
MODEL_FILE = "model.pkl"

def retrain_model():
    print("Starting retraining process...")
    
    # Load base dataset
    if os.path.exists(BASE_DATA_FILE):
        base_df = pd.read_csv(BASE_DATA_FILE)
        print(f"Loaded {len(base_df)} samples from base data.")
    else:
        print("Warning: Base data not found. Continuing with feedback only if available.")
        base_df = pd.DataFrame(columns=['text', 'label'])
        
    # Load feedback dataset
    if os.path.exists(FEEDBACK_DATA_FILE):
        feedback_df = pd.read_csv(FEEDBACK_DATA_FILE)
        print(f"Loaded {len(feedback_df)} samples from feedback data.")
    else:
        feedback_df = pd.DataFrame(columns=['text', 'label'])
        print("Note: No feedback data found.")
        
    # Merge datasets
    combined_df = pd.concat([base_df, feedback_df], ignore_index=True)
    
    if len(combined_df) == 0:
        print("Error: No data available for retraining.")
        return False
        
    print(f"Total samples for retraining: {len(combined_df)}")
    
    # It's an MLOps best practice to drop exact duplicates if they heavily skew the model
    # We will keep duplicates here since feedback might reinforce a specific pattern,
    # but in a production environment, deduplication logic goes here.
    
    X = combined_df['text']
    y = combined_df['label']
    
    # Re-create pipeline 
    # (In dynamic systems, we could warm-start the model, but full retrain is safer for pipelines)
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=5000)),
        ('clf', LogisticRegression(random_state=42))
    ])
    
    # Retrain
    print("Fitting model...")
    pipeline.fit(X, y)
    
    score = pipeline.score(X, y)
    print(f"Retraining Accuracy (on all data): {score * 100:.2f}%")
    
    # Overwrite the old model
    joblib.dump(pipeline, MODEL_FILE)
    print(f"Model successfully updated and saved to {MODEL_FILE}")
    
    return True

if __name__ == "__main__":
    print("--- Model Retraining (Feedback Loop) ---")
    retrain_model()
