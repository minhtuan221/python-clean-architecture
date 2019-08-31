import click
from app.domain.model.base import init_database, Base, ConnectionPool
from app import config

@click.group()
@click.option('-m', '--mode',
              default='develop',
              help='mode develop or production'
              )
@click.pass_context
def cli(ctx, mode: str):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below
    ctx.ensure_object(dict)

    ctx.obj['mode'] = mode




@cli.command()
@click.option('-s', '--sql-url',
              default="sqlite:///./test.db",
              help='database connection string'
              )
@click.pass_context
def initdb(ctx, sql_url: str):
    click.echo('Initialized the database')
    mode = ctx.obj['mode']
    if mode in config.config:
        config.cli_config = config.config[mode]
    init_database(config.cli_config.DATABASE_URL)


@cli.command()
@click.pass_context
def dropdb(ctx):
    click.echo('Dropped the database')

@cli.command()
@click.option('-a', '--alembic-config-file',
              default="alembic.ini",
              help='alembic config file for migration. Run python migrate.py for migrating database'
              )
@click.pass_context
def migrate(ctx, alembic_config_file):
    click.echo('Migrate: change database alembic config file to migrate. Please run `python migrate.py` for migrating database')
    mode = ctx.obj['mode']
    import configparser
    alembic_config = configparser.ConfigParser()
    alembic_config.read(alembic_config_file)
    alembic_config['alembic']['sqlalchemy.url'] = config.config[mode].DATABASE_URL
    with open(alembic_config_file, 'w') as configfile:
        alembic_config.write(configfile)


@cli.command()
@click.option('-s', '--sql-url',
              default="sqlite:///./test.db",
              help='database connection string'
              )
@click.option('-p', '--port',
              default="5000",
              help='http port'
              )
@click.pass_context
def runserver(ctx, sql_url: str, port: str):
    click.echo('Server start running')
    mode = ctx.obj['mode']
    if mode in config.config:
        config.cli_config = config.config[mode]
    from .http import app
    app.run(host='0.0.0.0', port=config.cli_config.PORT)


if __name__ == "__main__":
    cli()
