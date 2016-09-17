from __future__ import print_function

from trakt import Trakt
import six


def authenticate():
    # Request authentication
    print('Navigate to %s' % Trakt['oauth/pin'].url())
    pin = six.moves.input('Pin: ')

    # Exchange `code` for `access_token`
    authorization = Trakt['oauth'].token_exchange(pin, 'urn:ietf:wg:oauth:2.0:oob')

    if not authorization or not authorization.get('access_token'):
        return False, None

    return True, authorization['access_token']
