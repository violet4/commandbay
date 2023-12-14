import subprocess
import os
from os.path import dirname

import tomllib


def get_git_commit_hash():
    git_commit_hash = subprocess.check_output('git rev-parse --short HEAD', shell=True, text=True).strip()
    return git_commit_hash


# grep version pyproject.toml |head -1|cut -d= -f2|tr -d '" '
def get_pyproject_version():
    root_dir = dirname(dirname(os.path.abspath(__file__)))
    pyproject_toml_path = os.path.join(root_dir, 'pyproject.toml')
    with open(pyproject_toml_path, 'r') as fr:
        data = tomllib.loads(fr.read())

    return str(data.get('tool', {}).get('poetry', {}).get('version', ''))


def get_version_version():
    from commandbay.version import version
    return version


try:
    __version__ = get_version_version()
except ImportError:
    try:
        __version__ = f'{get_pyproject_version()}-{get_git_commit_hash()}'
    except:
        __version__ = ''
