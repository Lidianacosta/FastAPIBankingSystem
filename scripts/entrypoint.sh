#!/bin/sh
alembic upgrade head
python -m src.commands.init_db
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
