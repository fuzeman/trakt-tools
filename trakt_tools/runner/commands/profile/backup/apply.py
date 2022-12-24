from trakt_tools.core.authentication import authenticate
from trakt_tools.tasks import CreateApplyTask

import click
import os


@click.command('profile:backup:apply', short_help="Apply backup to a Trakt.tv profile (history)")
@click.argument('backup_zip', type=click.Path(exists=True))
@click.option(
    '--token',
    default=os.environ.get('TRAKT_TOKEN') or None,
    help='Trakt.tv authentication token. Overwrites TRAKT_TOKEN env var. (default: prompt)'
)
def profile_backup_apply(backup_zip, token):
    """Apply backup to a Trakt.tv profile.

    Only history can be applied to your profile currently. Support for applying collection, playback, ratings, and
    watchlist data has not been implemented yet.

    Note: History already on your profile will be duplicated, `history:duplicates:merge` can be run afterwards to merge
    any duplicates in your history.

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
