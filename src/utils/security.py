"""Security operations and JWT management.

Provides dependencies for authenticating users, generating access tokens,
and extracting the current user from active requests.
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from src.core.config import settings
from src.schemas.auth import TokenData
from src.schemas.user import User
from src.services.user import UserServiceDep
from src.utils.password import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


async def authenticate_user(
    username: str, password: str, user_service: UserServiceDep
):
    """Authenticate a user using their username and password.

    Args:
        username: The attempted username.
        password: The attempted plain text password.
        user_service: Dependency providing user database operations.

    Returns:
        The User instance if authentication succeeds, False otherwise.

    """
    user = await user_service.get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """Generate a JWT access token encoding the provided data.

    Args:
        data: A dict containing payload items (e.g., {"sub": username}).
        expires_delta: Optional timedelta for token expiration. If none,
            expires in 15 minutes.

    Returns:
        The encoded JWT string.

    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], user_service: UserServiceDep
):
    """Retrieve the current user from an incoming JWT token.

    Validates token signature and expiration, extracts the username, and fetches
    the corresponding user record from the database.

    Args:
        token: The bearer JWT token from the request authorization header.
        user_service: Dependency providing user database operations.

    Returns:
        The current User model instance.

    Raises:
        HTTPException: 401 if credentials cannot be validated or user doesn't exist.

    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError as e:
        raise credentials_exception from e
    user = await user_service.get_user_by_username(str(token_data.username))
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Retrieve the current user ensuring their account is active.

    Depends on `get_current_user` and adds an extra layer of validation.

    Args:
        current_user: The authenticated User object.

    Returns:
        The active User instance.

    Raises:
        HTTPException: 400 if the user account is disabled.

    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def forbid_demo_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Ensure the current user is not a demo user.

    Used to protect sensitive operations from being performed by demo accounts.

    Args:
        current_user: The authenticated active user.

    Returns:
        The current user if they are not a demo user.

    Raises:
        HTTPException: 403 if the user is a demo user.

    """
    if current_user.is_demo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action not permitted in demonstration mode.",
        )
    return current_user
