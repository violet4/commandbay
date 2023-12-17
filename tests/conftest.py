
import subprocess
import os
import time
import signal

import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from .factories import UserFactory


def server_has_started(process:subprocess.Popen, line:bytes, fail_start:bytes):
    while True:
        if process.stdout is None:
            return
        output = process.stdout.readline()
        if line in output:
            return True
        if fail_start in output:
            process.terminate()
            raise Exception("Process failed to start")
        time.sleep(0.1)  # Short sleep to avoid tight loop


@pytest.fixture(scope="session", autouse=True)
def start_backend_server():
    process = subprocess.Popen(['poetry', 'run', 'python', 'start_server.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    if not server_has_started(process, b'Application startup complete.', b'zzzzzzzzzzz'):
        return
    yield
    process.send_signal(signal.SIGINT)
    process.terminate()


@pytest.fixture(scope="function")
def browser():
    options = Options()

    # docker
    firefox_binary = os.getenv('FIREFOX_BIN')
    if firefox_binary:
        options.add_argument('--headless')

    options.binary = firefox_binary or '/usr/bin/firefox-bin'
    driver = webdriver.Firefox(options=options)
    yield driver
    driver.quit()


@pytest.fixture
def user_factory():
    return UserFactory
