from trakt_tools.core.input import boolean_input
from trakt_tools.models import Profile
from trakt_tools.tasks.backup.create.main import CreateBackupTask
from trakt_tools.tasks.clean.duplicates.scanner.main import Scanner
from trakt_tools.tasks.core.base import Task

from datetime import datetime
from trakt import Trakt
import logging
import time

log = logging.getLogger(__name__)


class CleanDuplicatesTask(Task):
    def __init__(self, backup_dir, rate_limit, delta_max):
        super(CleanDuplicatesTask, self).__init__()

        self.backup_dir = backup_dir
        self.rate_limit = rate_limit
        self.delta_max = delta_max

        self.scanner = None

    def run(self, token, backup=None, review=None):
        log.debug('run() - token: %r', token)

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
            profile = Profile.fetch(self.rate_limit)

        if not profile:
            print 'Unable to fetch profile'
            exit(1)

        print 'Logged in as %r' % profile

        if not boolean_input('Would you like to continue?', default=True):
            exit(0)

        # Create backup
        if backup is None:
            backup = boolean_input('Create profile backup?', default=True)

        if backup and not self._create_backup(profile):
            print 'Unable to create backup'
            exit(1)

        # Construct new duplicate scanner
        self.scanner = Scanner(self.delta_max)

        # Scan history for duplicates
        print 'Scanning for duplicates...'

        if not self.scanner.run(profile):
            return False

        if len(self.scanner.shows) or len(self.scanner.movies):
            print 'Found %d show(s) and %d movie(s) with duplicates' % (
                len(self.scanner.shows),
                len(self.scanner.movies)
            )
        else:
            print 'Unable to find any duplicates'
            exit(0)

        # Remove duplicates
        return self.execute(review)

    def execute(self, review=None):
        if review is None:
            review = boolean_input('Review every action?', default=True)

        return False

    # region Private methods

    def _create_backup(self, profile):
        return CreateBackupTask(
            self.backup_dir,
            self.rate_limit
        ).create_backup(
            profile
        )

    # endregion
