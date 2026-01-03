from io import BytesIO
import wx
# Import generated icon byte data
from resources.toolbar.toolbar_inspect import INSPECT_ICON
from resources.toolbar.toolbar_new_project import NEW_PROJECT_ICON
from resources.toolbar.toolbar_open_project import OPEN_PROJECT_ICON
from resources.toolbar.toolbar_close_solution import CLOSE_SOLUTION_ICON
from resources.toolbar.toolbar_pause_record import PAUSE_RECORD_ICON
from resources.toolbar.toolbar_save_project import SAVE_PROJECT_ICON
from resources.toolbar.toolbar_start_record import START_RECORD_ICON
from resources.toolbar.toolbar_stop_record import STOP_RECORD_ICON
from resources.toolbar.toolbar_resume_record import RESUME_RECORD_ICON


def _load_toolbar_icon(png_bytes: bytes) -> wx.Bitmap:
    """
    Load a toolbar icon from PNG bytes and scale it to 32x32.
    """
    stream = BytesIO(png_bytes)
    image = wx.Image(stream)

    # Force 32x32, high quality (matches C++)
    image = image.Scale(32, 32, wx.IMAGE_QUALITY_HIGH)

    return wx.Bitmap(image)


def load_toolbar_inspect_icon() -> wx.Bitmap:
    return _load_toolbar_icon(INSPECT_ICON)


def load_toolbar_new_project_icon() -> wx.Bitmap:
    return _load_toolbar_icon(NEW_PROJECT_ICON)


def load_toolbar_open_project_icon() -> wx.Bitmap:
    return _load_toolbar_icon(OPEN_PROJECT_ICON)


def load_toolbar_pause_record_icon() -> wx.Bitmap:
    return _load_toolbar_icon(PAUSE_RECORD_ICON)


def load_toolbar_save_project_icon() -> wx.Bitmap:
    return _load_toolbar_icon(SAVE_PROJECT_ICON)


def load_toolbar_start_record_icon() -> wx.Bitmap:
    return _load_toolbar_icon(START_RECORD_ICON)


def load_toolbar_stop_record_icon() -> wx.Bitmap:
    return _load_toolbar_icon(STOP_RECORD_ICON)


def load_toolbar_resume_record_icon() -> wx.Bitmap:
    return _load_toolbar_icon(RESUME_RECORD_ICON)


def load_toolbar_close_solution_icon() -> wx.Bitmap:
    return _load_toolbar_icon(CLOSE_SOLUTION_ICON)
