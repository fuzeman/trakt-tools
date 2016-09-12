from trakt_tools.tasks.core.base import Task

from trakt import Trakt
import logging

log = logging.getLogger(__name__)


class CleanDuplicates(Task):
    def __init__(self, backup_dir):
        super(CleanDuplicates, self).__init__()

        self.backup_dir = backup_dir

    def run(self, token):
        log.debug('CleanDuplicates.run() - token: %r', token)

        # Process backup download
        with Trakt.configuration.oauth(token=token):
            self.process()

    def process(self, username=None):
        if not username:
            username = self.get_username()

        log.debug('Username: %r', username)

        # Create backup

