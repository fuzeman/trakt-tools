from __future__ import print_function

from trakt_tools.core.input import boolean_input
from ..core.formatter import Formatter

from trakt import Trakt, ClientError, ServerError
import logging

log = logging.getLogger(__name__)


class Executor(object):
    def __init__(self, review=True):
        self.review = review

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
            self._remove_records(ids)

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
            self._remove_records(ids)

            print()
            print('-' * 70)
            print()

        return True

    def _remove_records(self, record_ids):
        while True:
            # Attempt removal of records
            try:
                response = Trakt['sync/history'].remove(
                    items={
                        'ids': record_ids
                    },
                    exceptions=True
                )
            except (ClientError, ServerError) as ex:
                _, description = ex.error

                print('Unable to remove history record(s): %s' % description)

                # Prompt for retry
                if not boolean_input('Would you like to retry?', default=True):
                    return False

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
