import six


def boolean_input(message, default=None):
    while True:
        result = six.moves.input('%s [%s]: ' % (message, 'yes' if default else 'no'))

        # Strip whitespace and convert to lower case
        result = result.strip().lower()

        # Parse result
        if result == '':
            return default

        if result in ['yes', 'y']:
            return True

        if result in ['no', 'n']:
            return False
