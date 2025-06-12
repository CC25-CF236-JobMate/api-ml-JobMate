# JobMate ML API

This repository contains the backend machine learning service for the JobMate platform. The API provides intelligent job recommendation and classification functionalities, designed to be a scalable and secure microservice running on Google Cloud.

**Live API Endpoint:** https://jobmate-api-705829099986.asia-southeast2.run.app

## 🚀 Features

- **Resume-Based Job Recommendation**: Recommends the top 5 most relevant jobs by analyzing the text of a user's resume and calculating cosine similarity against a database of job vectors
- **Job Category Prediction**: Predicts the category of a job (e.g., "Software Development," "Healthcare") based on its description using a trained supervised learning model
- **Centralized Model Management**: All ML models and data are loaded dynamically from a Google Cloud Storage bucket, allowing for updates without redeploying the application code
- **Secure API**: Endpoints are protected via Bearer Token authentication
- **Containerized & Cloud-Native**: Packaged with Docker and deployed on Google Cloud Run for scalability and reliability

## 🛠️ Tech Stack

- **Backend**: Flask, Gunicorn
- **Machine Learning**: Scikit-learn
- **Data Handling**: Pandas, NumPy, SciPy
- **Cloud Services**: Google Cloud Run, Google Cloud Storage, Google Cloud Build
- **Environment Management**: python-dotenv
- **Containerization**: Docker

## 🔐 Authentication

All endpoints (except `/` and `/healthcheck`) require an Authorization header:

```
Authorization: Bearer <your_api_token>
```

---

## 📋 API Endpoints

### 1. Get Root Message

**Endpoint:** `/`  
**Method:** `GET`  
**Description:** Shows a welcome message and lists all available endpoints

**Success Response (200 OK):**
```json
{
  "message": "✅ JobMate ML API is running 🚀",
  "docs": "Not available.",
  "health": "/healthcheck",
  "endpoints": [
    "POST /recommend",
    "POST /predict-category",
    "GET /categories",
    "GET /jobs/{job_id}"
  ]
}
```

---

### 2. Health Check

**Endpoint:** `/healthcheck`  
**Method:** `GET`  
**Description:** A simple health check to verify if the service is running

**Success Response (200 OK):**
```json
{
  "status": "ok"
}
```

---

### 3. Recommend Jobs

**Endpoint:** `/recommend`  
**Method:** `POST`  
**Description:** Recommends jobs based on the provided resume text

**Request Body:**
```json
{
  "text": "Experienced in Python, data analysis, and machine learning using Scikit-learn and Pandas. Seeking a data scientist role."
}
```

**Success Response (200 OK):**
```json
{
  "recommendations": [
    {
      "job_id": 123,
      "job_title": "Data Scientist",
      "description": "We are looking for a data scientist proficient in Python...",
      "similarity_score": 0.8971
    }
  ]
}
```

---

### 4. Predict Job Category

**Endpoint:** `/predict-category`  
**Method:** `POST`  
**Description:** Predicts the job category from a job description

**Request Body:**
```json
{
  "description": "Job responsibilities include developing web applications with React and Node.js."
}
```

**Success Response (200 OK):**
```json
{
  "predicted_category": "Information Technology"
}
```

---

### 5. Get All Categories

**Endpoint:** `/categories`  
**Method:** `GET`  
**Description:** Returns a list of all unique job categories the model was trained on

**Success Response (200 OK):**
```json
{
  "categories": [
    "Accounting",
    "Engineering",
    "Healthcare",
    "Information Technology"
  ]
}
```

---

### 6. Get Job Details

**Endpoint:** `/jobs/<int:job_id>`  
**Method:** `GET`  
**Description:** Returns all metadata for a specific job ID

**Success Response (200 OK):**
```json
{
  "id": 123,
  "Job Title": "Data Scientist",
  "Job Description": "Full job description text...",
  "Company": "Tech Corp"
}
```

## ⚙️ Setup and Development

### 🔧 Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# The name of the GCS bucket where models are stored
BUCKET_NAME="model-ml-jobmate"

# The secret token required to authenticate with the API
API_TOKEN="mysecretbearer123"
```

---

### 💻 Local Setup

**1. Clone the repository:**
```bash
git clone <your-repository-url>
cd <repository-directory>
```

**2. Create a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Set up Application Credentials:**
To access the GCS bucket locally, authenticate by running:
```bash
gcloud auth application-default login
```

**5. Run the application:**
```bash
flask --app main run --debug
```

The application will be available at `http://127.0.0.1:5000`.

---

### ☁️ Deployment to Google Cloud Run

The application is designed to be deployed as a container on Google Cloud Run.

**Step 1: Build and Push the Docker Image**

```bash
gcloud builds submit --tag gcr.io/capstone-jobseeker-dd654/jobmate-api .
```

**Step 2: Deploy to Cloud Run**

```bash
gcloud run deploy jobmate-api \
  --image gcr.io/capstone-jobseeker-dd654/jobmate-api:latest \
  --region asia-southeast2 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars BUCKET_NAME=model-ml-jobmate,API_TOKEN=mysecretbearer123 \
  --min-instances 0 \
  --max-instances 1 \
  --timeout 300 \
  --cpu 2 \
  --memory 8Gi
```

**Key Deployment Flags:**

- `--image`: Specifies the container image to deploy
- `--region`: Sets the deployment region
- `--allow-unauthenticated`: Makes the service publicly accessible (the application's own token auth provides security)
- `--set-env-vars`: Injects the required environment variables into the running container
- `--min-instances/--max-instances`: Configures autoscaling behavior
- `--cpu/--memory`: Allocates resources for the service instance

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

If you have any questions or need support, please open an issue in this repository.

---

**Made with ❤️ by JobMate Team**
