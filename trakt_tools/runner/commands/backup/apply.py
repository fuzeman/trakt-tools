import click


@click.command('backup:apply')
def backup_apply():
    "Apply backup to a Trakt.tv profile."
