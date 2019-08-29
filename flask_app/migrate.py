from alembic.config import main
# please check sqlalchemy.uri config in alembic.ini before run migration

# example cli:
# alembic init alembic
# alembic revision --autogenerate -m "add root_cause table"

# alembic upgrade head
# alembic upgrade +2
# alembic downgrade -1
# alembic upgrade ae10+2
# alembic upgrade --sql bc25b5f8939f:6c55e0560fd4

# alembic current
# alembic history --verbose


if __name__ == "__main__":
    main()
