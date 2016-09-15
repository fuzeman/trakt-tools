import logging

log = logging.getLogger(__name__)


class HistoryHandler(object):
    def run(self, backup, profile):
        items = []

        for i, count, page in profile.get_pages('/sync/history'):
            # Append `page` items to list
            items.extend(page)

            print '[history](%02d/%02d) Received %d item(s)' % (
                i, count,
                len(page)
            )

        # Write watched history to disk
        try:
            return backup.write('history.json', items)
        except Exception, ex:
            log.error('Unable to write watched history to disk: %s', ex, exc_info=True)

        return False
