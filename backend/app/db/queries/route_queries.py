"""Cypher fragments for routing edges in the graph."""

# Labels are validated in seed loader (allowlist) before formatting.


def merge_route_to(from_label: str, to_label: str) -> str:
    """Build MERGE for ROUTE_TO between two typed nodes (ids must be unique per label)."""
    return f"""
MATCH (a:{from_label} {{id: $from_id}})
MATCH (b:{to_label} {{id: $to_id}})
MERGE (a)-[r:ROUTE_TO]->(b)
SET r.distance_km = $distance_km,
    r.eta_minutes = $eta_minutes,
    r.edge_id = $edge_id
"""


LIST_ROUTE_EDGES = """
MATCH (a)-[r:ROUTE_TO]->(b)
RETURN r.edge_id AS id, a.id AS from_id, b.id AS to_id,
       r.distance_km AS distance_km, r.eta_minutes AS eta_minutes
"""
