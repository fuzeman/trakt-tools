from __future__ import print_function

import logging

log = logging.getLogger(__name__)


class RatingsHandler(object):
    def run(self, backup, profile):
        print('Ratings')

        # Request ratings
        response = profile.get('/sync/ratings')

        if response.status_code != 200:
            print('Invalid response returned')
            return False

        # Retrieve items
        items = response.json()

        print(' - Received %d item(s)' % len(items))

        # Write ratings to disk
        print(' - Writing to "ratings.json"...')

        try:
            return backup.write('ratings.json', items)
        except Exception as ex:
            log.error('Unable to write ratings to disk: %s', ex, exc_info=True)

        return False
