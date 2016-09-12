from trakt import Trakt
import logging
import os

log = logging.getLogger(__name__)


class CollectionHandler(object):
    def run(self, backup):
        return (
            self.run_media(backup, 'movies') and
            self.run_media(backup, 'shows')
        )

    def run_media(self, backup, media):
        # Request ratings
        response = Trakt.http.get('/sync/collection/%s?extended=metadata' % media)

        if response.status_code != 200:
            print 'Invalid response returned'
            return False

        # Retrieve items
        items = response.json()

        print 'Received %d item(s)' % len(items)

        # Ensure collection directory exists
        collection_dir = os.path.join(backup.path, 'collection')

        if not os.path.exists(collection_dir):
            os.makedirs(collection_dir)

        # Write collected items to disk
        try:
            return backup.write(os.path.join('collection', '%s.json' % media), items)
        except Exception, ex:
            log.error('Unable to write collected items to disk: %s', ex, exc_info=True)

        return False
