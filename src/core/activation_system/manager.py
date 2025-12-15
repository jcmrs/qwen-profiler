"""
Activation system for the Qwen Profiler
Manages dynamic activation of roles and components based on context
"""
import asyncio
import threading
from typing import Dict, List, Optional, Callable, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
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
    
    def activate_by_context(self, context: ActivationContext, duration: Optional[timedelta] = None) -> List[str]:
        """Activate all profiles matching the specified context"""
        with self._lock:
            activated = []
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