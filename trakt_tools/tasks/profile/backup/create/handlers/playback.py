import logging

log = logging.getLogger(__name__)


class PlaybackHandler(object):
    def run(self, backup, profile):
        print 'Playback Progress'

        # Request ratings
        response = profile.get('/sync/playback')

        if response.status_code != 200:
            print 'Invalid response returned'
            return False

        # Retrieve items
        items = response.json()

        print ' - Received %d item(s)' % len(items)

        # Write playback progress to disk
        print ' - Writing to "playback.json"...'

        try:
            return backup.write('playback.json', items)
        except Exception, ex:
            log.error('Unable to write playback progress to disk: %s', ex, exc_info=True)

        return False
