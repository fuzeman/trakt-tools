from trakt import Trakt
import logging
import random
import time

log = logging.getLogger(__name__)


class HistoryHandler(object):
    def run(self, backup):
        items = []

        page = 1
        page_count = None
        item_count = None

        while (page == 1 and page_count is None) or (page_count is not None and page <= page_count):
            # Request page
            response = Trakt.http.get('/sync/history', query={
                'page': page,
                'limit': 1000
            })

            if response.status_code != 200:
                print 'Invalid response returned, will retry in 5 seconds...'
                time.sleep(5)
                continue

            # Store page items
            received_count = 0

            for item in response.json():
                items.append(item)
                received_count += 1

            # Update page count
            page_count = int(response.headers['X-Pagination-Page-Count'])

            # Update item count
            item_count = int(response.headers['X-Pagination-Item-Count'])

            # Rate-limit requests
            if page < page_count:
                delay = 1 + random.randint(0, 3)

                print '[%02d/%02d] Received %d item(s), waiting %d second(s)...' % (
                    page, page_count,
                    received_count, delay
                )
                time.sleep(delay)
            else:
                print '[%02d/%02d] Received %d item(s)' % (
                    page, page_count,
                    received_count
                )

            # Increment current `page`
            page += 1

        print 'Received %d item(s)' % len(items)

        if len(items) != item_count:
            print 'Entire history wasn\'t retrieved - expected %d item(s), received %d item(s)' % (item_count, len(items))
            return False

        # Write watched history to disk
        try:
            return backup.write('history.json', items)
        except Exception, ex:
            log.error('Unable to write watched history to disk: %s', ex, exc_info=True)

        return False
