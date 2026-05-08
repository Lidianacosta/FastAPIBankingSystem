"""Main application entry point.

Configures the FastAPI application, includes API routers, and sets up
the database connection lifespan.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.controllers import (
    auth,
    checking_account,
    individual_client,
    transactions,
    user,
)
from src.utils.database import async_create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application lifecycle.

    Handles startup tasks such as creating database tables and
    shutdown cleanup.

    Args:
        app: The FastAPI application instance.

    """
    await async_create_db_and_tables()
    yield


tags_metadata = [
    {"name": "Auth", "description": "Authentication"},
    {"name": "Users", "description": "User management"},
    {"name": "Individual", "description": "Individual clients"},
    {"name": "Checking", "description": "Checking accounts"},
    {"name": "Deposit", "description": "Deposits"},
    {"name": "Withdrawal", "description": "Withdrawals"},
]


app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)


app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(user.router, prefix="/api", tags=["Users"])
app.include_router(
    individual_client.router,
    prefix="/api",
    tags=["Individual"],
)
app.include_router(
    checking_account.router,
    prefix="/api/individual-clients/{client_id}",
    tags=["Checking"],
)
app.include_router(
    transactions.deposit_router,
    prefix="/api/checking-accounts/{account_id}",
    tags=["Deposit"],
)
app.include_router(
    transactions.withdrawal_router,
    prefix="/api/checking-accounts/{account_id}",
    tags=["Withdrawal"],
)
