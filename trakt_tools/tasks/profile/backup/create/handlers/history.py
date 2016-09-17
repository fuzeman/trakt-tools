from __future__ import print_function

import logging

log = logging.getLogger(__name__)


class HistoryHandler(object):
    def run(self, backup, profile):
        print('History')

        items = []

        for i, count, page in profile.get_pages('/sync/history'):
            # Append `page` items to list
            items.extend(page)

            print(' - Received %d item(s) (page %d of %d)' % (
                len(page),
                i, count
            ))

        # Write watched history to disk
        print(' - Writing to "history.json"...')

        try:
            return backup.write('history.json', items)
        except Exception as ex:
            log.error('Unable to write watched history to disk: %s', ex, exc_info=True)

        return False
