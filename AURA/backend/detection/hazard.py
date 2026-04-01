"""
Hazard Detection Module

Classifies environmental risk based on temperature and gas sensor readings.
Uses configurable thresholds from settings.
"""

from config.settings import (
    RISK_TEMP_HIGH, RISK_TEMP_MEDIUM,
    RISK_GAS_HIGH, RISK_GAS_MEDIUM,
    COST_SAFE, COST_MEDIUM, COST_HIGH
)


def classify_risk(temp: float, gas: float) -> str:
    """
    Classify environmental risk based on sensor readings.
    
    Classification rules:
    - HIGH: temp > 70 OR gas > 70
    - MEDIUM: temp > 40 OR gas > 40
    - SAFE: otherwise
    
    Args:
        temp: Temperature reading in degrees
        gas: Gas level reading
    
    Returns:
        Risk level as string: 'HIGH', 'MEDIUM', or 'SAFE'
    """
    if temp > RISK_TEMP_HIGH or gas > RISK_GAS_HIGH:
        return 'HIGH'
    elif temp > RISK_TEMP_MEDIUM or gas > RISK_GAS_MEDIUM:
        return 'MEDIUM'
    return 'SAFE'


def risk_to_cost(risk_level: str) -> int:
    """
    Convert risk level to A* pathfinding cost.
    
    Higher costs make paths through dangerous areas
    less attractive to the pathfinding algorithm.
    
    Args:
        risk_level: Risk classification string
    
    Returns:
        Numerical cost for pathfinding (1=SAFE, 20=MEDIUM, 1000=HIGH)
    """
    costs = {
        'HIGH': COST_HIGH,
        'MEDIUM': COST_MEDIUM,
        'SAFE': COST_SAFE
    }
    return costs.get(risk_level, COST_SAFE)


def get_risk_color(risk_level: str) -> str:
    """
    Get color code for risk level visualization.
    
    Args:
        risk_level: Risk classification string
    
    Returns:
        Hex color code for UI display
    """
    colors = {
        'HIGH': '#ff3131',    # Red
        'MEDIUM': '#ffbf00',  # Yellow
        'SAFE': '#4be277'     # Green
    }
    return colors.get(risk_level, '#4be277')
