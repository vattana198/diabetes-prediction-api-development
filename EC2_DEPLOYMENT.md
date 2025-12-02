# EC2 Deployment Guide with UV

This guide will help you deploy the Diabetes Prediction API on an EC2 instance using `uv` for package management.

## Prerequisites

- EC2 instance running (Amazon Linux 2, Ubuntu, or similar)
- SSH access to your EC2 instance
- Python 3.13+ installed (or we'll install it with uv)

## Step 1: Connect to Your EC2 Instance

```bash
ssh -i your-key.pem ec2-user@your-ec2-public-ip
# or for Ubuntu:
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

## Step 2: Install UV

UV is a fast Python package installer and resolver. Install it with:

```bash
# Install uv using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH (for current session)
export PATH="$HOME/.cargo/bin:$PATH"

# Or add to your shell profile for permanent access
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Verify installation:
```bash
uv --version
```

## Step 3: Install Python (if needed)

UV can install Python for you:

```bash
# Install Python 3.13 (or your preferred version)
uv python install 3.13

# Or use system Python if already installed
python3 --version
```

## Step 4: Upload Your Project

### Option A: Using Git (Recommended)

```bash
# Clone your repository
git clone <your-repo-url>
cd diabetes-prediction
```

### Option B: Using SCP (from your local machine)

```bash
# From your local machine
scp -i your-key.pem -r /path/to/diabetes-prediction ec2-user@your-ec2-public-ip:~/
```

Then on EC2:
```bash
cd ~/diabetes-prediction
```

## Step 5: Install Project Dependencies with UV

### Method 1: Install in editable mode (Recommended)

```bash
# Install the project and all dependencies
uv pip install -e .

# This will:
# - Create a virtual environment automatically
# - Install all dependencies from pyproject.toml
# - Install the project in editable mode
```

### Method 2: Install dependencies only

```bash
# Install dependencies without the project itself
uv pip install -r <(uv pip compile pyproject.toml)
```

### Method 3: Using uv's project management

```bash
# Initialize uv project (if not already done)
uv init --no-readme

# Sync dependencies (installs everything from pyproject.toml)
uv sync
```

## Step 6: Verify Installation

```bash
# Check if packages are installed
uv pip list

# Test Python imports
python3 -c "import fastapi; import sklearn; print('Dependencies installed successfully!')"
```

## Step 7: Configure Environment Variables

```bash
# Set your EC2 public IP
export PUBLIC_IP=your-ec2-public-ip-here

# Set other environment variables
export HOST=0.0.0.0
export PORT=8000
export ENVIRONMENT=production
export LOG_LEVEL=info
```

## Step 8: Configure EC2 Security Group

1. Go to AWS Console → EC2 → Security Groups
2. Select your instance's security group
3. Add inbound rule:
   - Type: Custom TCP
   - Port: 8000 (or your chosen port)
   - Source: 0.0.0.0/0 (or specific IPs for security)

## Step 9: Run the API

### Option 1: Run directly

```bash
# Make sure you're in the project directory
cd ~/diabetes-prediction

# Run the API
python3 run_api.py
```

### Option 2: Run in background with nohup

```bash
nohup python3 run_api.py > api.log 2>&1 &
```

### Option 3: Run as a systemd service (Production)

Create a service file:

```bash
sudo nano /etc/systemd/system/diabetes-api.service
```

Add the following (adjust paths as needed):

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
Environment="PUBLIC_IP=your-ec2-public-ip-here"
Environment="PATH=/home/ec2-user/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 /home/ec2-user/diabetes-prediction/run_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable diabetes-api
sudo systemctl start diabetes-api
sudo systemctl status diabetes-api
```

## Step 10: Access Your API

Once running, access your API at:

- **API**: `http://your-ec2-public-ip:8000`
- **Documentation**: `http://your-ec2-public-ip:8000/docs`
- **Health Check**: `http://your-ec2-public-ip:8000/health`

## Troubleshooting

### UV not found after installation

```bash
# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Or install to a different location
curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --no-modify-path
# Then manually add to PATH
```

### Python version issues

```bash
# Check available Python versions
uv python list

# Install specific version
uv python install 3.13

# Use specific Python version
uv pip install --python 3.13 -e .
```

### Permission errors

```bash
# If you get permission errors, use --user flag
uv pip install --user -e .

# Or install to a virtual environment
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Port already in use

```bash
# Check what's using the port
sudo lsof -i :8000

# Kill the process or use a different port
export PORT=8080
```

### Model files not found

```bash
# Ensure models directory exists with all required files:
# - best_diabetes_model.pkl
# - scaler.pkl
# - label_encoders.pkl
# - selected_features.pkl
# - feature_indices.pkl

ls -la models/
```

## Quick Reference Commands

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# Install Python
uv python install 3.13

# Install project
cd diabetes-prediction
uv pip install -e .

# Set environment variables
export PUBLIC_IP=your-ec2-public-ip
export PORT=8000
export ENVIRONMENT=production

# Run API
python3 run_api.py
```

## Additional Resources

- UV Documentation: https://github.com/astral-sh/uv
- FastAPI Documentation: https://fastapi.tiangolo.com/
- AWS EC2 Documentation: https://docs.aws.amazon.com/ec2/

