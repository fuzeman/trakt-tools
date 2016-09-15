from trakt_tools.core.input import boolean_input
from trakt_tools.models import Backup, Profile
from trakt_tools.tasks.core.base import Task
from trakt_tools.tasks.backup.create.handlers import *

from trakt import Trakt
from zipfile import ZipFile, ZIP_DEFLATED
import logging
import os
import shutil

log = logging.getLogger(__name__)


class CreateBackupTask(Task):
    handlers = [
        CollectionHandler,
        HistoryHandler,
        PlaybackHandler,
        RatingsHandler,
        WatchlistHandler
    ]

    def __init__(self, backup_dir, rate_limit):
        super(CreateBackupTask, self).__init__()

        self.backup_dir = backup_dir
        self.rate_limit = rate_limit

    def run(self, token):
        log.debug('run() - token: %r', token)

        # Process backup download
        with Trakt.configuration.oauth(token=token):
            return self.process()

    def process(self, profile=None):
        log.debug('process()')

        if not profile:
            profile = Profile.fetch(self.rate_limit)

        if not profile:
            raise Exception('Unable to fetch profile')

        print 'Logged in as %r' % profile.username

        if not boolean_input('Would you like to continue?', default=True):
            exit(0)

        # Create backup
        return self.create_backup(profile)

    def create_backup(self, profile):
        backup = Backup.create(self.backup_dir, profile.username)

        # Run handlers
        for handler in self.handlers:
            h = handler()

            if not h.run(backup, profile):
                log.error('Handler %r failed', h)
                return False

        # Compress backup
        dest_path = os.path.join(
            self.backup_dir,
            profile.username,
            '%s.zip' % backup.name
        )

        with ZipFile(dest_path, 'w', ZIP_DEFLATED) as archive:
            # Add backup files
            for root, dirs, files in os.walk(backup.path):
                for filename in files:
                    path = os.path.join(root, filename)

                    # Add file to archive
                    archive.write(path, os.path.relpath(path, backup.path))

        # Delete backup directory
        shutil.rmtree(backup.path)

        return True
