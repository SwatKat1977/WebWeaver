from dataclasses import dataclass, field
from browser_launch_options import BrowserLaunchOptions

@dataclass(slots=True)
class ProjectCreateWizardData:
    # -- PAGE 1 [Basic Info] --
    solution_name: str = ""
    solution_directory: str = ""
    create_solution_dir: bool = True

    # -- PAGE 2 [Select Browser] --
    base_url: str = ""
    browser: str = ""
    launch_browser_automatically: bool = True

    # -- PAGE 3 [Behaviour Page] --
    browserLaunchOptions: BrowserLaunchOptions = \
        field(default_factory=BrowserLaunchOptions)
