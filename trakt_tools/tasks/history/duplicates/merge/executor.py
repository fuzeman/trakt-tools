from __future__ import print_function

from trakt_tools.core.input import boolean_input
from ..core.formatter import Formatter

from requests import RequestException
from trakt import Trakt, ClientError, ServerError
import logging
import six

log = logging.getLogger(__name__)


class Executor(object):
    def __init__(self, review=True, batch_size=200):
        self.review = review
        self.batch_size = batch_size

    def process_shows(self, profile, shows):
        log.debug('Executing actions on %d shows...', len(shows))

        timezone = profile.timezone

        for _, show in shows.items():
            if not show.children:
                continue

            title, ids = Formatter.show(show, timezone=timezone)
            print()

            # Review actions
            if self.review and not boolean_input(
                'Remove %d duplicate history record(s) for %s?' % (len(ids), title),
                default=True
            ):
                print('Skipped')
                continue

            # Remove history records
            for x in six.moves.xrange(0, len(ids), self.batch_size):
                profile._rate_limit()
                self._remove_records(ids[x:x + self.batch_size])

            print()
            print('-' * 70)
            print()

        return True

    def process_movies(self, profile, movies):
        log.debug('Executing actions on %d movies...', len(movies))

        timezone = profile.timezone

        for _, movie in movies.items():
            title, ids = Formatter.movie(movie, timezone=timezone)
            print()

            # Review actions
            if self.review and not boolean_input(
                'Remove %d duplicate history record(s) for %s?' % (len(ids), title),
                default=True
            ):
                print('Skipped')
                continue

            # Remove history records
            for x in six.moves.xrange(0, len(ids), self.batch_size):
                profile._rate_limit()
                self._remove_records(ids[x:x + self.batch_size])

            print()
            print('-' * 70)
            print()

        return True

    @staticmethod
    def _remove_records(ids):
        while True:
            # Attempt removal of records
            try:
                response = Trakt['sync/history'].remove(
                    items={
                        'ids': ids
                    },
                    exceptions=True
                )
            except (ClientError, ServerError, RequestException) as ex:
                # Retrieve error message
                message = str(ex)

                if isinstance(ex, (ClientError, ServerError)):
                    _, message = ex.error
                elif hasattr(ex, 'message'):
                    message = ex.message

                # Prompt for request retry
                print('Unable to remove %d history record(s): %s' % (len(ids), message))

                if not boolean_input('Would you like to retry the request?', default=True):
                    # Cancel request
                    return False

                # Retry request
                print()
                continue

            # Display results
            deleted_episodes = response.get('deleted', {}).get('episodes', 0)
            deleted_movies = response.get('deleted', {}).get('movies', 0)

            if deleted_episodes and deleted_movies:
                print('Removed %d episode record(s) and %d movie record(s) from history' % (
                    deleted_episodes,
                    deleted_movies
                ))
            elif deleted_episodes:
                print('Removed %d episode record(s) from history' % (
                    deleted_episodes
                ))
            elif deleted_movies:
                print('Removed %d movie record(s) from history' % (
                    deleted_movies
                ))

            for record_id in response.get('not_found', {}).get('ids', []):
                print('Unable to find record with id: %r' % record_id)

            return True
