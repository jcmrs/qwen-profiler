"""
Memory manager for the Qwen Profiler
Handles both short-term and long-term memory operations
"""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import weakref
import threading
from dataclasses import dataclass, field
from enum import Enum


class MemoryType(Enum):
    """Types of memory in the system"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


@dataclass
class MemoryEntry:
    """Represents a single memory entry"""
    id: str
    content: Any
    creation_time: datetime
    memory_type: MemoryType
    tags: List[str] = field(default_factory=list)
    ttl: Optional[timedelta] = None  # Time-to-live for short-term memory
    priority: int = 1  # Priority level (1-10)


class MemoryManager:
    """Manages the memory systems for the Qwen Profiler"""
    
    def __init__(self):
        self._short_term_memory: Dict[str, MemoryEntry] = {}
        self._long_term_memory: Dict[str, MemoryEntry] = {}
        self._lock = threading.RLock()  # Thread-safe operations
        self._cleanup_task: Optional[asyncio.Task] = None
        self._init_memory_stores()
    
    def _init_memory_stores(self):
        """Initialize memory stores with basic system entries"""
        # Add system metadata
        system_entry = MemoryEntry(
            id="system_metadata",
            content={
                "initialized": datetime.now(),
                "version": "0.1.0",
                "status": "active"
            },
            creation_time=datetime.now(),
            memory_type=MemoryType.LONG_TERM,
            tags=["system", "metadata"],
            priority=10
        )
        self._long_term_memory["system_metadata"] = system_entry
    
    def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry in the appropriate memory system"""
        with self._lock:
            try:
                if entry.memory_type == MemoryType.SHORT_TERM:
                    # Set default TTL for short-term memory if not provided
                    if entry.ttl is None:
                        entry.ttl = timedelta(minutes=30)  # Default 30 minutes
                    
                    self._short_term_memory[entry.id] = entry
                    return True
                elif entry.memory_type == MemoryType.LONG_TERM:
                    self._long_term_memory[entry.id] = entry
                    return True
                else:
                    raise ValueError(f"Unknown memory type: {entry.memory_type}")
            except Exception as e:
                print(f"Error storing memory entry: {e}")
                return False
    
    def retrieve(self, entry_id: str, memory_type: Optional[MemoryType] = None) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by ID"""
        with self._lock:
            if memory_type == MemoryType.SHORT_TERM or memory_type is None:
                entry = self._short_term_memory.get(entry_id)
                if entry and self._is_expired(entry):
                    self._remove_expired_entry(entry_id, MemoryType.SHORT_TERM)
                    entry = None
                if entry:
                    return entry
            
            if memory_type == MemoryType.LONG_TERM or memory_type is None:
                entry = self._long_term_memory.get(entry_id)
                if entry and self._is_expired(entry):
                    self._remove_expired_entry(entry_id, MemoryType.LONG_TERM)
                    entry = None
                if entry:
                    return entry
            
            return None
    
    def search(self, tags: Optional[List[str]] = None, memory_type: Optional[MemoryType] = None) -> List[MemoryEntry]:
        """Search for memory entries by tags and/or memory type"""
        with self._lock:
            results = []
            
            # Search in specified memory type or both
            memory_stores = []
            if memory_type == MemoryType.SHORT_TERM or memory_type is None:
                memory_stores.append((self._short_term_memory, MemoryType.SHORT_TERM))
            if memory_type == MemoryType.LONG_TERM or memory_type is None:
                memory_stores.append((self._long_term_memory, MemoryType.LONG_TERM))
            
            for memory_store, mem_type in memory_stores:
                for entry in memory_store.values():
                    if self._is_expired(entry):
                        self._remove_expired_entry(entry.id, mem_type)
                        continue
                    
                    if tags is None or any(tag in entry.tags for tag in tags):
                        results.append(entry)
            
            # Sort by priority (descending) then by creation time (descending)
            results.sort(key=lambda x: (x.priority, x.creation_time), reverse=True)
            return results
    
    def update(self, entry_id: str, content: Any, tags: Optional[List[str]] = None) -> bool:
        """Update an existing memory entry"""
        with self._lock:
            # Try to find in both memory types
            entry = self._short_term_memory.get(entry_id) or self._long_term_memory.get(entry_id)
            
            if not entry or self._is_expired(entry):
                return False
            
            # Update content and tags if provided
            entry.content = content
            if tags is not None:
                entry.tags = tags
            
            return True
    
    def delete(self, entry_id: str, memory_type: Optional[MemoryType] = None) -> bool:
        """Delete a memory entry"""
        with self._lock:
            if memory_type == MemoryType.SHORT_TERM:
                if entry_id in self._short_term_memory:
                    del self._short_term_memory[entry_id]
                    return True
            elif memory_type == MemoryType.LONG_TERM:
                if entry_id in self._long_term_memory:
                    del self._long_term_memory[entry_id]
                    return True
            else:
                # Try both memory types
                deleted = False
                if entry_id in self._short_term_memory:
                    del self._short_term_memory[entry_id]
                    deleted = True
                if entry_id in self._long_term_memory:
                    del self._long_term_memory[entry_id]
                    deleted = True
                return deleted
            
            return False
    
    def cleanup_expired(self):
        """Clean up expired entries from memory"""
        with self._lock:
            # Clean up short-term memory
            expired_short = [
                key for key, entry in self._short_term_memory.items()
                if self._is_expired(entry)
            ]
            for key in expired_short:
                del self._short_term_memory[key]
            
            # Clean up long-term memory (though typically these wouldn't expire)
            expired_long = [
                key for key, entry in self._long_term_memory.items()
                if self._is_expired(entry)
            ]
            for key in expired_long:
                del self._long_term_memory[key]
    
    def _is_expired(self, entry: MemoryEntry) -> bool:
        """Check if a memory entry has expired"""
        if entry.ttl is None:
            return False  # No TTL means no expiration
        
        return datetime.now() - entry.creation_time > entry.ttl
    
    def _remove_expired_entry(self, entry_id: str, memory_type: MemoryType):
        """Remove an expired entry"""
        if memory_type == MemoryType.SHORT_TERM:
            self._short_term_memory.pop(entry_id, None)
        else:  # LONG_TERM
            self._long_term_memory.pop(entry_id, None)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        with self._lock:
            self.cleanup_expired()  # Clean up before reporting stats
            
            return {
                "short_term": {
                    "count": len(self._short_term_memory),
                    "size_estimate": sum(len(str(entry.content)) for entry in self._short_term_memory.values())
                },
                "long_term": {
                    "count": len(self._long_term_memory),
                    "size_estimate": sum(len(str(entry.content)) for entry in self._long_term_memory.values())
                },
                "timestamp": datetime.now().isoformat()
            }
    
    def clear_memory(self, memory_type: Optional[MemoryType] = None):
        """Clear all entries from specified memory type or all memory"""
        with self._lock:
            if memory_type == MemoryType.SHORT_TERM or memory_type is None:
                self._short_term_memory.clear()
            if memory_type == MemoryType.LONG_TERM or memory_type is None:
                self._long_term_memory.clear()