from trakt import Trakt
import logging
import time

log = logging.getLogger(__name__)


class Profile(object):
    def __init__(self, settings):
        self.settings = settings

        self._cache = {}

    @property
    def username(self):
        if not self.settings:
            return None

        return self.settings.get('user', {}).get('username')

    # region Public methods

    # region HTTP

    def clear_cache(self):
        self._cache = None

    def request(self, method, path=None, query=None, data=None):
        if method != 'GET':
            # Ignore caching on non-GET requests
            return Trakt.http.request(
                method,
                path=path,
                query=query,
                data=data
            )

        if data:
            raise NotImplementedError("\"data\" parameter not supported")

        # Build cache key
        cache_key = self._build_cache_key(path, query)

        # Check cache for response
        if cache_key not in self._cache:
            # Fire request, store response in cache
            self._cache[cache_key] = Trakt.http.request(
                method,
                path=path,
                query=query
            )

        # Return response from cache
        return self._cache[cache_key]

    def delete(self, path=None, query=None, data=None):
        return self.request(
            'DELETE',
            path=path,
            query=query,
            data=data
        )

    def get(self, path=None, query=None):
        return self.request(
            'GET',
            path=path,
            query=query
        )

    def post(self, path=None, query=None, data=None):
        return self.request(
            'POST',
            path=path,
            query=query,
            data=data
        )

    def put(self, path=None, query=None, data=None):
        return self.request(
            'PUT',
            path=path,
            query=query,
            data=data
        )

    # endregion

    def get_pages(self, path=None, query=None, per_page=1000):
        page = 1
        page_count = None
        item_count = None

        received_count = 0

        while (page == 1 and page_count is None) or (page_count is not None and page <= page_count):
            page_query = {
                'page': page,
                'limit': per_page
            }

            if query:
                page_query.update(query)

            # Request page
            response = self.get(
                path=path,
                query=page_query
            )

            if response.status_code != 200:
                log.warn('Invalid response returned, will retry in 5 seconds...')
                time.sleep(5)
                continue

            items = response.json()

            # Increment received count
            received_count += len(items)

            # Update page count
            page_count = int(response.headers['X-Pagination-Page-Count'])

            # Update item count
            item_count = int(response.headers['X-Pagination-Item-Count'])

            # Yield page details
            yield page, page_count, items

            # Increment current `page`
            page += 1

        if received_count != item_count:
            raise Exception("Entire history wasn't retrieved (expected %d item(s), received %d item(s)" % (item_count, received_count))

    def __repr__(self):
        return '<Profile %r>' % self.username

    # endregion

    # region Private methods

    @staticmethod
    def _build_cache_key(path, query):
        if query:
            path += '?' + ('&'.join([
                key + '=' + str(value)
                for key, value in query.items()
            ]))

        return path

    # endregion

    # region Class methods

    @classmethod
    def fetch(cls):
        settings = Trakt['users/settings'].get()

        if not settings:
            return None

        return cls(settings)

    # endregion
