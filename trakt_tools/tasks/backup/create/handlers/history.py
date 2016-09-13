import logging
import random
import time

log = logging.getLogger(__name__)


class HistoryHandler(object):
    def run(self, backup, profile):
        items = []

        for i, count, page in profile.get_pages('/sync/history'):
            # Append `page` items to list
            items.extend(page)

            # Rate-limit requests
            if i < count:
                delay = 1 + random.randint(0, 3)

                print '[%02d/%02d] Received %d item(s), waiting %d second(s)...' % (
                    i, count,
                    len(page),
                    delay
                )
                time.sleep(delay)
            else:
                print '[%02d/%02d] Received %d item(s)' % (
                    i, count,
                    len(page)
                )

        # Write watched history to disk
        try:
            return backup.write('history.json', items)
        except Exception, ex:
            log.error('Unable to write watched history to disk: %s', ex, exc_info=True)

        return False
