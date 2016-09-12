from trakt import Trakt
import logging

log = logging.getLogger(__name__)


class PlaybackHandler(object):
    def run(self, backup):
        # Request ratings
        response = Trakt.http.get('/sync/playback')

        if response.status_code != 200:
            print 'Invalid response returned'
            return False

        # Retrieve items
        items = response.json()

        print 'Received %d item(s)' % len(items)

        # Write playback progress to disk
        try:
            return backup.write('playback.json', items)
        except Exception, ex:
            log.error('Unable to write playback progress to disk: %s', ex, exc_info=True)

        return False
