from alembic.config import main
from app import config
# please check sqlalchemy.uri config in alembic.ini before run migration

# example cli:
# alembic init alembic
# alembic revision --autogenerate -m "add root_cause table"

# alembic upgrade head --sql
# alembic upgrade head
# alembic upgrade +2
# alembic downgrade -1
# alembic upgrade ae10+2
# alembic upgrade --sql bc25b5f8939f:6c55e0560fd4

# alembic current
# alembic history --verbose


def migrate(alembic_config_file: str = 'alembic.ini'):
    import configparser
    alembic_config = configparser.ConfigParser()
    alembic_config.read(alembic_config_file)
    # alembic_config['alembic']['sqlalchemy.url'] = config.config['production'].DATABASE_URL
    # with open(alembic_config_file, 'w') as configfile:
    #     alembic_config.write(configfile)
    print('update migration config successful')


if __name__ == "__main__":
    migrate()
    main()
