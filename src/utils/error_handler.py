from fastapi import HTTPException

def check_found(resource, name: str = "Register"):
    """
    Checks if a resource retrieved from the database exists.
    Raises a 404 error if not found.
    
    Usage:
    user = db.query(User).get(user_id)
    check_found(user, "User")
    """
    if not resource:
        raise HTTPException(status_code=404, detail=f"{name} not found")

def raise_bad_request(message: str):
    """Raises a generic 400 Bad Request error."""
    raise HTTPException(status_code=400, detail=message)

def raise_unauthorized(message: str = "Unauthorized operation"):
    """Raises a generic 401 Unauthorized error."""
    raise HTTPException(status_code=401, detail=message)