from trakt_tools.core.authentication import authenticate
from trakt_tools.tasks.clean.duplicates.main import CleanDuplicates
import click


@click.command('clean:duplicates')
@click.option('--token', default=None, help='Trakt.tv authentication token.')
@click.pass_context
def clean_duplicates(ctx, token):
    "Remove duplicate scrobbles from a Trakt.tv profile."

    if not token:
        success, token = authenticate()

        if not success:
            print 'Authentication failed'
            exit(1)

    # Download data from profile
    task = CleanDuplicates(ctx.parent.backup_dir)
    task.run(token)
