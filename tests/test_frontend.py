from selenium import webdriver
from selenium.webdriver.common.by import By

def test_frontend_page(browser:webdriver.Firefox):
    browser.get('http://localhost:7321')
    assert browser.find_element(by=By.CSS_SELECTOR, value='.text-3xl')
