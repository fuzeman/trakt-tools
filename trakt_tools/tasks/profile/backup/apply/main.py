from trakt_tools.core.input import boolean_input
from trakt_tools.models import Profile
from trakt_tools.tasks.base import Task
from .handlers import HistoryHandler

from trakt import Trakt

import logging

log = logging.getLogger(__name__)


class CreateApplyTask(Task):
    # TODO: implement other handlers
    handlers = [
        # CollectionHandler,
        HistoryHandler,
        # PlaybackHandler,
        # RatingsHandler,
        # WatchlistHandler
    ]

    def __init__(self, backup_zip, per_page=1000, debug=False, rate_limit=20):
        super(CreateApplyTask, self).__init__(debug=debug, rate_limit=rate_limit)

        self.backup_zip = backup_zip
        self.per_page = per_page

    def run(self, token):
        log.debug('run()')

        # Process applying backup
        with Trakt.configuration.oauth(token=token):
            return self.process()

    def process(self, profile=None):
        log.debug('process()')

        if not profile:
            print('Requesting profile...')
            profile = Profile.fetch(
                self.per_page,
                self.rate_limit
            )

        if not profile:
            raise Exception('Unable to fetch profile')

        print('Logged in as %r' % profile.username)
        print()

        if not boolean_input('Would you like to continue?', default=True):
            exit(0)

        print()

        # Apply backup
        return self.apply_backup()

    def apply_backup(self):
        for handler in self.handlers:
            h = handler()

            if not h.run(self.backup_zip):
                print('Unable to apply backup, handler %r failed' % h)
                return False

            print()
