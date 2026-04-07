import os
import csv
import joblib
import subprocess
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Configuration
MODEL_FILE = "model.pkl"
FEEDBACK_FILE = "feedback_data.csv"

# Global variable to hold the trained model in memory
model_pipeline = None

def load_model():
    """Load the model from disk into the global variable."""
    global model_pipeline
    if os.path.exists(MODEL_FILE):
        model_pipeline = joblib.load(MODEL_FILE)
        return True
    return False

# Initialize model on startup
load_model()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400
        
    text = data["text"].strip()
    if not text:
        return jsonify({"error": "Empty text"}), 400
        
    if model_pipeline is None:
        return jsonify({"error": "Model not loaded. Please train first."}), 503
        
    # Get prediction and probability
    # pipeline.predict() returns an array of label strings
    predicted_label = model_pipeline.predict([text])[0]
    
    # pipeline.predict_proba() returns probabilities for classes.
    # We find the index of the predicted label from classes_ to get its confidence.
    classes = list(model_pipeline.classes_)
    class_idx = classes.index(predicted_label)
    probabilities = model_pipeline.predict_proba([text])[0]
    confidence = probabilities[class_idx]
    
    return jsonify({
        "prediction": predicted_label,
        "confidence": float(confidence)
    })

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    if not data or "text" not in data or "label" not in data:
        return jsonify({"error": "Missing text or label"}), 400
        
    text = data["text"].strip()
    label = data["label"].strip()
    
    # Simple validation
    if label not in ["Positive", "Negative"]:
        return jsonify({"error": "Invalid label"}), 400
        
    # Append to feedback_data.csv
    with open(FEEDBACK_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Handle cases where commas in text might break CSV by quoting
        writer.writerow([text, label])
        
    return jsonify({"success": True, "message": "Feedback recorded."})

@app.route("/retrain", methods=["POST"])
def retrain():
    """
    Note for demonstration:
    In a real production MLOps system, retraining is usually handled synchronously 
    through a separate data pipeline orchestrator (like Apache Airflow) or background 
    job system (like Celery), since it can take hours or days to run. 
    Here, because the dataset is tiny, we perform retraining synchronously.
    """
    try:
        # Run the retrain.py script as a subprocess
        result = subprocess.run(["python", "retrain.py"], capture_output=True, text=True, check=True)
        
        # Reload the newly updated model into the Flask application's memory
        if load_model():
            output_msg = format_retrain_output(result.stdout)
            return jsonify({
                "success": True, 
                "message": "Model retrained and loaded successfully.",
                "logs": output_msg
            })
        else:
            return jsonify({
                "success": False, 
                "error": "Retrain script ran, but model file was not found."
            }), 500
            
    except subprocess.CalledProcessError as e:
        return jsonify({
            "success": False, 
            "error": f"Retraining failed. Output: {e.output}"
        }), 500

def format_retrain_output(stdout_raw):
    """Utility to clean up stdout for UI display"""
    return [line for line in stdout_raw.split("\n") if line.strip()]

if __name__ == "__main__":
    # Ensure model exists before running, if not prompt user.
    if not os.path.exists(MODEL_FILE):
        print("Warning: model.pkl not found! Please run 'python train.py' first.")
    
    app.run(debug=True, port=5000)
# Test CI/CD trigger
