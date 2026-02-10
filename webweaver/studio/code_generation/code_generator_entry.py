from typing import Type
from .base_code_generator import BaseCodeGenerator
from .base_code_generator_settings import BaseCodeGeneratorSettings


class CodeGeneratorRegistryEntry:
    def __init__(self,
                 generator_cls: Type[BaseCodeGenerator],
                 settings_cls: Type[BaseCodeGeneratorSettings]):
        self.generator_cls = generator_cls
        self.settings_cls = settings_cls

    @property
    def name(self) -> str:
        return self.generator_cls.name
