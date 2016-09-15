from trakt_tools.core.input import boolean_input
from trakt_tools.models import Profile
from trakt_tools.tasks.profile.backup import CreateBackupTask
from trakt_tools.tasks.base import Task
from .executor import Executor
from ..scan import ScanHistoryDuplicatesTask

from trakt import Trakt
import logging

log = logging.getLogger(__name__)


class MergeHistoryDuplicatesTask(Task):
    def __init__(self, backup_dir, delta_max, per_page=1000, debug=False, rate_limit=20):
        super(MergeHistoryDuplicatesTask, self).__init__(
            debug=debug,
            rate_limit=rate_limit
        )

        self.backup_dir = backup_dir
        self.delta_max = delta_max
        self.per_page = per_page

        self.scanner = None

    def run(self, token, backup=None, review=None):
        log.debug('run()')

        # Process backup download
        with Trakt.configuration.oauth(token=token):
            return self.process(
                backup=backup,
                review=review
            )

    def process(self, profile=None, backup=None, review=None):
        log.debug('process()')

        if not profile:
            print 'Requesting profile...'
            profile = Profile.fetch(
                self.per_page,
                self.rate_limit
            )

        if not profile:
            print 'Unable to fetch profile'
            exit(1)

        print 'Logged in as %r' % profile.username
        print

        if not boolean_input('Would you like to continue?', default=True):
            exit(0)

        print

        # Create backup
        if backup is None:
            backup = boolean_input('Create profile backup?', default=True)
            print

        if backup and not self._create_backup(profile):
            print 'Unable to create backup'
            exit(1)

        print

        # Construct new duplicate scanner
        self.scanner = ScanHistoryDuplicatesTask(
            delta_max=self.delta_max,

            debug=self.debug,
            rate_limit=self.rate_limit
        )

        # Scan history for duplicates
        if not self.scanner.scan(profile):
            exit(1)

        print

        if len(self.scanner.shows) or len(self.scanner.movies):
            print 'Found %d show(s) and %d movie(s) with duplicates' % (
                len(self.scanner.shows),
                len(self.scanner.movies)
            )
        else:
            print 'Unable to find any duplicates'
            exit(0)

        print

        # Execute actions
        if not self.execute(profile, review):
            print 'Unable to execute actions'
            exit(1)

        return True

    def execute(self, profile, review=None):
        if review is None:
            review = boolean_input('Review every action?', default=True)
            print

        executor = Executor(review)

        if not executor.process_shows(profile, self.scanner.shows):
            return False

        if not executor.process_movies(profile, self.scanner.movies):
            return False

        print 'Done'
        return True

    # region Private methods

    def _create_backup(self, profile):
        return CreateBackupTask(
            backup_dir=self.backup_dir,

            debug=self.debug,
            rate_limit=self.rate_limit
        ).create_backup(
            profile
        )

    # endregion
