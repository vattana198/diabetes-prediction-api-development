"""
Model Service for loading and using the diabetes prediction model
"""
import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelService:
    """Service class for loading and using the diabetes prediction model"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the model service
        
        Args:
            base_dir: Base directory of the project. If None, will try to detect automatically.
        """
        if base_dir is None:
            # Try to detect base directory
            current_file = Path(__file__).resolve()
            # Go up from src/model_service.py to project root
            if current_file.parent.name == "src":
                base_dir = str(current_file.parent.parent)
            else:
                # Fallback: assume we're in project root
                base_dir = str(current_file.parent)
        
        self.base_dir = Path(base_dir)
        self.models_dir = self.base_dir / "models"
        
        self.model = None
        self.scaler = None
        self.label_encoders = None
        self.selected_features = None
        self.feature_indices = None
        self.model_type = None
        
        # Load model and preprocessing components
        self._load_model()
    
    def _load_model(self):
        """Load the model and all preprocessing components"""
        try:
            # Load model
            model_path = self.models_dir / "best_diabetes_model.pkl"
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            self.model = joblib.load(model_path)
            logger.info(f"Model loaded from {model_path}")
            
            # Get model type
            self.model_type = type(self.model).__name__
            
            # Load scaler
            scaler_path = self.models_dir / "scaler.pkl"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                logger.info(f"Scaler loaded from {scaler_path}")
            else:
                logger.warning(f"Scaler file not found: {scaler_path}")
            
            # Load label encoders
            encoders_path = self.models_dir / "label_encoders.pkl"
            if encoders_path.exists():
                self.label_encoders = joblib.load(encoders_path)
                logger.info(f"Label encoders loaded from {encoders_path}")
            else:
                logger.warning(f"Label encoders file not found: {encoders_path}")
            
            # Load selected features
            features_path = self.models_dir / "selected_features.pkl"
            if features_path.exists():
                self.selected_features = joblib.load(features_path)
                logger.info(f"Selected features loaded: {self.selected_features}")
            else:
                logger.warning(f"Selected features file not found: {features_path}")
            
            # Load feature indices
            indices_path = self.models_dir / "feature_indices.pkl"
            if indices_path.exists():
                self.feature_indices = joblib.load(indices_path)
                logger.info(f"Feature indices loaded")
            else:
                logger.warning(f"Feature indices file not found: {indices_path}")
            
            logger.info("Model service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None
    
    def get_model_type(self) -> Optional[str]:
        """Get the type of the loaded model"""
        return self.model_type
    
    def _preprocess_input(self, patient_data: Dict) -> np.ndarray:
        """
        Preprocess input data for prediction
        
        Args:
            patient_data: Dictionary containing patient features
            
        Returns:
            Preprocessed feature array ready for model prediction
        """
        # Create DataFrame from input
        df = pd.DataFrame([patient_data])
        
        # Encode categorical variables
        if self.label_encoders:
            for col, encoder in self.label_encoders.items():
                if col in df.columns:
                    # Check if value is in encoder classes
                    if df[col].iloc[0] in encoder.classes_:
                        df[col] = encoder.transform([df[col].iloc[0]])
                    else:
                        # Handle unknown values - use most common class or raise error
                        raise ValueError(
                            f"Unknown value '{df[col].iloc[0]}' for feature '{col}'. "
                            f"Allowed values: {list(encoder.classes_)}"
                        )
        
        # Get all feature names in the order they were used during training
        # Based on the notebook, the features are: gender, age, hypertension, heart_disease, 
        # smoking_history, bmi, HbA1c_level, blood_glucose_level
        feature_order = [
            'gender', 'age', 'hypertension', 'heart_disease', 
            'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level'
        ]
        
        # Reorder columns to match training order
        df = df[feature_order]
        
        # Convert to numpy array
        features_array = df.values
        
        # Scale features
        if self.scaler:
            features_array = self.scaler.transform(features_array)
        
        # Select features based on correlation analysis
        if self.feature_indices is not None:
            features_array = features_array[:, self.feature_indices]
        elif self.selected_features is not None:
            # If feature_indices not available, select by feature names
            # This is a fallback - ideally feature_indices should be used
            selected_array = []
            for feature in self.selected_features:
                if feature in feature_order:
                    idx = feature_order.index(feature)
                    selected_array.append(features_array[:, idx])
            if selected_array:
                features_array = np.column_stack(selected_array)
        
        return features_array
    
    def predict(self, patient_data: Dict) -> Tuple[int, float]:
        """
        Make a prediction for a single patient
        
        Args:
            patient_data: Dictionary containing patient features:
                - gender: str ('Female', 'Male', 'Other')
                - age: float
                - hypertension: int (0 or 1)
                - heart_disease: int (0 or 1)
                - smoking_history: str ('No Info', 'current', 'ever', 'former', 'never', 'not current')
                - bmi: float
                - HbA1c_level: float
                - blood_glucose_level: float
        
        Returns:
            Tuple of (prediction, probability):
                - prediction: 0 (No Diabetes) or 1 (Diabetes)
                - probability: Probability of diabetes (0-1)
        """
        if not self.is_model_loaded():
            raise RuntimeError("Model is not loaded")
        
        # Preprocess input
        features = self._preprocess_input(patient_data)
        
        # Make prediction
        prediction = self.model.predict(features)[0]
        
        # Get prediction probability
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(features)[0]
            probability = probabilities[1]  # Probability of class 1 (diabetes)
        else:
            # If model doesn't have predict_proba, use prediction as probability estimate
            probability = float(prediction)
        
        return int(prediction), float(probability)

