from trakt_tools.core.authentication import authenticate
from trakt_tools.tasks.clean.duplicates.main import CleanDuplicatesTask
import click


@click.command('clean:duplicates', )
@click.option('--token', default=None, help='Trakt.tv authentication token.')
@click.option('--delta-max', default=10 * 60, help='Maximum delta to consider as duplicate')
@click.option('--no-backup', is_flag=True, help='Disable automatic profile backup')
@click.option('--review/--no-review')
@click.pass_context
def clean_duplicates(ctx, token, delta_max, no_backup):
    "Remove duplicate scrobbles from a Trakt.tv profile."

    if not token:
        success, token = authenticate()

        if not success:
            print 'Authentication failed'
            exit(1)

    # Run task
    success = CleanDuplicatesTask(ctx.parent.backup_dir, delta_max).run(
        token=token,
        backup=not no_backup
    )

    if not success:
        exit(1)
