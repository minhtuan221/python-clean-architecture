import click
from app.domain.model.base import init_database, Base, ConnectionPool
from app import config


@click.group()
def cli():
    pass



@cli.command()
@click.option('-s', '--sql-dsn',
              default="sqlite:///./test.db",
              help='database connection string'
              )
def initdb(sql_dsn: str):
    click.echo('Initialized the database')
    init_database(config.cli_config.DATABASE_URI)


@cli.command()
def dropdb():
    click.echo('Dropped the database')


@cli.command()
@click.option('-s', '--sql-dsn',
              default="sqlite:///./test.db",
              help='database connection string'
              )
@click.option('-p', '--port',
              default="5000",
              help='http port'
              )
@click.option('-m', '--mode',
              default='develop',
              help='mode develop or production'
              )
def runserver(sql_dsn: str, port: str, mode: str):
    click.echo('Server start running')
    if mode in config.config:
        config.cli_config = config.config[mode]
    from .http import app
    app.run(host='0.0.0.0', port=config.cli_config.PORT)


if __name__ == "__main__":
    cli()
