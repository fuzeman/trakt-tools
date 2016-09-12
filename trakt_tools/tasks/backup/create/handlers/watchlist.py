from trakt import Trakt
import logging

log = logging.getLogger(__name__)


class WatchlistHandler(object):
    def run(self, backup):
        # Request ratings
        response = Trakt.http.get('/sync/watchlist')

        if response.status_code != 200:
            print 'Invalid response returned'
            return False

        # Retrieve items
        items = response.json()

        print 'Received %d item(s)' % len(items)

        # Write watchlist to disk
        try:
            return backup.write('watchlist.json', items)
        except Exception, ex:
            log.error('Unable to write watchlist to disk: %s', ex, exc_info=True)

        return False
