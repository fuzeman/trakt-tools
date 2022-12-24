from __future__ import print_function

from trakt_tools.core.authentication import authenticate
from trakt_tools.tasks import ScanHistoryDuplicatesTask

import click
import os


@click.command('history:duplicates:scan')
@click.option(
    '--token',
    default=os.environ.get('TRAKT_TOKEN') or None,
    help='Trakt.tv authentication token. Overwrites TRAKT_TOKEN env var. (default: prompt)'
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
@click.pass_context
def history_duplicates_scan(ctx, token, delta_max, per_page):
    """Scan for duplicate history records"""

    if not token:
        success, token = authenticate()

        if not success:
            print('Authentication failed')
            exit(1)

        print()

    # Run task
    success = ScanHistoryDuplicatesTask(
        delta_max=delta_max,
        per_page=per_page,

        debug=ctx.parent.debug,
        rate_limit=ctx.parent.rate_limit
    ).run(
        token=token
    )

    if not success:
        exit(1)
