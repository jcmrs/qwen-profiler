"""
ML-based predictor for role activation in the Qwen Profiler
Uses historical activation patterns and context to predict which roles should be activated
"""
import asyncio
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import statistics
from enum import Enum
import pickle
import os

from ..memory.manager import MemoryManager, MemoryEntry, MemoryType


class PredictionModelType(Enum):
    """Types of prediction models available"""
    LINEAR_REGRESSION = "linear_regression"
    DECISION_TREE = "decision_tree"
    RANDOM_FOREST = "random_forest"
    NEURAL_NETWORK = "neural_network"
    ENSEMBLE = "ensemble"


@dataclass
class ActivationPrediction:
    """Represents a prediction for profile activation"""
    profile_id: str
    probability: float  # 0.0 to 1.0
    confidence: float   # 0.0 to 1.0
    context: str  # Using string instead of ActivationContext to avoid circular import
    predicted_at: datetime
    model_used: PredictionModelType


class MLRolePredictor:
    """
    ML-based predictor for determining which roles should be activated based on context
    Uses historical activation patterns and current context to make predictions
    """
    
    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        self.memory_manager = memory_manager or MemoryManager()
        self.logger = logging.getLogger(__name__)

        # Historical activation patterns
        self.activation_history: List[Dict[str, Any]] = []

        # Context patterns that influence activation
        self.context_patterns: Dict[str, Dict[str, float]] = {}

        # Active prediction model
        self.prediction_model = None
        self.model_type = PredictionModelType.LINEAR_REGRESSION  # Default to simpler model
        self.model_trained = False

        # Lock for thread safety
        self._lock = threading.RLock()

        # Load any existing activation history from memory
        self._load_history_from_memory()

    def record_activation_event(self, profile_id: str, context: str,
                              conditions: Dict[str, Any] = None) -> bool:
        """Record an activation event for ML model training"""
        with self._lock:
            activation_record = {
                "profile_id": profile_id,
                "context": context,
                "conditions": conditions or {},
                "timestamp": datetime.now(),
                "was_activated": True  # This was an actual activation
            }

            self.activation_history.append(activation_record)

            # Store in memory for persistence
            memory_entry = MemoryEntry(
                id=f"activation_record_{profile_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                content=activation_record,
                creation_time=datetime.now(),
                memory_type=MemoryType.LONG_TERM,
                tags=["ml_prediction", "activation", "history"],
                ttl=timedelta(days=30)  # Keep activation records for 30 days
            )
            self.memory_manager.store(memory_entry)

            # Retrain model periodically as new data comes in
            if len(self.activation_history) % 10 == 0:  # Retrain every 10 new records
                self.train_model()

            return True
    
    def record_deactivation_event(self, profile_id: str, context: str,
                                 conditions: Dict[str, Any] = None) -> bool:
        """Record a deactivation event for ML model training"""
        with self._lock:
            deactivation_record = {
                "profile_id": profile_id,
                "context": context,
                "conditions": conditions or {},
                "timestamp": datetime.now(),
                "was_activated": False  # This was an actual non-activation
            }

            self.activation_history.append(deactivation_record)

            # Store in memory for persistence
            memory_entry = MemoryEntry(
                id=f"deactivation_record_{profile_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                content=deactivation_record,
                creation_time=datetime.now(),
                memory_type=MemoryType.LONG_TERM,
                tags=["ml_prediction", "deactivation", "history"],
                ttl=timedelta(days=30)  # Keep deactivation records for 30 days
            )
            self.memory_manager.store(memory_entry)

            # Retrain model periodically as new data comes in
            if len(self.activation_history) % 10 == 0:  # Retrain every 10 new records
                self.train_model()

            return True
    
    def train_model(self) -> bool:
        """Train the ML model on historical activation data"""
        with self._lock:
            if len(self.activation_history) < 5:
                # Need more data to train
                self.logger.info("Not enough data to train prediction model yet")
                return False
            
            try:
                # Process historical data to extract features and labels
                # Simple model: look for patterns in context, conditions, and profile combinations
                feature_data = []
                labels = []
                
                for record in self.activation_history:
                    # Convert context and conditions to numerical features
                    features = self._extract_features(record)
                    label = 1 if record["was_activated"] else 0
                    
                    feature_data.append(features)
                    labels.append(label)
                
                # For now, implement a simple frequency-based model
                # In a real implementation, we would use actual ML libraries like scikit-learn
                self._build_frequency_model(feature_data, labels)
                
                self.model_trained = True
                self.logger.info(f"Model trained on {len(self.activation_history)} historical records")
                
                # Store the model in memory
                model_entry = MemoryEntry(
                    id=f"prediction_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    content={
                        "model_type": self.model_type.value,
                        "training_records_count": len(self.activation_history),
                        "training_timestamp": datetime.now().isoformat(),
                        "context_patterns": self.context_patterns
                    },
                    creation_time=datetime.now(),
                    memory_type=MemoryType.LONG_TERM,
                    tags=["ml_prediction", "model", "trained"],
                    ttl=timedelta(days=30)
                )
                self.memory_manager.store(model_entry)
                
                return True
            except Exception as e:
                self.logger.error(f"Error training prediction model: {e}")
                return False
    
    def _extract_features(self, record: Dict[str, Any]) -> List[float]:
        """Extract numerical features from an activation record"""
        # Create a simple encoding of the context and conditions
        features = []

        # Encode context as a number
        context_encoding = {
            "technical": 0.0,
            "behavioral": 1.0,
            "semantic": 2.0,
            "integration": 3.0,
            "unknown": 4.0
        }
        features.append(context_encoding.get(record["context"], 4.0))

        # Process conditions - encode important condition keys
        conditions = record["conditions"]

        # Add some common condition indicators
        condition_features = [
            float(bool(conditions.get("user_intent"))),
            float(bool(conditions.get("target_framework"))),
            float(bool(conditions.get("required_validation"))),
            float(len(str(conditions))) / 100.0  # Normalize length of conditions
        ]
        features.extend(condition_features)

        return features
    
    def _build_frequency_model(self, feature_data: List[List[float]], labels: List[int]):
        """Build a simple frequency-based model for predictions"""
        # Reset context patterns
        self.context_patterns = {}
        
        # Count activations by profile and context
        activation_counts = {}
        total_counts = {}
        
        for i, record in enumerate(self.activation_history):
            profile_id = record["profile_id"]
            context = record["context"]
            was_activated = record["was_activated"]
            
            key = f"{profile_id}_{context}"
            
            if key not in activation_counts:
                activation_counts[key] = 0
            if key not in total_counts:
                total_counts[key] = 0
            
            total_counts[key] += 1
            if was_activated:
                activation_counts[key] += 1
        
        # Calculate probabilities based on historical activation rates
        for key, total in total_counts.items():
            if total > 0:
                prob = activation_counts.get(key, 0) / total
                profile_id, context = key.split("_", 1)
                
                if profile_id not in self.context_patterns:
                    self.context_patterns[profile_id] = {}
                
                self.context_patterns[profile_id][context] = {
                    "probability": prob,
                    "activation_count": activation_counts.get(key, 0),
                    "total_count": total
                }
    
    def predict_profile_activation(self, profile_id: str, context: str,
                                  conditions: Optional[Dict[str, Any]] = None) -> ActivationPrediction:
        """Predict whether a profile should be activated based on context"""
        with self._lock:
            if not self.model_trained:
                # If no model is trained, return a baseline prediction
                return ActivationPrediction(
                    profile_id=profile_id,
                    probability=0.5,  # 50% baseline
                    confidence=0.0,   # Low confidence without model
                    context=context,
                    predicted_at=datetime.now(),
                    model_used=self.model_type
                )

            # Look up historical pattern for this profile_id and context
            context_str = context
            probability = 0.5  # Default fallback
            confidence = 0.5   # Default confidence

            if profile_id in self.context_patterns:
                if context_str in self.context_patterns[profile_id]:
                    pattern = self.context_patterns[profile_id][context_str]
                    probability = pattern["probability"]
                    # Confidence increases with more historical data
                    confidence = min(0.95, pattern["total_count"] / 20.0)  # Up to 95% confidence with 20+ samples

            # Calculate additional factors based on conditions
            if conditions:
                # Adjust probability based on specific conditions
                if "urgent" in str(conditions.get("priority", "")).lower():
                    probability = min(1.0, probability * 1.5)  # Increase probability for urgent
                elif "low_priority" in str(conditions.get("priority", "")).lower():
                    probability = max(0.0, probability * 0.7)  # Decrease probability for low priority

            return ActivationPrediction(
                profile_id=profile_id,
                probability=probability,
                confidence=confidence,
                context=context,
                predicted_at=datetime.now(),
                model_used=self.model_type
            )
    
    def predict_activations_for_context(self, context: str,
                                       all_profiles: List[Dict[str, Any]],  # Using dict instead of ActivationProfile to avoid circular import
                                       conditions: Optional[Dict[str, Any]] = None) -> List[ActivationPrediction]:
        """Predict which profiles should be activated for a given context"""
        predictions = []

        for profile in all_profiles:
            # Handle both dict and ActivationProfile objects for compatibility
            profile_id = profile.get("id") if isinstance(profile, dict) else getattr(profile, "id", str(profile))
            prediction = self.predict_profile_activation(
                profile_id, context, conditions
            )
            predictions.append(prediction)

        # Sort predictions by probability (highest first)
        predictions.sort(key=lambda x: x.probability, reverse=True)

        return predictions
    
    def _load_history_from_memory(self):
        """Load historical activation records from memory"""
        with self._lock:
            # Search for activation history entries in memory
            history_entries = self.memory_manager.search(
                tags=["ml_prediction", "activation", "history"],
                memory_type=MemoryType.LONG_TERM
            )
            
            for entry in history_entries:
                if "profile_id" in entry.content:  # Verify it's a valid record
                    # Convert string timestamp back to datetime
                    record = entry.content.copy()
                    record["timestamp"] = datetime.fromisoformat(record["timestamp"])
                    self.activation_history.append(record)
            
            # Also load deactivation records
            deactivation_entries = self.memory_manager.search(
                tags=["ml_prediction", "deactivation", "history"],
                memory_type=MemoryType.LONG_TERM
            )
            
            for entry in deactivation_entries:
                if "profile_id" in entry.content:  # Verify it's a valid record
                    # Convert string timestamp back to datetime
                    record = entry.content.copy()
                    record["timestamp"] = datetime.fromisoformat(record["timestamp"])
                    self.activation_history.append(record)
            
            self.logger.info(f"Loaded {len(self.activation_history)} historical records for ML prediction")