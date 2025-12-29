"""
Processing Status Store
In-memory store to track classification processing status in real-time
"""
from typing import Dict, List, Optional
from datetime import datetime
import threading

class ProcessingStatus:
    """Store for tracking processing status of classifications"""
    
    def __init__(self):
        self._store: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    def initialize(self, classification_id: str):
        """Initialize status tracking for a classification"""
        with self._lock:
            self._store[classification_id] = {
                "status": "processing",
                "current_step": 0,
                "total_steps": 5,
                "steps": [
                    {"name": "Rear View Analysis", "status": "pending", "message": "Waiting..."},
                    {"name": "Side View Analysis", "status": "pending", "message": "Waiting..."},
                    {"name": "Top View Analysis", "status": "pending", "message": "Waiting..."},
                    {"name": "Udder View Analysis", "status": "pending", "message": "Waiting..."},
                    {"name": "Side-Udder View Analysis", "status": "pending", "message": "Waiting..."}
                ],
                "started_at": datetime.now().isoformat(),
                "completed_at": None,
                "error": None
            }
    
    def update_step(self, classification_id: str, step_index: int, status: str, message: str):
        """Update a specific processing step"""
        with self._lock:
            if classification_id not in self._store:
                return
            
            if 0 <= step_index < len(self._store[classification_id]["steps"]):
                self._store[classification_id]["steps"][step_index]["status"] = status
                self._store[classification_id]["steps"][step_index]["message"] = message
                
                if status == "processing":
                    self._store[classification_id]["current_step"] = step_index + 1
    
    def complete(self, classification_id: str, success: bool = True, error: Optional[str] = None):
        """Mark processing as complete"""
        with self._lock:
            if classification_id not in self._store:
                return
            
            self._store[classification_id]["status"] = "completed" if success else "error"
            self._store[classification_id]["completed_at"] = datetime.now().isoformat()
            if error:
                self._store[classification_id]["error"] = error
    
    def get(self, classification_id: str) -> Optional[Dict]:
        """Get current status for a classification"""
        with self._lock:
            return self._store.get(classification_id)
    
    def remove(self, classification_id: str):
        """Remove status tracking (cleanup)"""
        with self._lock:
            if classification_id in self._store:
                del self._store[classification_id]


# Singleton instance
processing_status = ProcessingStatus()
