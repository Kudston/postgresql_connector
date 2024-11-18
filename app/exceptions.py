from fastapi import HTTPException, status

from fastapi import HTTPException, status

class GeneralException(Exception):
    pass

def handle_bad_request_exception(exception: Exception):
    """Raises an 400 HTTPException"""

    raise HTTPException(
        detail=str(exception), status_code=status.HTTP_400_BAD_REQUEST
    ) from exception


def handle_not_found_exception(exception: Exception):
    """Raises an 404 HTTPException"""

    raise HTTPException(
        detail=str(exception), status_code=status.HTTP_404_NOT_FOUND
    ) from exception


def handle_conflict_exception(exception: Exception):
    """Raises an 409 HTTPException"""

    raise HTTPException(
        detail=str(exception), status_code=status.HTTP_409_CONFLICT
    ) from exception


def handle_file_too_large_exception(exception: Exception):
    """Raises an 413 HTTPException"""

    raise HTTPException(
        detail=str(exception), status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    ) from exception


def handle_forbidden_exception(exception: Exception):
    """Raises an 403 HTTPException"""

    raise HTTPException(
        detail=str(exception), status_code=status.HTTP_403_FORBIDDEN
    ) from exception


def invalid_auth_credentials_exception(authenticate_value: str = "Bearer"):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": f"{authenticate_value}"},
    )
