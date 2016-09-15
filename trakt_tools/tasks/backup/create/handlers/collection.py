import logging
import os

log = logging.getLogger(__name__)


class CollectionHandler(object):
    def run(self, backup, profile):
        return (
            self.run_media(backup, profile, 'movies') and
            self.run_media(backup, profile, 'shows')
        )

    def run_media(self, backup, profile, media):
        # Request ratings
        response = profile.get('/sync/collection/%s?extended=metadata' % media)

        if response.status_code != 200:
            print 'Invalid response returned'
            return False

        # Retrieve items
        items = response.json()

        print '[collection/%s] Received %d item(s)' % (media, len(items))

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
