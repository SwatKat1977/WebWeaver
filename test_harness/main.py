"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

    This program is free software : you can redistribute it and /or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.If not, see < https://www.gnu.org/licenses/>.
"""
import logging
import time
from browser_type import BrowserType
from web_driver import WebDriver
from web_driver_option import WebDriverOption
from web_driver_option_parameters import WebDriverOptionParameters
from button_control import ButtonControl
from tickbox_control import TickboxControl
from textbox_control import TextboxControl
from dropdown_control import DropdownControl
from multiselect_dropdown_control import MultiSelectDropdownControl
from radio_button_control import RadioButtonControl

LOGGING_DATETIME_FORMAT_STRING = "%Y-%m-%d %H:%M:%S"
LOGGING_DEFAULT_LOG_LEVEL = logging.DEBUG
LOGGING_LOG_FORMAT_STRING = "%(asctime)s [%(levelname)s] %(message)s"

# pylint: disable=too-many-locals, too-many-statements

def main_full(test_textbox: bool = False,
              test_multiselect: bool = False,
              test_tickbox: bool = False,
              test_dropdown: bool = False,
              test_button: bool = False):
    """ Full test """

    logger = logging.getLogger(__name__)
    log_format = logging.Formatter(LOGGING_LOG_FORMAT_STRING,
                                   LOGGING_DATETIME_FORMAT_STRING)
    console_stream = logging.StreamHandler()
    console_stream.setFormatter(log_format)
    logger.setLevel(LOGGING_DEFAULT_LOG_LEVEL)
    logger.addHandler(console_stream)

    params = [(WebDriverOption.DISABLE_GPU,), # (WebDriverOption.MAXIMISED,),
              (WebDriverOption.REMOTE_DEBUGGING_PORT, "5553"),
              (WebDriverOption.DISABLE_POPUP_BLOCKING,),
              (WebDriverOption.DISABLE_NOTIFICATIONS,),
              (WebDriverOption.LOG_LEVEL, "3")]

    wb = WebDriver(BrowserType.CHROME, parameters=params,
                   screenshots_enabled=True)
    print(f"WD is {wb.driver}")

    if test_textbox:
        wb.open_page("https://www.saucedemo.com/")

        username = TextboxControl(wb, logger)
        username.find_element_by_xpath("//input[@id='user-name']")
        username.set_value("trial_user")
        time.sleep(10)
        print("username: ", username.get_value())
        username.clear()
        time.sleep(10)

    if test_tickbox:
        wb.open_page("https://webdriveruniversity.com/Dropdown-Checkboxes-RadioButtons/index.html")

        time.sleep(5)

        tick = TickboxControl(wb, logger)
        tick.find_element_by_xpath("//div[@class='section-title']//label[1]//input")

        print("Is ticked:", tick.is_toggled())
        tick.toggle()
        time.sleep(5)

        print("Is ticked:", tick.is_toggled())

        time.sleep(5)

    if test_dropdown:
        wb.open_page("https://webdriveruniversity.com/Dropdown-Checkboxes-RadioButtons/index.html")

        drop: str = "//select[@id='dropdowm-menu-1']"
        drop_ctrl = DropdownControl(wb, logger)
        drop_ctrl.find_element_by_xpath(drop)

        drop_ctrl.select_by_text("SQL")
        print("Options", drop_ctrl.get_all_options())

        time.sleep(10)

    if test_multiselect:
        logger.info("Testing Multiselect dropdown...")
        multi: str = "//select[@id='cars']"

        wb.open_page("https://demoqa.com/select-menu?utm_source=chatgpt.com")

        time.sleep(6)

        ms = MultiSelectDropdownControl(wb, logger)
        ms.find_element_by_xpath(multi)
        print("ALL Multi options: ", ms.get_all_options())

        wb.take_screenshot()

        time.sleep(5)
        ms.select_by_value("volvo")
        ms.select_by_value("audi")

        time.sleep(10)

        ms.deselect_by_text("Volvo")
        time.sleep(10)

    if test_button:
        button_page: str = "https://webdriveruniversity.com/Click-Buttons/index.html"
        wb.open_page(button_page)

        button = ButtonControl(wb, logger)
        button.find_element_by_xpath("//span[@id='button1']")
        button.click()

        time.sleep(10)

    radio_test_page = "https://webdriveruniversity.com/Dropdown-Checkboxes-RadioButtons/index.html"
    radio_button_xpath = "//input[@name= 'color' and @value='orange']"
    wb.open_page(radio_test_page)
    radio_button = RadioButtonControl(wb, logger)
    radio_button.find_element_by_xpath(radio_button_xpath)

    print(f"Radio button selected (should be no): {radio_button.is_selected()}")
    radio_button.select()
    print(f"Radio button selected (should be yes): {radio_button.is_selected()}")

    time.sleep(10)


def options_test():
    """ Test driver options """
    print(WebDriverOptionParameters)

    print(WebDriverOptionParameters[WebDriverOption.HEADLESS].is_valid_for(BrowserType.EDGE))
    print(WebDriverOptionParameters[WebDriverOption.HEADLESS].is_valid_for(BrowserType.FIREFOX))


options: bool = False # True
full: bool = True # False
# options: bool = False
# full: bool = False

if options:
    options_test()

if full:
    main_full(test_dropdown=True, test_multiselect=True)
