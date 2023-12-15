import sys
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


def get_versions():
    from commandbay.version import version, full_version
    return version, full_version


# version is written by scripts/version.py called in `make version` in `make build`
try:
    __version__, full_version = get_versions()
except ImportError:
    try:
        __version__ = get_pyproject_version()
        full_version = f"{__version__}-{get_git_commit_hash()}"
    except:
        __version__ = full_version = ''
