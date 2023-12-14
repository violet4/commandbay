import os
import subprocess
import tomllib


def read_version():
    with open('pyproject.toml', 'r') as fr:
        version = tomllib.loads(fr.read())['tool']['poetry']['version']
    return version


def get_git_commit_hash():
    git_commit_hash = subprocess.check_output('git rev-parse --short HEAD', shell=True, text=True).strip()
    return git_commit_hash


def calculate_full_version():
    version = read_version()
    git_commit_hash = get_git_commit_hash()
    full_version_string = f'{version}-{git_commit_hash}'
    return full_version_string


def main():
    full_version_string = calculate_full_version()
    version_py_contents = f'''version = "{full_version_string}"'''

    # version.txt
    with open('version.txt', 'w') as fw:
        print(full_version_string, file=fw, end='')

    # commandbay/version.py
    with open(os.path.join('commandbay', 'version.py'), 'w') as fw:
        print(version_py_contents, file=fw)


if __name__ == '__main__':
    main()
