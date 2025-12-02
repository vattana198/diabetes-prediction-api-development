"""
FastAPI application for Diabetes Prediction Model
"""
import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import numpy as np
import pandas as pd

# Import model service and config
from model_service import ModelService
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model service with base directory from settings
model_service = ModelService(base_dir=settings.BASE_DIR)


# Request/Response Schemas
class DiabetesPredictionRequest(BaseModel):
    """Request schema for diabetes prediction"""
    gender: str = Field(..., description="Gender: 'Female', 'Male', or 'Other'")
    age: float = Field(..., ge=0, le=120, description="Age in years")
    hypertension: int = Field(..., ge=0, le=1, description="Hypertension: 0 (No) or 1 (Yes)")
    heart_disease: int = Field(..., ge=0, le=1, description="Heart disease: 0 (No) or 1 (Yes)")
    smoking_history: str = Field(
        ..., 
        description="Smoking history: 'No Info', 'current', 'ever', 'former', 'never', or 'not current'"
    )
    bmi: float = Field(..., ge=10, le=100, description="Body Mass Index")
    HbA1c_level: float = Field(..., ge=3.5, le=10, description="HbA1c level (glycated hemoglobin)")
    blood_glucose_level: float = Field(..., ge=80, le=300, description="Blood glucose level")

    class Config:
        json_schema_extra = {
            "example": {
                "gender": "Female",
                "age": 45.0,
                "hypertension": 0,
                "heart_disease": 0,
                "smoking_history": "never",
                "bmi": 25.5,
                "HbA1c_level": 5.7,
                "blood_glucose_level": 140
            }
        }


class DiabetesPredictionResponse(BaseModel):
    """Response schema for diabetes prediction"""
    prediction: int = Field(..., description="Predicted class: 0 (No Diabetes) or 1 (Diabetes)")
    probability: float = Field(..., ge=0, le=1, description="Probability of diabetes")
    risk_level: str = Field(..., description="Risk level: 'Low', 'Medium', or 'High'")

    class Config:
        json_schema_extra = {
            "example": {
                "prediction": 0,
                "probability": 0.15,
                "risk_level": "Low"
            }
        }


class BatchPredictionRequest(BaseModel):
    """Request schema for batch predictions"""
    patients: List[DiabetesPredictionRequest] = Field(..., description="List of patient data")


class BatchPredictionResponse(BaseModel):
    """Response schema for batch predictions"""
    predictions: List[DiabetesPredictionResponse] = Field(..., description="List of predictions")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    model_type: Optional[str] = None


# API Endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "message": "Diabetes Prediction API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model_service.is_model_loaded(),
        "model_type": model_service.get_model_type() if model_service.is_model_loaded() else None
    }


@app.post("/predict", response_model=DiabetesPredictionResponse, tags=["Prediction"])
async def predict_diabetes(request: DiabetesPredictionRequest):
    """
    Predict diabetes risk for a single patient
    
    - **gender**: Patient's gender
    - **age**: Patient's age in years
    - **hypertension**: Whether patient has hypertension (0 or 1)
    - **heart_disease**: Whether patient has heart disease (0 or 1)
    - **smoking_history**: Patient's smoking history
    - **bmi**: Body Mass Index
    - **HbA1c_level**: Glycated hemoglobin level
    - **blood_glucose_level**: Blood glucose level
    """
    try:
        # Convert request to dictionary
        patient_data = request.model_dump()
        
        # Make prediction
        prediction, probability = model_service.predict(patient_data)
        
        # Determine risk level
        if probability < 0.3:
            risk_level = "Low"
        elif probability < 0.7:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        return DiabetesPredictionResponse(
            prediction=prediction,
            probability=round(probability, 4),
            risk_level=risk_level
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_diabetes_batch(request: BatchPredictionRequest):
    """
    Predict diabetes risk for multiple patients in batch
    
    - **patients**: List of patient data dictionaries
    """
    try:
        predictions = []
        
        for patient_data in request.patients:
            # Convert to dictionary
            data = patient_data.model_dump()
            
            # Make prediction
            prediction, probability = model_service.predict(data)
            
            # Determine risk level
            if probability < 0.3:
                risk_level = "Low"
            elif probability < 0.7:
                risk_level = "Medium"
            else:
                risk_level = "High"
            
            predictions.append(
                DiabetesPredictionResponse(
                    prediction=prediction,
                    probability=round(probability, 4),
                    risk_level=risk_level
                )
            )
        
        return BatchPredictionResponse(predictions=predictions)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.reload_enabled,
        log_level=settings.LOG_LEVEL
    )

