from __future__ import print_function

from trakt_tools.core.input import boolean_input

from requests import RequestException
from trakt import Trakt
import logging
import pytz
import time

log = logging.getLogger(__name__)


class Profile(object):
    def __init__(self, settings, per_page=None, rate_limit=None):
        self.settings = settings

        self.per_page = per_page
        self.rate_limit = rate_limit

        self._cache = {}
        self._last_request_at = None

    @property
    def username(self):
        if not self.settings:
            return None

        return self.settings.get('user', {}).get('username')

    @property
    def timezone(self):
        name = self.timezone_name

        if not name:
            return None

        try:
            return pytz.timezone(name)
        except Exception:
            log.warn('Unknown account timezone %r, timestamps will be displayed in the GMT/UTC timezone instead', name)
            return None

    @property
    def timezone_name(self):
        if not self.settings:
            return None

        return self.settings.get('account', {}).get('timezone')

    # region Public methods

    # region HTTP

    def clear_cache(self):
        self._cache = None

    def request(self, method, path=None, query=None, data=None):
        # Ignore caching on non-GET requests
        if method != 'GET':
            self._rate_limit()

            # Fire request
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
            self._rate_limit()

            # Send request
            response = Trakt.http.request(
                method,
                path=path,
                query=query
            )

            # Store response is cache (if successful)
            if response.status_code == 200:
                self._cache[cache_key] = response

            return response

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

    def get_pages(self, path=None, query=None):
        page = 1
        page_count = None
        item_count = None

        received_count = 0
        retry_count = 0

        while (page == 1 and page_count is None) or (page_count is not None and page <= page_count):
            page_query = {
                'page': page,
                'limit': self.per_page
            }

            if query:
                page_query.update(query)

            # Request page
            try:
                response = self.get(
                    path=path,
                    query=page_query
                )
            except RequestException as ex:
                self._retry_request(
                    retry_count,
                    prompt=retry_count >= 3,
                    message='Unable to fetch page #%d' % page,
                    reason='exception: %s' % ex.message
                )
                retry_count += 1
                continue

            if response.status_code != 200:
                self._retry_request(
                    retry_count,
                    prompt=retry_count >= 3,
                    message='Unable to fetch page #%d' % page,
                    reason='status: %s' % response.status_code
                )
                retry_count += 1
                continue

            # Valid response returned
            items = response.json()

            # Reset state
            retry_count = 0

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
            raise Exception("Entire history wasn't retrieved (expected %d item(s), received %d item(s)" % (
                item_count,
                received_count
            ))

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

    def _rate_limit(self):
        # Rate-limit requests
        if self.rate_limit is not None and self._last_request_at is not None:
            delay = (60 / self.rate_limit) - (time.time() - self._last_request_at)

            if delay > 0:
                time.sleep(delay)

        self._last_request_at = time.time()

    @staticmethod
    def _retry_request(retry_count, prompt=True, message='Request failed', reason=None):
        # Ask if a retry should be attempted
        if prompt:
            print('%s (%s)' % (
                message,
                reason
            ))

            if boolean_input('Request has failed %d times, retry request?' % retry_count, default=True):
                # Retry request again
                return

            # User cancelled the request
            if reason:
                raise Exception('%s (attempted %d times), %s' % (
                    message,
                    retry_count,
                    reason
                ))

            raise Exception('%s (attempted %d times)' % (
                message,
                retry_count
            ))

        # Retry request
        print('%s, retrying in 5 seconds... (%s)' % (
            message,
            reason
        ))
        time.sleep(5)

    # endregion

    # region Class methods

    @classmethod
    def fetch(cls, per_page, rate_limit):
        settings = Trakt['users/settings'].get()

        if not settings:
            return None

        return cls(
            settings,
            per_page=per_page,
            rate_limit=rate_limit
        )

    # endregion
