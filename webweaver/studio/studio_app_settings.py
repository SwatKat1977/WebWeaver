
from dataclasses import dataclass
from pathlib import Path

@dataclass
class StudioAppSettings:
    plugins_path: Path
    restore_last_solution: bool = True
