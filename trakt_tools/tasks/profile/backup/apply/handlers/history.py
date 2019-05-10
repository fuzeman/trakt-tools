import json
import logging
from zipfile import ZipFile

import six
from trakt import Trakt

from trakt_tools.core.input import boolean_input

log = logging.getLogger(__name__)


class HistoryHandler(object):
    def run(self, backup_zip, batch_size=200):
        print('Applying history')

        episodes = []
        movies = []

        with ZipFile(backup_zip, 'r') as zipFile:
            with zipFile.open('history.json', 'r') as fp:
                history = json.load(fp)

        for item in history:
            item_type = item.get('type')
            watched_at = item.get('watched_at')

            if item_type == 'movie':
                ids = item.get('movie').get('ids')
                movies.append({'watched_at': watched_at, 'ids': ids})

            elif item_type == 'episode':
                ids = item.get('episode').get('ids')
                episodes.append({'watched_at': watched_at, 'ids': ids})

            else:
                print('Unable to apply {}: {}'.format(item_type, item))

        # Add the episodes in batches
        print('Adding {} Episodes in batches of {}:'.format(len(episodes), batch_size))
        for x in six.moves.xrange(0, len(episodes), batch_size):
            if not self._add_episodes(episodes[x:x + batch_size]):
                return False

        # Add the movies in batches
        print('Adding {} Movies in batches of {}:'.format(len(movies), batch_size))
        for x in six.moves.xrange(0, len(movies), batch_size):
            if not self._add_movies(movies[x:x + batch_size]):
                return False

        return True

    def _add_episodes(self, episodes):
        response = Trakt['sync/history'].add({'episodes': episodes})

        print(' - Added {} Episodes'.format(response.get("added").get("episodes")))

        failed_episodes = response.get('not_found').get('episodes')
        if len(failed_episodes) > 0:
            print()
            print('Unable to apply Episodes:')
            for episode in failed_episodes:
                print(' - ', episode)

            print()
            if not boolean_input('Would you like to continue anyway?', default=False):
                return False

        return True

    def _add_movies(self, movies):
        response = Trakt['sync/history'].add({'movies': movies})

        print(' - Added {} Movies'.format(response.get("added").get("movies")))

        failed_movies = response.get('not_found').get('movies')
        if len(failed_movies) > 0:
            print()
            print('Unable to apply Movies:')
            for movie in failed_movies:
                print(' - ', movie)

            print()
            if not boolean_input('Would you like to continue anyway?', default=False):
                return False

        return True
