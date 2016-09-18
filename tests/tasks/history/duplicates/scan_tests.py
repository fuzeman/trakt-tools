from trakt_tools.tasks import ScanHistoryDuplicatesTask

from datetime import datetime
from dateutil.tz import tzutc


#
# Single duplicates
#


def test_duplicate_single_episode():
    scanner = ScanHistoryDuplicatesTask(
        delta_max=600
    )

    # Process history
    assert scanner.process_item({
        'action': 'scrobble',
        'type': 'episode',

        'id': 1,
        'watched_at': '2014-03-31T09:28:53.000Z',

        'episode': {
            'season': 2,
            'number': 1,
            'title': 'Pawnee Zoo',

            'ids': {
                'trakt': 251,
                'tvdb': 797571,
                'tmdb': 397629
            }
        },

        'show': {
            'title': 'Parks and Recreation',
            'year': 2009,

            'ids': {
                'trakt': 4,
                'slug': 'parks-and-recreation',
                'tvdb': 84912,
                'imdb': 'tt1266020',
                'tmdb': 8592,
                'tvrage': 21686
            }
        }
    }) is True

    assert scanner.process_item({
        'action': 'scrobble',
        'type': 'episode',

        'id': 2,
        'watched_at': '2014-03-31T09:20:53.000Z',

        'episode': {
            'season': 2,
            'number': 1,
            'title': 'Pawnee Zoo',

            'ids': {
                'trakt': 251,
                'tvdb': 797571,
                'tmdb': 397629
            }
        },

        'show': {
            'title': 'Parks and Recreation',
            'year': 2009,

            'ids': {
                'trakt': 4,
                'slug': 'parks-and-recreation',
                'tvdb': 84912,
                'imdb': 'tt1266020',
                'tmdb': 8592,
                'tvrage': 21686
            }
        }
    }) is True

    # Close scanner
    scanner.close()

    # Validate entry
    show = scanner.shows.get('4')
    assert show is not None

    assert show.title == 'Parks and Recreation'
    assert show.year == 2009

    # Validate children
    assert len(show.children) == 1

    episode = show.children.get('251')
    assert episode is not None

    # Validate groups
    assert len(episode.groups) == 1

    assert [
        r.id for r in episode.groups.get(datetime(2014, 3, 31, 9, 28, 53, tzinfo=tzutc()), [])
    ] == [
        1,
        2
    ]

    # Validate records
    assert sorted(episode.records.keys()) == [
        1,
        2
    ]


def test_duplicate_single_movie():
    scanner = ScanHistoryDuplicatesTask(
        delta_max=600
    )

    # Process history
    assert scanner.process_item({
        'action': 'scrobble',
        'type': 'movie',

        'id': 1,
        'watched_at': '2014-03-31T09:28:53.000Z',

        'movie': {
            'title': 'The Dark Knight',
            'year': 2008,

            'ids': {
                'trakt': 4,
                'slug': 'the-dark-knight-2008',
                'imdb': 'tt0468569',
                'tmdb': 155
            }
        }
    }) is True

    assert scanner.process_item({
        'action': 'scrobble',
        'type': 'movie',

        'id': 2,
        'watched_at': '2014-03-31T09:20:53.000Z',

        'movie': {
            'title': 'The Dark Knight',
            'year': 2008,

            'ids': {
                'trakt': 4,
                'slug': 'the-dark-knight-2008',
                'imdb': 'tt0468569',
                'tmdb': 155
            }
        }
    }) is True

    # Close scanner
    scanner.close()

    # Validate entry
    movie = scanner.movies.get('4')
    assert movie is not None

    assert movie.title == 'The Dark Knight'
    assert movie.year == 2008

    # Validate groups
    assert len(movie.groups) == 1

    assert [
        r.id for r in movie.groups.get(datetime(2014, 3, 31, 9, 28, 53, tzinfo=tzutc()), [])
    ] == [
        1,
        2
    ]

    # Validate records
    assert sorted(movie.records.keys()) == [
        1,
        2
    ]


#
# Unique
#


def test_unique_episode():
    scanner = ScanHistoryDuplicatesTask(
        delta_max=600
    )

    # Process history
    assert scanner.process_item({
        'action': 'scrobble',
        'type': 'episode',

        'id': 1,
        'watched_at': '2014-03-31T09:28:53.000Z',

        'episode': {
            'season': 2,
            'number': 1,
            'title': 'Pawnee Zoo',

            'ids': {
                'trakt': 251,
                'tvdb': 797571,
                'tmdb': 397629
            }
        },

        'show': {
            'title': 'Parks and Recreation',
            'year': 2009,

            'ids': {
                'trakt': 4,
                'slug': 'parks-and-recreation',
                'tvdb': 84912,
                'imdb': 'tt1266020',
                'tmdb': 8592,
                'tvrage': 21686
            }
        }
    }) is True

    assert scanner.process_item({
        'action': 'scrobble',
        'type': 'episode',

        'id': 2,
        'watched_at': '2014-03-30T09:28:53.000Z',

        'episode': {
            'season': 2,
            'number': 1,
            'title': 'Pawnee Zoo',

            'ids': {
                'trakt': 251,
                'tvdb': 797571,
                'tmdb': 397629
            }
        },

        'show': {
            'title': 'Parks and Recreation',
            'year': 2009,

            'ids': {
                'trakt': 4,
                'slug': 'parks-and-recreation',
                'tvdb': 84912,
                'imdb': 'tt1266020',
                'tmdb': 8592,
                'tvrage': 21686
            }
        }
    }) is True

    # Close scanner
    scanner.close()

    # Validate entry
    assert scanner.shows.get('4') is None


def test_unique_movie():
    scanner = ScanHistoryDuplicatesTask(
        delta_max=600
    )

    # Process history
    assert scanner.process_item({
        'action': 'scrobble',
        'type': 'movie',

        'id': 1,
        'watched_at': '2014-03-30T09:28:53.000Z',

        'movie': {
            'title': 'The Dark Knight',
            'year': 2008,

            'ids': {
                'trakt': 4,
                'slug': 'the-dark-knight-2008',
                'imdb': 'tt0468569',
                'tmdb': 155
            }
        }
    }) is True

    assert scanner.process_item({
        'action': 'scrobble',
        'type': 'movie',

        'id': 2,
        'watched_at': '2014-03-31T09:28:53.000Z',

        'movie': {
            'title': 'The Dark Knight',
            'year': 2008,

            'ids': {
                'trakt': 4,
                'slug': 'the-dark-knight-2008',
                'imdb': 'tt0468569',
                'tmdb': 155
            }
        }
    }) is True

    # Close scanner
    scanner.close()

    # Validate entry
    assert scanner.movies.get('4') is None


#
# Record duplication
#


def test_record_duplication():
    scanner = ScanHistoryDuplicatesTask(
        delta_max=600
    )

    # Process history
    assert scanner.process_item({
        'action': 'scrobble',
        'type': 'movie',

        'id': 1,
        'watched_at': '2014-03-31T09:28:53.000Z',

        'movie': {
            'title': 'The Dark Knight',
            'year': 2008,

            'ids': {
                'trakt': 4,
                'slug': 'the-dark-knight-2008',
                'imdb': 'tt0468569',
                'tmdb': 155
            }
        }
    }) is True

    assert scanner.process_item({
        'action': 'scrobble',
        'type': 'movie',

        'id': 1,
        'watched_at': '2014-03-31T09:20:53.000Z',

        'movie': {
            'title': 'The Dark Knight',
            'year': 2008,

            'ids': {
                'trakt': 4,
                'slug': 'the-dark-knight-2008',
                'imdb': 'tt0468569',
                'tmdb': 155
            }
        }
    }) is True

    # Close scanner
    scanner.close()

    # Validate entry
    assert scanner.movies.get('4') is None
