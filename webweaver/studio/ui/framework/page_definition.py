import dataclasses
import typing
from webweaver.studio.ui.framework.settings_page import SettingsPage


@dataclasses.dataclass
class PageDefinition:
    label: str
    page_class: typing.Type[SettingsPage]
    icon: typing.Optional[str] = None               # Future
    path: typing.Optional[list[str]] = None         # Future
