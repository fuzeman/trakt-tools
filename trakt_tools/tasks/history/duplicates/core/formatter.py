from __future__ import print_function

import six


class Formatter(object):
    @classmethod
    def movie(cls, movie, timezone=None):
        title = '"%s" (%r)' % (
            movie.title,
            movie.year
        )

        print('%s - %d plays -> %d plays' % (
            title,
            len(movie.records),
            len(movie.groups)
        ))

        ids = []

        for timestamp_utc, records in movie.groups.items():
            if timezone:
                timestamp = timestamp_utc.astimezone(timezone)
            else:
                timestamp = timestamp_utc

            print('\t%s (%s)' % (
                timestamp.strftime('%b %d, %Y %I:%M %p %Z'),
                timestamp_utc.isoformat()
            ))

            ids.extend([
                record.id for record in records[1:]
            ])

        return title, ids

    @classmethod
    def show(cls, show, timezone=None):
        title = '"%s" (%r)' % (
            show.title,
            show.year
        )

        print('%s' % title)

        return title, Formatter.episodes(show, timezone=timezone)

    @classmethod
    def episodes(cls, show, timezone=None):
        ids = []

        for x, episode in enumerate(six.itervalues(show.children)):
            print('\tS%02dE%02d - %d plays -> %d plays' % (
                episode.season,
                episode.number,
                len(episode.records),
                len(episode.groups)
            ))

            for timestamp_utc, records in episode.groups.items():
                if timezone:
                    timestamp = timestamp_utc.astimezone(timezone)
                else:
                    timestamp = timestamp_utc

                print('\t\t%s (%s)' % (
                    timestamp.strftime('%b %d, %Y %I:%M %p %Z'),
                    timestamp_utc.isoformat()
                ))

                ids.extend([
                    record.id for record in records[1:]
                ])

            if x < len(show.children) - 1:
                print()

        return ids
