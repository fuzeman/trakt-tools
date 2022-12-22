from . import commands

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
@click.option('--debug/--no-debug', help='Display debug messages.')
@click.option('--rate-limit', default=20, help='Maximum number of requests per minute. (default: 20)')
@click.option('--no-confirm', is_flag=True, show_default=True, help='Do not confirm some actions')
@click.pass_context
def cli(ctx, debug, rate_limit, no_confirm):
    # Setup logging level
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.WARN
    )

    # Update context
    ctx.debug = debug
    ctx.rate_limit = rate_limit
    ctx.confirm = not no_confirm


# Add commands
cli.add_command(commands.profile_backup_apply)
cli.add_command(commands.profile_backup_create)
cli.add_command(commands.history_duplicates_merge)
cli.add_command(commands.history_duplicates_scan)


def get_prog():
    try:
        if os.path.basename(sys.argv[0]) in ('__main__.py', '-c'):
            return '%s -m trakt_tools' % sys.executable

        if os.path.basename(sys.argv[0]) == 'run.py':
            return 'run.py'
    except (AttributeError, TypeError, IndexError):
        pass

    return 'trakt_tools'


def main():
    cli(prog_name=get_prog(), obj={}, max_content_width=100)


if __name__ == '__main__':
    main()
