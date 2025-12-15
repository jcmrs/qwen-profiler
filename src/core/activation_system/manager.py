"""
Activation system for the Qwen Profiler
Manages dynamic activation of roles and components based on context
"""
import asyncio
import threading
from typing import Dict, List, Optional, Callable, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import statistics
from collections import defaultdict, deque
from ..memory.manager import MemoryManager, MemoryEntry, MemoryType


class ActivationState(Enum):
    """States for role activation"""
    INACTIVE = "inactive"
    ACTIVATING = "activating"
    ACTIVE = "active"
    DEACTIVATING = "deactivating"


class ActivationContext(Enum):
    """Context types that trigger activation"""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SEMANTIC = "semantic"
    INTEGRATION = "integration"


@dataclass
class ActivationProfile:
    """Represents a profile that can be activated"""
    id: str
    name: str
    context: ActivationContext
    priority: int = 5  # 1-10 scale, 10 is highest priority
    active: bool = False
    activation_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    deactivation_callbacks: List[Callable] = field(default_factory=list)


class ActivationSystem:
    """Manages the activation of various roles and components in the system"""

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        self._profiles: Dict[str, ActivationProfile] = {}
        self._active_profiles: Set[str] = set()
        self._lock = threading.RLock()
        self._memory_manager = memory_manager or MemoryManager()
        self._init_default_profiles()
        self._cleanup_task = None
        self._setup_cleanup_task()

        # Initialize ML predictor for activation prediction (deferred instantiation to avoid circular import)
        self._ml_predictor_instance = None
        self._memory_manager = memory_manager or MemoryManager()
    
    @property
    def ml_predictor(self):
        """Lazily instantiate the ML predictor to avoid circular imports"""
        if self._ml_predictor_instance is None:
            # Import here to avoid circular import issues
            from ..ml_prediction.predictor import MLRolePredictor
            self._ml_predictor_instance = MLRolePredictor(memory_manager=self._memory_manager)
        return self._ml_predictor_instance

    def _init_default_profiles(self):
        """Initialize default activation profiles for the system"""
        default_profiles = [
            ActivationProfile(
                id="infrastructure-architect",
                name="Infrastructure Architect",
                context=ActivationContext.TECHNICAL,
                priority=8,
                dependencies=[]
            ),
            ActivationProfile(
                id="validation-engineer",
                name="Validation Engineer",
                context=ActivationContext.TECHNICAL,
                priority=7,
                dependencies=[]
            ),
            ActivationProfile(
                id="sre-specialist",
                name="SRE Specialist",
                context=ActivationContext.TECHNICAL,
                priority=9,
                dependencies=[]
            ),
            ActivationProfile(
                id="behavioral-architect",
                name="Behavioral Architect",
                context=ActivationContext.BEHAVIORAL,
                priority=8,
                dependencies=[]
            ),
            ActivationProfile(
                id="cognitive-validator",
                name="Cognitive Validator",
                context=ActivationContext.BEHAVIORAL,
                priority=7,
                dependencies=["behavioral-architect"]
            ),
            ActivationProfile(
                id="response-coordinator",
                name="Response Coordinator",
                context=ActivationContext.BEHAVIORAL,
                priority=8,
                dependencies=["behavioral-architect", "cognitive-validator"]
            ),
            ActivationProfile(
                id="domain-linguist",
                name="Domain Linguist",
                context=ActivationContext.SEMANTIC,
                priority=9,
                dependencies=[]
            )
        ]

        for profile in default_profiles:
            self._profiles[profile.id] = profile
    
    def _setup_cleanup_task(self):
        """Set up a periodic cleanup task for expired activations"""
        # For now, just log that we would set up the task
        # In a real implementation, we'd schedule this task
        pass
    
    def register_profile(self, profile: ActivationProfile) -> bool:
        """Register a new activation profile"""
        with self._lock:
            if profile.id in self._profiles:
                return False
            self._profiles[profile.id] = profile
            return True

    def deactivate_profile(self, profile_id: str) -> bool:
        """Deactivate a profile by ID"""
        with self._lock:
            if profile_id not in self._profiles:
                return False

            profile = self._profiles[profile_id]
            if not profile.active:
                return False

            # Check for dependents that would be affected
            dependents = [pid for pid, p in self._profiles.items() if profile_id in p.dependencies]
            if dependents:
                logging.warning(f"Deactivating {profile_id} may affect dependent profiles: {dependents}")

            # Deactivate the profile
            profile.active = False
            profile.activation_time = None
            self._active_profiles.discard(profile_id)

            # Remove from memory
            self._memory_manager.delete(f"activation_{profile_id}")

            # Record deactivation event for ML model training
            self.ml_predictor.record_deactivation_event(
                profile_id=profile_id,
                context=profile.context,
                conditions={"deactivation_source": "direct_call", "triggering_context": profile.context.value}
            )

            logging.info(f"Deactivated profile: {profile_id}")
            return True

    def _update_correlations(self, profile_id: str, context: str, condition: str = None):
        """Update correlation data for ML prediction"""
        # Update context-profile correlations
        if context and profile_id:
            # Simple frequency-based correlation
            current_corr = self._context_profile_correlations[context][profile_id]
            self._context_profile_correlations[context][profile_id] = current_corr + 0.1

        # Normalize correlations to sum to 1 for each context
        for ctx, profiles in self._context_profile_correlations.items():
            total = sum(profiles.values())
            if total > 0:
                for profile in profiles:
                    self._context_profile_correlations[ctx][profile] = profiles[profile] / total

    def predict_profile_activation_probability(self, profile_id: str, context: ActivationContext,
                                            conditions: Optional[Dict[str, Any]] = None) -> float:
        """Predict the probability that a profile should be activated in the given context"""
        prediction = self.ml_predictor.predict_profile_activation(profile_id, context, conditions)
        return prediction.probability

    def get_predicted_activations_for_context(self, context: ActivationContext,
                                            conditions: Optional[Dict[str, Any]] = None) -> List[Tuple[str, float]]:
        """Get profiles predicted to be activated for a given context with their probabilities"""
        predictions = self.ml_predictor.predict_activations_for_context(
            context, list(self._profiles.values()), conditions
        )
        # Return tuples of (profile_id, probability)
        return [(pred.profile_id, pred.probability) for pred in predictions]

    def activate_by_context_with_predictions(self, context: ActivationContext,
                                           threshold: float = 0.5,
                                           conditions: Optional[Dict[str, Any]] = None,
                                           duration: Optional[timedelta] = None) -> List[str]:
        """Activate profiles based on ML predictions with a probability threshold"""
        predicted_profiles = self.get_predicted_activations_for_context(context, conditions)

        activated_profiles = []
        for profile_id, probability in predicted_profiles:
            if probability >= threshold:
                success = self.activate_profile(profile_id, duration)
                if success:
                    activated_profiles.append(profile_id)

        return activated_profiles

    def predict_profiles_for_context(self, context: str, condition: str = None) -> List[Tuple[str, float]]:
        """Predict which profiles should be activated based on context using ML model - Legacy correlation method"""
        with self._lock:
            predictions = []

            # If we have correlation data for this context, use it
            if context in self._context_profile_correlations:
                for profile_id, correlation in self._context_profile_correlations[context].items():
                    # Only include profiles with significant correlation (> 0.1)
                    if correlation > 0.1:
                        predictions.append((profile_id, correlation))

            # Sort predictions by correlation strength
            predictions.sort(key=lambda x: x[1], reverse=True)
            return predictions

    def predict_and_activate_profiles(self, context: str, condition: str = None, threshold: float = 0.2) -> List[str]:
        """Use ML model to predict and activate appropriate profiles"""
        predictions = self.predict_profiles_for_context(context, condition)

        activated_profiles = []
        for profile_id, confidence in predictions:
            if confidence >= threshold and self.is_active(profile_id) == False:
                success = self.activate_profile(profile_id)
                if success:
                    activated_profiles.append(profile_id)

        return activated_profiles
    
    def activate_profile(self, profile_id: str, duration: Optional[timedelta] = None) -> bool:
        """Activate a profile by ID"""
        with self._lock:
            if profile_id not in self._profiles:
                return False

            profile = self._profiles[profile_id]

            # Check dependencies
            for dep_id in profile.dependencies:
                if dep_id not in self._active_profiles:
                    logging.warning(f"Cannot activate {profile_id}, dependency {dep_id} not active")
                    return False

            # Set expiry time if duration is specified
            if duration:
                profile.expiry_time = datetime.now() + duration
            else:
                profile.expiry_time = None  # No expiration

            # Activate the profile
            profile.active = True
            profile.activation_time = datetime.now()
            self._active_profiles.add(profile_id)

            # Store in memory for tracking
            memory_entry = MemoryEntry(
                id=f"activation_{profile_id}",
                content={
                    "profile_id": profile_id,
                    "activation_time": profile.activation_time.isoformat(),
                    "expiry_time": profile.expiry_time.isoformat() if profile.expiry_time else None,
                    "context": profile.context.value,
                    "priority": profile.priority
                },
                creation_time=profile.activation_time,
                memory_type=MemoryType.SHORT_TERM,
                tags=["activation", profile.context.value],
                ttl=timedelta(hours=1)  # Keep activation records for 1 hour
            )
            self._memory_manager.store(memory_entry)

            # Record activation event for ML model training
            self.ml_predictor.record_activation_event(
                profile_id=profile_id,
                context=profile.context,
                conditions={"activation_source": "direct_call", "triggering_context": profile.context.value}
            )

            logging.info(f"Activated profile: {profile_id} (context: {profile.context.value})")
            return True
    
    def deactivate_profile(self, profile_id: str) -> bool:
        """Deactivate a profile by ID"""
        with self._lock:
            if profile_id not in self._profiles:
                return False
            
            profile = self._profiles[profile_id]
            if not profile.active:
                return False
            
            # Execute deactivation callbacks
            for callback in profile.deactivation_callbacks:
                try:
                    callback()
                except Exception as e:
                    logging.error(f"Error in deactivation callback for {profile_id}: {e}")
            
            # Deactivate the profile
            profile.active = False
            profile.activation_time = None
            profile.expiry_time = None
            self._active_profiles.discard(profile_id)
            
            # Remove from memory
            self._memory_manager.delete(f"activation_{profile_id}")
            
            logging.info(f"Deactivated profile: {profile_id}")
            return True
    
    def is_active(self, profile_id: str) -> bool:
        """Check if a profile is currently active"""
        with self._lock:
            if profile_id not in self._profiles:
                return False
            return self._profiles[profile_id].active
    
    def get_active_profiles(self) -> List[ActivationProfile]:
        """Get all currently active profiles"""
        with self._lock:
            return [
                profile for profile in self._profiles.values()
                if profile.active and (
                    profile.expiry_time is None or 
                    datetime.now() < profile.expiry_time
                )
            ]
    
    def activate_by_context(self, context: ActivationContext, duration: Optional[timedelta] = None, use_ml_prediction: bool = False) -> List[str]:
        """Activate all profiles matching the specified context"""
        with self._lock:
            activated = []

            if use_ml_prediction:
                # Use ML model to predict which profiles should be activated
                predictions = self.predict_profiles_for_context(context.value)
                # Activate profiles based on ML predictions
                for profile_id, confidence in predictions:
                    profile = self._profiles.get(profile_id)
                    if profile and profile.context == context and not profile.active:
                        if self.activate_profile(profile_id, duration):
                            activated.append(profile_id)
            else:
                # Default behavior: activate all profiles matching the context
                # Sort profiles by priority (highest first)
                sorted_profiles = sorted(
                    self._profiles.values(),
                    key=lambda p: p.priority,
                    reverse=True
                )

                for profile in sorted_profiles:
                    if profile.context == context:
                        if self.activate_profile(profile.id, duration):
                            activated.append(profile.id)

            return activated
    
    def deactivate_by_context(self, context: ActivationContext) -> List[str]:
        """Deactivate all profiles matching the specified context"""
        with self._lock:
            deactivated = []
            for profile in self._profiles.values():
                if profile.context == context and profile.active:
                    if self.deactivate_profile(profile.id):
                        deactivated.append(profile.id)
            return deactivated
    
    def cleanup_expired(self):
        """Clean up expired activations"""
        with self._lock:
            now = datetime.now()
            expired_profiles = [
                profile_id for profile_id, profile in self._profiles.items()
                if profile.active and 
                profile.expiry_time and 
                now > profile.expiry_time
            ]
            
            for profile_id in expired_profiles:
                self.deactivate_profile(profile_id)
    
    def get_activation_stats(self) -> Dict[str, Any]:
        """Get activation system statistics"""
        with self._lock:
            self.cleanup_expired()  # Clean up before reporting stats
            
            stats = {
                "total_profiles": len(self._profiles),
                "active_profiles": len(self._active_profiles),
                "activation_counts_by_context": {
                    "technical": len([p for p in self.get_active_profiles() if p.context == ActivationContext.TECHNICAL]),
                    "behavioral": len([p for p in self.get_active_profiles() if p.context == ActivationContext.BEHAVIORAL]),
                    "semantic": len([p for p in self.get_active_profiles() if p.context == ActivationContext.SEMANTIC]),
                    "integration": len([p for p in self.get_active_profiles() if p.context == ActivationContext.INTEGRATION])
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return stats
    
    def trigger_contextual_activation(self, context: ActivationContext, condition: str) -> List[str]:
        """Trigger activation based on contextual conditions"""
        # This is a simplified version - in a full implementation,
        # this would have more sophisticated condition checking
        activation_rules = {
            ActivationContext.TECHNICAL: [
                "infrastructure", "validation", "sre", "deployment", "monitoring"
            ],
            ActivationContext.BEHAVIORAL: [
                "behavior", "response", "cognitive", "drift", "consistency"
            ],
            ActivationContext.SEMANTIC: [
                "semantic", "translation", "ontology", "domain", "intent"
            ],
            ActivationContext.INTEGRATION: [
                "integration", "cross-pillar", "coordinator", "synergy"
            ]
        }
        
        if condition.lower() in activation_rules[context]:
            return self.activate_by_context(context)
        return []