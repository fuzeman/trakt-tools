from __future__ import print_function

from trakt_tools.core.input import boolean_input
from trakt_tools.models import Profile
from trakt_tools.tasks.base import Task
from ..core.formatter import Formatter
from .models import Entry, Record

from trakt import Trakt
from trakt.mapper import SyncMapper
from trakt.objects import Episode
import logging
import six

log = logging.getLogger(__name__)


class ScanHistoryDuplicatesTask(Task):
    def __init__(self, delta_max, per_page=1000, debug=False, rate_limit=20):
        super(ScanHistoryDuplicatesTask, self).__init__(
            debug=debug,
            rate_limit=rate_limit
        )

        self.delta_max = delta_max
        self.per_page = per_page

        self.shows = {}
        self.movies = {}

        self._current_shows = {}
        self._current_movies = {}

    def run(self, token):
        log.debug('run()')

        # Process backup download
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
            print('Unable to fetch profile')
            exit(1)

        print('Logged in as %r' % profile.username)
        print()

        if not boolean_input('Would you like to continue?', default=True):
            exit(0)

        print()

        if not self.scan(profile):
            exit(1)

        print()

        if not self.shows and not self.movies:
            print('Unable to find any duplicates')
            exit(0)

        timezone = profile.timezone

        # Display duplicate shows
        for _, show in self.shows.items():
            if not show.children:
                continue

            Formatter.show(show, timezone=timezone)
            print()

        # Display duplicate movies
        for _, movie in self.movies.items():
            Formatter.movie(movie, timezone=timezone)
            print()

        return True

    def scan(self, profile):
        print('Scanning for duplicates...')

        # Process items
        for i, count, page in profile.get_pages('/sync/history'):
            print(' - Processing %d items... (page %d of %d)' % (len(page), i, count))

            for item in page:
                # Process item, stop scanning if an error is encountered
                if not self.process_item(item):
                    print('Unable to process item: %r' % item)
                    return False

        # Find duplicated items
        self.shows = self._get_duplicated_items(self._current_shows)
        self.movies = self._get_duplicated_items(self._current_movies)

        # Destroy item stores
        self._current_shows = None
        self._current_movies = None
        return True

    def process_item(self, data):
        if 'episode' in data:
            return self.map_item(self._current_shows, SyncMapper.episode(None, None, data))

        if 'movie' in data:
            return self.map_item(self._current_movies, SyncMapper.movie(None, None, data))

        log.warn('Unknown item: %r', data)
        return False

    def map_item(self, store, current, create_shows=True):
        # Create show structure
        if create_shows and isinstance(current, Episode):
            show_key = current.show.get_key('trakt')

            if not show_key:
                log.warn('Unable to find "trakt" key in show: %r', current.show)
                return False

            if show_key not in store:
                store[show_key] = Entry.from_item(current.show)

            return self.map_item(store[show_key].children, current, create_shows=False)

        # Retrieve item key
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

        for key, entry in six.iteritems(store):
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
