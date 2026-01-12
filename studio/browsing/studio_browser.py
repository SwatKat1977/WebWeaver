
class StudioBrowser:
    def __init__(self, driver):
        self._driver = driver

    def open_page(self, url: str):
        self._driver.get(url)

    def quit(self):
        self._driver.quit()

    def screenshot(self, path: str):
        self._driver.save_screenshot(path)

    @property
    def raw(self):
        return self._driver
