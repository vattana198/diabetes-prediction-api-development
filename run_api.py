#!/usr/bin/env python3
"""
Script to run the FastAPI application
Supports deployment on EC2 with configurable host and port via environment variables
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import settings after adding to path
from config import settings

if __name__ == "__main__":
    # Get public IP from environment if provided
    public_ip = os.getenv("PUBLIC_IP", None)
    
    # Display configuration
    print("=" * 60)
    print("Diabetes Prediction API")
    print("=" * 60)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Host: {settings.HOST}")
    print(f"Port: {settings.PORT}")
    print(f"Auto-reload: {settings.reload_enabled}")
    print(f"Log level: {settings.LOG_LEVEL}")
    print("=" * 60)
    
    # Display access URLs
    if public_ip:
        print(f"API will be accessible at: http://{public_ip}:{settings.PORT}")
        print(f"API Documentation: http://{public_ip}:{settings.PORT}/docs")
        print(f"Health check: http://{public_ip}:{settings.PORT}/health")
    elif settings.HOST == "0.0.0.0":
        print(f"API will be accessible at: http://localhost:{settings.PORT} (or use your EC2 public IP)")
        print(f"API Documentation: http://localhost:{settings.PORT}/docs")
        print(f"Health check: http://localhost:{settings.PORT}/health")
        print(f"\nTo use with EC2 public IP, set PUBLIC_IP environment variable:")
        print(f"  export PUBLIC_IP=your-ec2-public-ip")
        print(f"  python run_api.py")
    else:
        print(f"API will be accessible at: http://{settings.HOST}:{settings.PORT}")
        print(f"API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
        print(f"Health check: http://{settings.HOST}:{settings.PORT}/health")
    print("=" * 60)
    print()
    
    # Change to src directory for uvicorn
    os.chdir(str(src_path))
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.reload_enabled,
        log_level=settings.LOG_LEVEL
    )

