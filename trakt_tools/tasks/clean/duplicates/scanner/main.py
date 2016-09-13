from trakt.mapper import SyncMapper
from trakt.objects import Show, Episode, Movie
import gc
import logging
import time

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
            print '[%02d/%02d] Processing items...' % (i, count)

            for item in page:
                # Process item, stop scanning if an error is encountered
                if not self.process(item):
                    log.error('Unable to process item: %r', item)
                    return False

            # Rate limit requests
            print '[%02d/%02d] Waiting 5 seconds...' % (i, count)
            time.sleep(5)

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


class Entry(object):
    __slots__ = (
        'key',
        'title',
        'year',

        'season',
        'number',

        'children',

        'groups',
        'records'
    )

    def __init__(self, key, title, year, season=None, number=None):
        self.key = key
        self.title = title
        self.year = year

        self.season = season
        self.number = number

        self.children = {}

        self.groups = {}
        self.records = []

    @property
    def duplicated(self):
        return len(self.records) > len(self.groups)

    def add(self, current, delta_max):
        for records in self.groups.itervalues():
            matched = False

            for record in records:
                delta = (record.watched_at - current.watched_at).total_seconds()

                if delta < delta_max:
                    matched = True
                    break

            if matched:
                # Add record to group
                records.append(current)

                # Add record to list
                self.records.append(current)
                return True

        return False

    def create_group(self, record):
        if record.watched_at in self.groups:
            raise Exception('Group %r already exists' % record.watched_at)

        # Create record group
        self.groups[record.watched_at] = [record]

        # Add record to list
        self.records.append(record)

    def __repr__(self):
        fragments = []

        # Title + Year
        fragments.append('%r (%r)' % (
            self.title,
            self.year
        ))

        # Season + Episode
        if self.season is not None and self.number is not None:
            fragments.append('S%02dE%02d' % (
                self.season,
                self.number
            ))

        # Children
        if self.children:
            fragments.append('%d children' % (
                len(self.children)
            ))

        # Groups + Records
        if self.groups or self.records:
            fragments.append('%d group(s) / %d record(s)' % (
                len(self.groups),
                len(self.records)
            ))

        return '<Entry %s>' % ' - '.join(fragments)

    @classmethod
    def from_item(cls, item):
        # Construct entry
        if isinstance(item, Episode):
            season, number = item.pk

            entry = cls(
                item.get_key('trakt'),
                item.show.title,
                item.show.year,
                season,
                number
            )
        elif isinstance(item, (Show, Movie)):
            entry = cls(
                item.get_key('trakt'),
                item.title,
                item.year
            )
        else:
            raise ValueError('Unsupported item: %r' % item)

        # Create record group
        if isinstance(item, (Episode, Movie)):
            entry.create_group(Record.from_item(item))

        return entry


class Record(object):
    __slots__ = (
        'id',
        'watched_at'
    )

    def __init__(self, id, watched_at):
        self.id = id
        self.watched_at = watched_at

    def __repr__(self):
        return '<Record id: %r, watched_at: %r>' % (
            self.id,
            self.watched_at
        )

    @classmethod
    def from_item(cls, item):
        if isinstance(item, (Episode, Movie)):
            return cls(
                item.id,
                item.watched_at
            )

        raise ValueError('Unsupported item: %r' % item)
