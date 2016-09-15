from trakt.objects import Show, Episode, Movie


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
