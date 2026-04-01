"""
Survivor Detection Module

Simulates survivor detection probabilities based on environmental risk level.
Survivors are statistically more likely to be found in SAFE zones
(they have moved away from danger) compared to HIGH-risk zones.
"""

import random
import time
import uuid
from typing import Optional, Dict

from config.settings import PROB_SAFE, PROB_MEDIUM, PROB_HIGH


def detect_survivor(x: int, y: int, risk_level: str) -> Optional[Dict]:
    """
    Attempt to detect a survivor at the given coordinates.
    
    Detection probability varies by risk level:
    - SAFE: Higher probability (survivors fled to safety)
    - MEDIUM: Medium probability
    - HIGH: Low probability (danger zone)
    
    Args:
        x: X coordinate on grid
        y: Y coordinate on grid
        risk_level: Current risk classification ('SAFE', 'MEDIUM', 'HIGH')
    
    Returns:
        Survivor dictionary if detected, None otherwise.
    """
    probabilities = {
        'SAFE': PROB_SAFE,
        'MEDIUM': PROB_MEDIUM,
        'HIGH': PROB_HIGH
    }
    
    prob = probabilities.get(risk_level, 0.0)
    
    if random.random() < prob:
        survivor_id = f"VICTIM-{uuid.uuid4().hex[:6].upper()}"
        
        return {
            'id': survivor_id,
            'x': x,
            'y': y,
            'timestamp': time.time(),
            'status': 'VERIFIED',
            'risk_level_at_detection': risk_level
        }
    
    return None


def create_survivor_record(x: int, y: int, status: str = 'VERIFIED') -> Dict:
    """
    Create a survivor record manually (for testing or manual entry).
    
    Args:
        x: X coordinate
        y: Y coordinate
        status: Survivor status ('VERIFIED', 'UNVERIFIED')
    
    Returns:
        Survivor dictionary record.
    """
    return {
        'id': f"VICTIM-{uuid.uuid4().hex[:6].upper()}",
        'x': x,
        'y': y,
        'timestamp': time.time(),
        'status': status
    }


def format_survivor_id(index: int) -> str:
    """
    Generate a formatted survivor ID with index.
    
    Args:
        index: Survivor sequence number
    
    Returns:
        Formatted survivor ID string.
    """
    return f"VICTIM-{index:04d}"
