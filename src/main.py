from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.controllers import checking_account, individual_client, transactions
from src.utils.database import async_create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await async_create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(
    individual_client.router,
    prefix="/api",
    tags=["Client", "Individual"],
)
app.include_router(
    checking_account.router,
    prefix="/api/individual-clients/{client_id}",
    tags=["Acount", "Checking"],
)
app.include_router(
    transactions.deposit_router,
    prefix="/api/checking-accounts/{account_id}",
    tags=["Transactions", "Deposit"],
)
app.include_router(
    transactions.withdrawal_router,
    prefix="/api/checking-accounts/{account_id}",
    tags=["Transactions", "Withdrawal"],
)
