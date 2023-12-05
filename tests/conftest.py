
import subprocess
import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from .factories import UserFactory


def server_has_started(process:subprocess.Popen):
    while True:
        output = b''
        if process.stdout is not None:
            output = process.stdout.readline()
        if b"Ready in" in output:  # Replace with actual readiness message
            break
        time.sleep(0.1)  # Short sleep to avoid tight loop

@pytest.fixture(scope="session", autouse=True)
def start_nextjs_server():
    os.chdir('frontend')
    process = subprocess.Popen(['npm', 'run', 'dev'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    server_has_started(process)
    yield
    process.kill()


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
