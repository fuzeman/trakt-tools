from argparse import ArgumentParser
from subprocess import Popen
import os


DEPENDENCIES = [
    ('develop', [
        '-rrequirements_develop.txt',
        '-rtests/requirements.txt'
    ]),
    ('pip', [
        '-rrequirements.txt',
        '-rtests/requirements.txt'
    ]),
    ('travis', [
        '-rrequirements_vendor.txt',
        '-rtests/requirements.txt',

        '--editable=git+https://github.com/fuzeman/trakt.py.git@{BRANCH}#egg=trakt-py'
    ]),
    ('flake8', [
        'flake8'
    ]),
    ('py32', [
        'coverage==3.7.1',
        'pytest>=2.7.0, < 3.0.0',
        'requests>=2.4.0, < 2.11.0'
    ]),
]


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('env')

    args = parser.parse_args()

    # Retrieve branch
    branch = os.environ.get('CURRENT_BRANCH') or 'master'

    # Install environment dependencies
    env_parts = args.env.split('-')

    for key, dependencies in DEPENDENCIES:
        if key not in env_parts:
            continue

        for dep in dependencies:
            dep = dep.replace('{BRANCH}', branch)

            # Install dependency
            print('Installing dependency: %r' % (dep,))
            process = Popen(['pip', 'install', '--upgrade', dep])
            process.wait()
