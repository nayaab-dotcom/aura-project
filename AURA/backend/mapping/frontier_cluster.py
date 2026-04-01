"""
Frontier Clustering Module

Reduces decision noise by grouping nearby frontiers into clusters.
Each cluster is represented by a single target for evaluation.
"""

import math
from typing import List, Tuple, Set


def cluster_frontiers(
    frontiers: List[Tuple[int, int]],
    radius: int = 3,
    max_clusters: int = 30
) -> List[Tuple[int, int]]:
    """
    Cluster nearby frontiers into groups.
    
    Args:
        frontiers: List of frontier coordinates
        radius: Distance threshold for clustering (cells)
        max_clusters: Maximum number of clusters to return
    
    Returns:
        List of clustered frontier representatives (centroids)
    """
    if not frontiers:
        return []
    
    if len(frontiers) <= max_clusters:
        return frontiers
    
    clusters = []
    assigned = set()
    
    for frontier in frontiers:
        if frontier in assigned:
            continue
        
        cluster = [frontier]
        assigned.add(frontier)
        
        for other in frontiers:
            if other in assigned:
                continue
            
            dist = math.sqrt(
                (frontier[0] - other[0])**2 + 
                (frontier[1] - other[1])**2
            )
            
            if dist <= radius:
                cluster.append(other)
                assigned.add(other)
        
        centroid = _compute_centroid(cluster)
        clusters.append(centroid)
    
    if len(clusters) > max_clusters:
        clusters = _reduce_clusters(clusters, max_clusters)
    
    return clusters


def _compute_centroid(cluster: List[Tuple[int, int]]) -> Tuple[int, int]:
    """Compute the centroid of a cluster."""
    if not cluster:
        return (0, 0)
    
    if len(cluster) == 1:
        return cluster[0]
    
    avg_x = sum(c[0] for c in cluster) / len(cluster)
    avg_y = sum(c[1] for c in cluster) / len(cluster)
    
    return (round(avg_x), round(avg_y))


def _reduce_clusters(
    clusters: List[Tuple[int, int]],
    max_clusters: int
) -> List[Tuple[int, int]]:
    """
    Reduce clusters to max count by selecting spread-out representatives.
    Uses furthest-point sampling.
    """
    if len(clusters) <= max_clusters:
        return clusters
    
    selected = []
    remaining = clusters.copy()
    
    center_x = 25
    center_y = 25
    
    first = min(remaining, key=lambda c: math.sqrt((c[0]-center_x)**2 + (c[1]-center_y)**2))
    selected.append(first)
    remaining.remove(first)
    
    while remaining and len(selected) < max_clusters:
        furthest = max(remaining, key=lambda c: min(
            math.sqrt((c[0]-s[0])**2 + (c[1]-s[1])**2) for s in selected
        ))
        selected.append(furthest)
        remaining.remove(furthest)
    
    return selected


def get_cluster_info(frontiers: List[Tuple[int, int]], radius: int = 3) -> dict:
    """Get statistics about frontier clustering."""
    clusters = cluster_frontiers(frontiers, radius, max_clusters=100)
    
    return {
        'total_frontiers': len(frontiers),
        'cluster_count': len(clusters),
        'reduction_ratio': len(frontiers) / len(clusters) if clusters else 0
    }