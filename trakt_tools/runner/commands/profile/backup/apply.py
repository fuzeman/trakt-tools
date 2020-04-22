from trakt_tools.core.authentication import authenticate
from trakt_tools.tasks import CreateApplyTask

import click
import os


@click.command('profile:backup:apply', short_help="Apply backup to a Trakt.tv profile")
@click.argument('backup_zip', type=click.Path(exists=True))
@click.option(
    '--token',
    default=None,
    help='Trakt.tv authentication token. (default: prompt)'
)
@click.option(
    '--per-page',
    default=1000,
    help='Request page size. (default: 1000)'
)
def profile_backup_apply(backup_zip, token, per_page):
    """Apply backup to a Trakt.tv profile

    BACKUP_ZIP is the location of the zip file created by the profile:history:backup command
    """

    if not token:
        success, token = authenticate()

        if not success:
            print('Authentication failed')
            exit(1)

        print()

    # Ensure backup directory exists
    if not os.path.exists(backup_zip):
        print('No such backup zip: "{}"'.format(backup_zip))
        exit(1)

    # Run task
    success = CreateApplyTask(backup_zip).run(token=token)

    if not success:
        exit(1)
