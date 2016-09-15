import logging
import os

log = logging.getLogger(__name__)


class CollectionHandler(object):
    def run(self, backup, profile):
        print 'Collection'

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

        if media == 'movies':
            print ' - Received %d movie(s)' % len(items)
        elif media == 'shows':
            print ' - Received %d show(s)' % len(items)
        else:
            print ' - Received %d item(s)' % len(items)

        # Ensure collection directory exists
        collection_dir = os.path.join(backup.path, 'collection')

        if not os.path.exists(collection_dir):
            os.makedirs(collection_dir)

        # Write collected items to disk
        dest_path = os.path.join('collection', '%s.json' % media)

        print ' - Writing to "%s"...' % dest_path

        try:
            return backup.write(dest_path, items)
        except Exception, ex:
            log.error('Unable to write collected items to disk: %s', ex, exc_info=True)

        return False
