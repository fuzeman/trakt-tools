from trakt_tools.runner import commands
from trakt import Trakt
import click
import logging
import os
import sys


# Configure trakt.py
# TODO use the trakt-tools api key
Trakt.configuration.defaults.app(
    id='10248'
)

Trakt.configuration.defaults.client(
    id='023e5e78690b1d8014b40ecff062f02f9fbe187649920b06a5e56939b4514ddf',
    secret='30bb522275beb2710334cf4db18ca157b5fc85d1e17c913229bf853a9390a1ea'
)


# Initialize command-line parser
@click.group()
@click.option('--backup-dir', default=None, help='Directory to store backups.')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.pass_context
def cli(ctx, backup_dir, debug):
    if not backup_dir:
        backup_dir = os.path.join(os.curdir, 'backups')

    # Setup logging level
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO
    )

    # Update context with absolute path for `backup_dir`
    ctx.backup_dir = os.path.abspath(backup_dir)

    # Ensure directory exists
    if not os.path.exists(ctx.backup_dir):
        os.makedirs(ctx.backup_dir)

# Add commands
cli.add_command(commands.backup_apply)
cli.add_command(commands.backup_create)
cli.add_command(commands.clean_duplicates)


def get_prog():
    try:
        if os.path.basename(sys.argv[0]) in ('__main__.py', '-c'):
            return '%s -m trakt_tools' % sys.executable
    except (AttributeError, TypeError, IndexError):
        pass

    return 'trakt_tools'


def main():
    cli(prog_name=get_prog(), obj={}, max_content_width=100)


if __name__ == '__main__':
    main()
