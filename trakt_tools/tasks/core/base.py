from trakt import Trakt


class Task(object):
    def __init__(self):
        self._settings = None

    def get_settings(self):
        if self._settings is None:
            # Retrieve account settings
            self._settings = Trakt['users/settings'].get()

        # Return cached settings
        return self._settings

    def get_username(self):
        settings = self.get_settings()

        if not settings:
            return None

        return settings.get('user', {}).get('username')
