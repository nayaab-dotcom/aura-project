"""
Hazard Detection Module - Classifies environmental risk based on sensor readings.
"""

from config import (
    RISK_TEMP_HIGH, RISK_TEMP_MEDIUM,
    RISK_GAS_HIGH, RISK_GAS_MEDIUM,
    COST_SAFE, COST_MEDIUM, COST_HIGH
)


def classify_risk(temp: float, gas: float) -> str:
    """
    Classify environmental risk based on sensor readings.
    
    Rules:
    - HIGH: temp > 70 OR gas > 70
    - MEDIUM: temp > 40 OR gas > 40
    - SAFE: otherwise
    """
    if temp > RISK_TEMP_HIGH or gas > RISK_GAS_HIGH:
        return 'HIGH'
    elif temp > RISK_TEMP_MEDIUM or gas > RISK_GAS_MEDIUM:
        return 'MEDIUM'
    return 'SAFE'


def risk_to_cost(risk_level: str) -> int:
    """Convert risk level to A* pathfinding cost."""
    costs = {'HIGH': COST_HIGH, 'MEDIUM': COST_MEDIUM, 'SAFE': COST_SAFE}
    return costs.get(risk_level, COST_SAFE)


def get_risk_color(risk_level: str) -> str:
    """Get color code for risk level visualization."""
    colors = {'HIGH': '#ff3131', 'MEDIUM': '#ffbf00', 'SAFE': '#4be277'}
    return colors.get(risk_level, '#4be277')
