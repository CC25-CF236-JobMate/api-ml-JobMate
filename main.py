# =================================================================
# IMPORTS
# =================================================================
import os
import pickle
import re
import logging
import io

from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import BaseModel
from dotenv import load_dotenv
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from google.cloud import storage

# =================================================================
# ENVIRONMENT & CONSTANTS
# =================================================================
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN", "default_token")
BUCKET_NAME = os.getenv("BUCKET_NAME")

# =================================================================
# LOGGING SETUP
# =================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# =================================================================
# FLASK APP INITIALIZATION
# =================================================================
app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# =================================================================
# LOAD MODELS & DATA FROM GCS
# =================================================================
try:
    if not BUCKET_NAME:
        raise ValueError("BUCKET_NAME environment variable not set.")

    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    logger.info("✅ Successfully connected to GCS bucket: %s", BUCKET_NAME)

    def load_pickle_from_gcs(file_path):
        """Helper function to download and load a pickle file from GCS."""
        logger.info("-> Loading %s...", file_path)
        blob = bucket.blob(file_path)
        file_bytes = blob.download_as_bytes()
        return pickle.load(io.BytesIO(file_bytes))

    # Memuat semua model .pkl
    unsupervised_vectorizer = load_pickle_from_gcs("models/tfidf_vectorizer.pkl")
    supervised_vectorizer = load_pickle_from_gcs("models/supervised_vectorizer.pkl")
    classifier = load_pickle_from_gcs("models/job_classifier.pkl")

    # Memuat file CSV
    logger.info("-> Loading models/job_metadata.csv...")
    blob_csv = bucket.blob("models/job_metadata.csv")
    job_metadata = pd.read_csv(io.BytesIO(blob_csv.download_as_bytes()))

    # Memuat file .npz
    logger.info("-> Loading models/job_vectors.npz...")
    blob_npz = bucket.blob("models/job_vectors.npz")
    temp_npz_path = "/tmp/job_vectors.npz"
    blob_npz.download_to_filename(temp_npz_path)
    job_vectors = sparse.load_npz(temp_npz_path)

    # Memastikan kolom 'id' ada
    if 'id' not in job_metadata.columns:
        job_metadata.reset_index(inplace=True)
        job_metadata.rename(columns={'index': 'id'}, inplace=True)

    logger.info("✅ All models and data successfully loaded from GCS.")

except Exception as e:
    logger.error("❌ CRITICAL: Failed to load models/data from GCS: %s", str(e), exc_info=True)
    raise RuntimeError("Failed to load models and data from GCS.") from e

# =================================================================
# UTILS
# =================================================================
def basic_preprocess(text: str) -> str:
    """A simple text preprocessing function."""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# =================================================================
# SCHEMAS (Pydantic, opsional untuk validasi input)
# =================================================================
class ResumeInput(BaseModel):
    text: str

class TextInput(BaseModel):
    description: str

# =================================================================
# API ROUTES / ENDPOINTS
# =================================================================
@app.before_request
def check_auth():
    """Middleware to check API token for all routes except root and healthcheck."""
    # TAMBAHKAN INI: Jika request adalah preflight OPTIONS, lewati saja.
    # Biarkan Flask-CORS yang menanganinya.
    if request.method == 'OPTIONS':
        return

    if request.endpoint in ['root', 'healthcheck']:
        return
    if "Authorization" not in request.headers or request.headers["Authorization"] != f"Bearer {API_TOKEN}":
        return jsonify({"detail": "Unauthorized"}), 401

@app.route("/")
def root():
    """Root endpoint to show API status and available routes."""
    return jsonify({
        "message": "✅ JobMate ML API is running 🚀",
        "docs": "Not available.",
        "health": "/healthcheck",
        "endpoints": [
            "POST /recommend",
            "POST /predict-category",
            "GET /categories",
            "GET /jobs/{job_id}"
        ]
    })

@app.route("/healthcheck")
def healthcheck():
    """Healthcheck endpoint."""
    return jsonify({"status": "ok"})

@app.route("/recommend", methods=["POST"])
def recommend_jobs():
    """Recommends jobs based on resume text."""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"detail": "Missing 'text' in request body"}), 400

    text = basic_preprocess(data.get("text"))
    vector = unsupervised_vectorizer.transform([text])
    similarities = cosine_similarity(vector, job_vectors).flatten()
    top_indices = similarities.argsort()[-5:][::-1]
    top_jobs = job_metadata.iloc[top_indices]

    recommendations = [
        {
            "job_id": int(row.id),
            "job_title": row._asdict().get("Job Title", "N/A"),
            "description": row._asdict().get("Job Description", "")[:300],
            "similarity_score": round(float(similarities[idx]), 4)
        }
        for idx, row in zip(top_indices, top_jobs.itertuples(index=False))
    ]
    
    return jsonify({"recommendations": recommendations})

@app.route("/predict-category", methods=["POST"])
def predict_category():
    """Predicts job category from a job description."""
    data = request.get_json()
    if not data or 'description' not in data:
        return jsonify({"detail": "Missing 'description' in request body"}), 400
    
    description = basic_preprocess(data.get("description"))
    
    try:
        vec = supervised_vectorizer.transform([description])
        pred = classifier.predict(vec)[0]
        return jsonify({"predicted_category": pred})
    except Exception as e:
        logger.error("Error during prediction: %s", str(e))
        return jsonify({"detail": "Internal Server Error"}), 500

@app.route("/categories", methods=["GET"])
def get_all_categories():
    """Returns a list of all available job categories."""
    try:
        categories = sorted(list(classifier.classes_))
        return jsonify({"categories": categories})
    except Exception as e:
        logger.error("Error getting categories: %s", str(e))
        return jsonify({"detail": "Internal Server Error"}), 500

@app.route("/jobs/<int:job_id>", methods=["GET"])
def get_job_detail(job_id):
    """Returns details for a specific job ID."""
    try:
        job = job_metadata[job_metadata['id'] == job_id]
        if job.empty:
            return jsonify({"detail": "Job not found"}), 404
        return jsonify(job.to_dict(orient="records")[0])
    except Exception as e:
        logger.error("Error getting job detail: %s", str(e))
        return jsonify({"detail": "Internal Server Error"}), 500

# =================================================================
# MAIN EXECUTION
# =================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)