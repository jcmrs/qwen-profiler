"""
Unit tests for the MemoryManager component
"""
import pytest
from datetime import datetime, timedelta
from src.core.memory.manager import MemoryManager, MemoryEntry, MemoryType


class TestMemoryManager:
    """Test suite for MemoryManager functionality"""
    
    def setup_method(self):
        """Setup method that runs before each test"""
        self.memory_manager = MemoryManager()
        
        # Clear any existing entries to ensure test isolation
        self.memory_manager.clear_memory()
    
    def test_store_and_retrieve_short_term_memory(self):
        """Test storing and retrieving short-term memory entries"""
        entry = MemoryEntry(
            id="test_entry",
            content={"data": "test content"},
            creation_time=datetime.now(),
            memory_type=MemoryType.SHORT_TERM,
            ttl=timedelta(minutes=10)
        )
        
        # Store the entry
        success = self.memory_manager.store(entry)
        assert success is True
        
        # Retrieve the entry
        retrieved = self.memory_manager.retrieve("test_entry", MemoryType.SHORT_TERM)
        assert retrieved is not None
        assert retrieved.id == "test_entry"
        assert retrieved.content == {"data": "test content"}
        assert retrieved.memory_type == MemoryType.SHORT_TERM
    
    def test_store_and_retrieve_long_term_memory(self):
        """Test storing and retrieving long-term memory entries"""
        entry = MemoryEntry(
            id="long_term_test",
            content={"data": "long term content"},
            creation_time=datetime.now(),
            memory_type=MemoryType.LONG_TERM
        )
        
        # Store the entry
        success = self.memory_manager.store(entry)
        assert success is True
        
        # Retrieve the entry
        retrieved = self.memory_manager.retrieve("long_term_test", MemoryType.LONG_TERM)
        assert retrieved is not None
        assert retrieved.id == "long_term_test"
        assert retrieved.content == {"data": "long term content"}
        assert retrieved.memory_type == MemoryType.LONG_TERM
    
    def test_update_existing_entry(self):
        """Test updating an existing memory entry"""
        entry = MemoryEntry(
            id="update_test",
            content={"data": "initial content"},
            creation_time=datetime.now(),
            memory_type=MemoryType.LONG_TERM
        )
        
        # Store the initial entry
        self.memory_manager.store(entry)
        
        # Update the entry
        update_success = self.memory_manager.update("update_test", {"data": "updated content"})
        assert update_success is True
        
        # Retrieve and verify the updated content
        retrieved = self.memory_manager.retrieve("update_test")
        assert retrieved is not None
        assert retrieved.content == {"data": "updated content"}
    
    def test_search_by_tags(self):
        """Test searching memory entries by tags"""
        entry1 = MemoryEntry(
            id="tag_test_1",
            content={"data": "content 1"},
            creation_time=datetime.now(),
            memory_type=MemoryType.LONG_TERM,
            tags=["test", "unit", "memory"]
        )
        
        entry2 = MemoryEntry(
            id="tag_test_2",
            content={"data": "content 2"},
            creation_time=datetime.now(),
            memory_type=MemoryType.SHORT_TERM,
            tags=["test", "integration"]
        )
        
        # Store both entries
        self.memory_manager.store(entry1)
        self.memory_manager.store(entry2)
        
        # Search for entries with the "test" tag
        results = self.memory_manager.search(tags=["test"])
        assert len(results) == 2  # Both entries have "test" tag
        result_ids = [r.id for r in results]
        assert "tag_test_1" in result_ids
        assert "tag_test_2" in result_ids
    
    def test_delete_entry(self):
        """Test deleting a memory entry"""
        entry = MemoryEntry(
            id="delete_test",
            content={"data": "to be deleted"},
            creation_time=datetime.now(),
            memory_type=MemoryType.SHORT_TERM
        )
        
        # Store the entry
        self.memory_manager.store(entry)
        
        # Verify it exists
        retrieved = self.memory_manager.retrieve("delete_test")
        assert retrieved is not None
        
        # Delete the entry
        delete_success = self.memory_manager.delete("delete_test")
        assert delete_success is True
        
        # Verify it's gone
        retrieved_after_delete = self.memory_manager.retrieve("delete_test")
        assert retrieved_after_delete is None
    
    def test_statistics(self):
        """Test getting memory statistics"""
        # Initially, memory should be empty (except system entries)
        stats = self.memory_manager.get_statistics()
        initial_short_count = stats["short_term"]["count"]
        initial_long_count = stats["long_term"]["count"]
        
        # Add some entries
        for i in range(3):
            entry = MemoryEntry(
                id=f"stat_test_{i}",
                content={"data": f"content {i}"},
                creation_time=datetime.now(),
                memory_type=MemoryType.SHORT_TERM
            )
            self.memory_manager.store(entry)
        
        for i in range(2):
            entry = MemoryEntry(
                id=f"stat_test_long_{i}",
                content={"data": f"long content {i}"},
                creation_time=datetime.now(),
                memory_type=MemoryType.LONG_TERM
            )
            self.memory_manager.store(entry)
        
        # Get updated stats
        updated_stats = self.memory_manager.get_statistics()
        
        # Check that counts increased
        assert updated_stats["short_term"]["count"] == initial_short_count + 3
        assert updated_stats["long_term"]["count"] == initial_long_count + 2
    
    def test_cleanup_expired_entries(self):
        """Test cleanup of expired short-term memory entries"""
        # Create an entry that expires immediately
        expired_entry = MemoryEntry(
            id="expired_test",
            content={"data": "expired content"},
            creation_time=datetime.now() - timedelta(minutes=2),  # Created 2 minutes ago
            memory_type=MemoryType.SHORT_TERM,
            ttl=timedelta(minutes=1)  # TTL is 1 minute, so this is expired
        )

        # Manually add the expired entry to the memory manager's internal storage
        # (bypassing the retrieve mechanism that would clean it immediately)
        self.memory_manager._short_term_memory[expired_entry.id] = expired_entry

        # Verify it exists before cleanup (this will clean it up due to expiration)
        retrieved_before = self.memory_manager.retrieve("expired_test")
        # The retrieved_before should be None because the expired entry gets cleaned up on access
        assert retrieved_before is None

        # Add the expired entry again for testing cleanup_expired directly
        self.memory_manager._short_term_memory[expired_entry.id] = expired_entry

        # At this point, the entry is in memory but expired

        # Get initial count
        initial_count = len(self.memory_manager._short_term_memory)

        # Cleanup expired entries
        self.memory_manager.cleanup_expired()

        # Verify it's been removed after cleanup
        final_count = len(self.memory_manager._short_term_memory)
        assert final_count == initial_count - 1  # Entry was removed

        # Verify it's not retrievable
        retrieved_after = self.memory_manager.retrieve("expired_test")
        assert retrieved_after is None