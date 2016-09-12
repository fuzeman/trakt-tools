from trakt import Trakt


def authenticate():
    # Request authentication
    print 'Navigate to %s' % Trakt['oauth/pin'].url()
    pin = raw_input('Pin: ')

    # Exchange `code` for `access_token`
    authorization = Trakt['oauth'].token_exchange(pin, 'urn:ietf:wg:oauth:2.0:oob')

    if not authorization or not authorization.get('access_token'):
        return False, None

    print 'Token exchanged - authorization: %r' % authorization
    return True, authorization['access_token']
