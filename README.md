# 🧠 JobMate ML API

Machine Learning inference API for **JobMate** — A robust microservice developed with FastAPI and powered by Scikit-learn recommendation models.

This service provides **Job Recommendation** and **Resume Classification** capabilities, designed to be deployed independently (e.g., via Google Cloud Run) for seamless integration with the main REST API backend.

## ⚙️ Tech Stack

- **Python 3.10**
- **FastAPI** - Modern web framework for building APIs
- **Scikit-learn** - Machine learning library
- **Pandas, NumPy, SciPy** - Data processing and scientific computing
- **Uvicorn + Gunicorn** - ASGI server for production
- **Docker** - Containerization (optional)

## 🚀 API Endpoints

### Health Check
**GET** `/healthcheck`

Check if the server is running properly.

**Response:**
```json
{
  "status": "ok"
}
```

### 🔒 Authentication

All endpoints except `/healthcheck` require the following header:
```
Authorization: Bearer mysecrettoken123
```

### Job Recommendations
**POST** `/recommend`

Get job recommendations based on resume content.

**Request Body:**
```json
{
  "text": "Experienced Python developer with background in data science and machine learning..."
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "job_id": 12,
      "job_title": "Data Scientist",
      "description": "We are looking for a data scientist who can...",
      "similarity_score": 0.8235
    }
  ]
}
```

### Job Category Prediction
**POST** `/predict-category`

Predict job category from resume content.

**Request Body:**
```json
{
  "text": "Frontend engineer with experience in React and Vue..."
}
```

**Response:**
```json
{
  "predicted_category": "Software Engineer"
}
```

### Available Categories
**GET** `/categories`

Get all available job categories in the classification model.

**Response:**
```json
{
  "categories": [
    "Data Analyst",
    "Software Engineer",
    "Project Manager"
  ]
}
```

### Job Details
**GET** `/jobs/{job_id}`

Get complete job details by job ID.

**Example:** `GET /jobs/5`

**Response:**
```json
{
  "id": 5,
  "Job Title": "ML Engineer",
  "Job Description": "We need an ML engineer with experience in NLP..."
}
```

## 📁 Project Structure

```
jobmate-ml-api/
├── main.py                      # FastAPI application entry point
├── models/                      # Pre-trained ML models and data
│   ├── tfidf_vectorizer.pkl     # TF-IDF vectorizer for text processing
│   ├── supervised_vectorizer.pkl # Supervised learning vectorizer
│   ├── job_classifier.pkl       # Job classification model
│   ├── job_vectors.npz          # Pre-computed job vectors
│   └── job_metadata.csv         # Job metadata database
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── .dockerignore               # Docker ignore patterns
├── .gitignore                  # Git ignore patterns
└── README.md                   # Project documentation
```

## 🛠️ Local Development

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Setup Instructions

1. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   
   # On Linux/macOS
   source .venv/bin/activate
   
   # On Windows
   .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the development server**
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the API**
   - API Base URL: http://localhost:8000
   - Interactive API Docs (Swagger): http://localhost:8000/docs
   - Alternative API Docs (ReDoc): http://localhost:8000/redoc

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -t jobmate-ml-api .
```

### Run Docker Container
```bash
docker run -p 8000:8000 jobmate-ml-api
```

## ☁️ Google Cloud Run Deployment

### Prerequisites
- Google Cloud SDK installed and configured
- Docker installed
- Google Cloud project with billing enabled

### Deployment Steps

1. **Build and tag Docker image**
   ```bash
   docker build -t gcr.io/[PROJECT_ID]/jobmate-ml-api .
   ```

2. **Push to Google Container Registry**
   ```bash
   docker push gcr.io/[PROJECT_ID]/jobmate-ml-api
   ```

3. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy jobmate-ml-api \
     --image gcr.io/[PROJECT_ID]/jobmate-ml-api \
     --platform managed \
     --region asia-southeast2 \
     --allow-unauthenticated \
     --port 8000 \
     --memory 2Gi \
     --cpu 1
   ```

### Environment Variables (Optional)
You can set environment variables during deployment:
```bash
gcloud run deploy jobmate-ml-api \
  --image gcr.io/[PROJECT_ID]/jobmate-ml-api \
  --set-env-vars="API_TOKEN=your-secret-token"
```

## 🧪 Testing

### Manual Testing
Use the interactive Swagger documentation at `/docs` endpoint to test all API endpoints.

### cURL Examples

**Health Check:**
```bash
curl -X GET "http://localhost:8000/healthcheck"
```

**Job Recommendation:**
```bash
curl -X POST "http://localhost:8000/recommend" \
  -H "Authorization: Bearer mysecrettoken123" \
  -H "Content-Type: application/json" \
  -d '{"text": "Python developer with ML experience"}'
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is part of the JobMate application suite.

## 👨‍💻 Team

**JobMate Development Team**  
CC25-CF236 Cohort

---

### 🔗 Related Repositories
- [JobMate Main API](link-to-main-api)
- [JobMate Frontend](link-to-frontend)
- [JobMate Documentation](link-to-docs)

### 📞 Support
For questions or support, please contact the development team or create an issue in this repository.