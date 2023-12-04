from selenium import webdriver

def test_frontend_page(browser:webdriver.Firefox):
    browser.get('http://localhost:3000')  # Assuming Next.js runs on port 3000
    assert browser.find_element(value='asdf')
