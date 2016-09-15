from trakt_tools.tasks.clean.duplicates.scanner.models import Entry, Record

from trakt.mapper import SyncMapper
from trakt.objects import Episode
import logging

log = logging.getLogger(__name__)


class Scanner(object):
    def __init__(self, delta_max):
        self.delta_max = delta_max

        self.shows = {}
        self.movies = {}

        self._current_shows = {}
        self._current_movies = {}

    def run(self, profile):
        # Process items
        for i, count, page in profile.get_pages('/sync/history'):
            print '[history](%02d/%02d) Processing %d items...' % (i, count, len(page))

            for item in page:
                # Process item, stop scanning if an error is encountered
                if not self.process(item):
                    log.error('Unable to process item: %r', item)
                    return False

        # Find duplicated items
        self.shows = self._get_duplicated_items(self._current_shows)
        self.movies = self._get_duplicated_items(self._current_movies)

        # Destroy item stores
        self._current_shows = None
        self._current_movies = None
        return True

    def process(self, data):
        if 'episode' in data:
            return self.process_item(self._current_shows, SyncMapper.episode(None, None, data))

        if 'movie' in data:
            return self.process_item(self._current_movies, SyncMapper.movie(None, None, data))

        log.warn('Unknown item: %r', data)
        return False

    def process_item(self, store, current, create_shows=True):
        if create_shows and isinstance(current, Episode):
            show_key = current.show.get_key('trakt')

            if not show_key:
                log.warn('Unable to find "trakt" key in show: %r', current.show)
                return False

            if show_key not in store:
                store[show_key] = Entry.from_item(current.show)

            return self.process_item(store[show_key].children, current, create_shows=False)

        key = current.get_key('trakt')

        if not key:
            log.warn('Unable to find "trakt" key in item: %r', current)
            return False

        # Check if item already exists
        if key not in store:
            # Create new entry
            store[key] = Entry.from_item(current)
            return True

        # Try add record to existing group
        record = Record.from_item(current)

        if store[key].add(record, self.delta_max):
            return True

        # Create new group
        store[key].create_group(record)
        return True

    @staticmethod
    def _get_duplicated_items(store):
        result = {}

        for key, entry in store.iteritems():
            if entry.duplicated:
                result[key] = entry

            if entry.children:
                # Update `entry` with duplicated children
                entry.children = dict([
                    (k, e) for k, e in entry.children.items()
                    if e.duplicated
                ])

                # Include if there is at least one duplicated child
                if entry.children:
                    result[key] = entry

        return result
