from __future__ import print_function

from trakt_tools.core.authentication import authenticate
from trakt_tools.tasks import MergeHistoryDuplicatesTask

import click
import os


@click.command('history:duplicates:merge')
@click.option(
    '--token',
    default=None,
    help='Trakt.tv authentication token. (default: prompt)'
)
@click.option(
    '--backup-dir',
    default=None,
    help='Directory that backups should be stored in. (default: "./backups")'
)
@click.option(
    '--delta-max',
    default=10 * 60,
    help='Maximum delta between history records to consider as duplicate. (in seconds) (default: 600)'
)
@click.option(
    '--per-page',
    default=1000,
    help='Request page size. (default: 1000)'
)
@click.option(
    '--backup/--no-backup',
    default=None,
    help='Backup profile before applying any changes. (default: prompt)'
)
@click.option(
    '--review/--no-review',
    default=None,
    help='Review each action before applying them. (default: prompt)'
)
@click.pass_context
def history_duplicates_merge(ctx, token, backup_dir, delta_max, per_page, backup, review):
    """Merge duplicate history records"""

    if not token:
        success, token = authenticate()

        if not success:
            print('Authentication failed')
            exit(1)

        print()

    # Set default backup directory
    if not backup_dir:
        backup_dir = os.path.join(os.curdir, 'backups')

    # Ensure backup directory exists
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Run task
    success = MergeHistoryDuplicatesTask(
        backup_dir=backup_dir,
        delta_max=delta_max,
        per_page=per_page,

        debug=ctx.parent.debug,
        rate_limit=ctx.parent.rate_limit
    ).run(
        token=token,
        backup=backup,
        review=review
    )

    if not success:
        exit(1)
