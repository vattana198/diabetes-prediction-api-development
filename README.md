# Diabetes Prediction Project

A machine learning project for predicting diabetes risk based on patient features, with a FastAPI backend for model inference.

## Project Structure

```
diabetes-prediction/
├── data/
│   └── diabetes_data.csv          # Dataset
├── models/                         # Saved models and preprocessing components
│   ├── best_diabetes_model.pkl
│   ├── scaler.pkl
│   ├── label_encoders.pkl
│   ├── selected_features.pkl
│   ├── feature_indices.pkl
│   └── model_summary.json
├── notebooks/
│   └── diabetes_prediction.ipynb   # Jupyter notebook with EDA and model training
├── src/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application
│   ├── model_service.py           # Model loading and prediction service
│   ├── config.py                   # Configuration settings
│   └── test_api.py                # API testing script
├── run_api.py                      # Script to run the API server
├── .env.example                    # Environment variables template
├── pyproject.toml                  # Project dependencies
└── README.md
```

## Features

- **Data Analysis**: Comprehensive exploratory data analysis
- **Model Training**: Multiple classification algorithms (Logistic Regression, Decision Tree, Random Forest)
- **Model Evaluation**: Detailed performance metrics and visualizations
- **REST API**: FastAPI backend for model inference
- **Batch Predictions**: Support for single and batch predictions

## Installation

### Local Development

1. Install dependencies:
```bash
pip install -e .
```

Or using uv (faster):
```bash
# Install uv first (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv pip install -e .
```

### EC2 Deployment

For detailed EC2 deployment instructions with uv, see [EC2_DEPLOYMENT.md](EC2_DEPLOYMENT.md)

Quick start on EC2:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# Install Python (if needed)
uv python install 3.13

# Install project
uv pip install -e .

# Set environment variables
export PUBLIC_IP=your-ec2-public-ip
export PORT=8000
export ENVIRONMENT=production

# Run API
python3 run_api.py
```

## Model Training

1. Open the Jupyter notebook:
```bash
jupyter notebook notebooks/diabetes_prediction.ipynb
```

2. Run all cells to:
   - Load and explore the data
   - Clean and preprocess the data
   - Train multiple models
   - Evaluate and compare models
   - Save the best model

The trained model and preprocessing components will be saved in the `models/` directory.

## API Usage

### Starting the API Server

Run the FastAPI server:

```bash
python run_api.py
```

Or using uvicorn directly:

```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### API Endpoints

#### 1. Health Check
```bash
GET /health
```

Returns the health status of the API and model.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_type": "RandomForestClassifier"
}
```

#### 2. Single Prediction
```bash
POST /predict
```

Predicts diabetes risk for a single patient.

**Request Body:**
```json
{
  "gender": "Female",
  "age": 45.0,
  "hypertension": 0,
  "heart_disease": 0,
  "smoking_history": "never",
  "bmi": 25.5,
  "HbA1c_level": 5.7,
  "blood_glucose_level": 140
}
```

**Response:**
```json
{
  "prediction": 0,
  "probability": 0.1523,
  "risk_level": "Low"
}
```

**Field Descriptions:**
- `gender`: "Female", "Male", or "Other"
- `age`: Age in years (0-120)
- `hypertension`: 0 (No) or 1 (Yes)
- `heart_disease`: 0 (No) or 1 (Yes)
- `smoking_history`: "No Info", "current", "ever", "former", "never", or "not current"
- `bmi`: Body Mass Index (10-100)
- `HbA1c_level`: Glycated hemoglobin level (3.5-10)
- `blood_glucose_level`: Blood glucose level (80-300)

**Risk Levels:**
- `Low`: Probability < 0.3
- `Medium`: 0.3 ≤ Probability < 0.7
- `High`: Probability ≥ 0.7

#### 3. Batch Prediction
```bash
POST /predict/batch
```

Predicts diabetes risk for multiple patients.

**Request Body:**
```json
{
  "patients": [
    {
      "gender": "Male",
      "age": 55.0,
      "hypertension": 1,
      "heart_disease": 0,
      "smoking_history": "former",
      "bmi": 28.0,
      "HbA1c_level": 6.5,
      "blood_glucose_level": 160
    },
    {
      "gender": "Female",
      "age": 35.0,
      "hypertension": 0,
      "heart_disease": 0,
      "smoking_history": "never",
      "bmi": 22.0,
      "HbA1c_level": 5.0,
      "blood_glucose_level": 100
    }
  ]
}
```

**Response:**
```json
{
  "predictions": [
    {
      "prediction": 1,
      "probability": 0.7234,
      "risk_level": "High"
    },
    {
      "prediction": 0,
      "probability": 0.0891,
      "risk_level": "Low"
    }
  ]
}
```

### Testing the API

Use the provided test script:

```bash
python src/test_api.py
```

Or test manually with curl:

```bash
# Health check
curl http://localhost:8000/health

# Single prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Female",
    "age": 45.0,
    "hypertension": 0,
    "heart_disease": 0,
    "smoking_history": "never",
    "bmi": 25.5,
    "HbA1c_level": 5.7,
    "blood_glucose_level": 140
  }'
```

## Model Information

The model uses the following features (selected based on correlation analysis):
- HbA1c_level
- blood_glucose_level
- age
- bmi
- smoking_history
- gender
- hypertension

## Environment Variables

The API can be configured using environment variables:

- `HOST`: Server host (default: `0.0.0.0` - binds to all interfaces)
- `PORT`: Server port (default: `8000`)
- `ENVIRONMENT`: Environment mode - `development` or `production` (default: `development`)
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins, or `*` for all (default: `*`)
- `LOG_LEVEL`: Logging level - `debug`, `info`, `warning`, `error` (default: `info`)
- `BASE_DIR`: Base directory path (auto-detected if not set)
- `PUBLIC_IP`: Your EC2 public IP address (used for displaying access URLs)

### Example Configuration

**For EC2 Deployment:**
```bash
export HOST=0.0.0.0
export PORT=8000
export ENVIRONMENT=production
export PUBLIC_IP=54.123.45.67  # Your EC2 public IP
export LOG_LEVEL=info
```

**For Production with Custom Domain:**
```bash
export HOST=0.0.0.0
export PORT=8000
export ENVIRONMENT=production
export CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
export LOG_LEVEL=info
```

Or create a `.env` file (see `.env.example` for template):
```bash
cp .env.example .env
# Edit .env with your settings
```

## EC2 Deployment

### Prerequisites

1. EC2 instance with Python 3.13+ installed
2. Security group configured to allow inbound traffic on your chosen port
3. Model files in the `models/` directory

### Deployment Steps

1. **Connect to your EC2 instance:**
   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-public-ip
   ```

2. **Clone or upload your project:**
   ```bash
   git clone <your-repo-url>
   # or upload files via SCP
   ```

3. **Install dependencies:**
   ```bash
   cd diabetes-prediction
   pip install -e .
   # or
   python -m pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   export HOST=0.0.0.0
   export PORT=8000
   export ENVIRONMENT=production
   export PUBLIC_IP=your-ec2-public-ip-here
   ```
   
   Replace `your-ec2-public-ip-here` with your actual EC2 public IP address.

5. **Configure EC2 Security Group:**
   - Open your EC2 Security Group
   - Add inbound rule: Custom TCP, Port 8000 (or your chosen port), Source: 0.0.0.0/0 (or specific IPs)

6. **Run the API:**
   ```bash
   python run_api.py
   ```
   
   Or run in background with nohup:
   ```bash
   nohup python run_api.py > api.log 2>&1 &
   ```

7. **Access the API:**
   - API: `http://your-ec2-public-ip:8000`
   - Docs: `http://your-ec2-public-ip:8000/docs`
   - Health: `http://your-ec2-public-ip:8000/health`

### Running as a Service (Systemd)

Create a systemd service file for automatic startup:

```bash
sudo nano /etc/systemd/system/diabetes-api.service
```

Add the following content:
```ini
[Unit]
Description=Diabetes Prediction API
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/diabetes-prediction
Environment="HOST=0.0.0.0"
Environment="PORT=8000"
Environment="ENVIRONMENT=production"
ExecStart=/usr/bin/python3 /home/ec2-user/diabetes-prediction/run_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable diabetes-api
sudo systemctl start diabetes-api
sudo systemctl status diabetes-api
```

### Using a Reverse Proxy (Nginx)

For production, it's recommended to use Nginx as a reverse proxy:

1. **Install Nginx:**
   ```bash
   sudo yum install nginx -y  # Amazon Linux
   # or
   sudo apt-get install nginx -y  # Ubuntu
   ```

2. **Configure Nginx:**
   ```bash
   sudo nano /etc/nginx/conf.d/diabetes-api.conf
   ```

   Add configuration:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;  # or your EC2 public IP

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Start Nginx:**
   ```bash
   sudo systemctl start nginx
   sudo systemctl enable nginx
   ```

### Security Considerations

1. **Firewall Configuration:**
   - Only open necessary ports
   - Consider restricting access to specific IP ranges

2. **CORS Configuration:**
   - In production, set `CORS_ORIGINS` to your frontend domain(s)
   - Avoid using `*` in production

3. **HTTPS/SSL:**
   - Use a reverse proxy (Nginx) with SSL certificate (Let's Encrypt)
   - Or use AWS Application Load Balancer with SSL certificate

4. **Environment Variables:**
   - Use secure methods to store sensitive configuration
   - Consider using AWS Systems Manager Parameter Store or Secrets Manager

## Development

### Running Tests

```bash
python src/test_api.py
```

### Code Structure

- `src/main.py`: FastAPI application with endpoints
- `src/model_service.py`: Model loading and prediction logic
- `src/test_api.py`: API testing utilities

## License

[Add your license here]

## Author

[Add your name here]

