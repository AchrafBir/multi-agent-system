import uuid

def generate_unique_id(prefix=""):
    """Generates a unique ID with an optional prefix."""
    return f"{prefix}{uuid.uuid4().hex[:8]}"