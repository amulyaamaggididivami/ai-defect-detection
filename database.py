import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

DB_FILE = Path("detections.json")

def load_detections() -> List[Dict]:
    """Load all detection records from file"""
    if not DB_FILE.exists():
        return []
    
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_detection(filename: str, has_defect: bool, confidence: float, defect_type: str = None):
    """Save a new detection record"""
    detections = load_detections()
    
    record = {
        "timestamp": datetime.now().isoformat(),
        "filename": filename,
        "has_defect": has_defect,
        "confidence": confidence,
        "defect_type": defect_type
    }
    
    detections.append(record)
    
    with open(DB_FILE, 'w') as f:
        json.dump(detections, f, indent=2)

def get_recent_defects(hours: int = 1) -> List[Dict]:
    """Get defects detected in the last N hours"""
    detections = load_detections()
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    recent_defects = [
        d for d in detections
        if d["has_defect"] and datetime.fromisoformat(d["timestamp"]) > cutoff_time
    ]
    
    # Sort by timestamp, most recent first
    recent_defects.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return recent_defects

def get_all_detections(hours: int = 24) -> List[Dict]:
    """Get all detections (defect and no defect) from last N hours"""
    detections = load_detections()
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    recent = [
        d for d in detections
        if datetime.fromisoformat(d["timestamp"]) > cutoff_time
    ]
    
    # Sort by timestamp, most recent first
    recent.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return recent

def clear_all_detections():
    """Clear all detection history"""
    with open(DB_FILE, 'w') as f:
        json.dump([], f)
