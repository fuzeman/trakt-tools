from datetime import datetime
import json
import os


class Backup(object):
    def __init__(self, name, path, username=None, timestamp=None):
        self.name = name
        self.path = path

        self.username = username
        self.timestamp = timestamp

    #
    # Public methods
    #

    def write(self, path, data):
        path = os.path.join(self.path, path)

        if os.path.exists(path):
            return False

        with open(path, 'w') as fp:
            json.dump(data, fp, indent=4, sort_keys=True)

        return True

    #
    # Static methods
    #

    @classmethod
    def create(cls, backup_dir, username, timestamp=None):
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Build name
        name = timestamp.strftime("%Y-%m-%d_%H-%M")

        # Build path
        path = os.path.join(
            backup_dir,
            username,
            name
        )

        # Ensure directory exists
        os.makedirs(path)

        # Construct backup
        return cls(
            name=name,
            path=path,

            username=username,
            timestamp=timestamp
        )
