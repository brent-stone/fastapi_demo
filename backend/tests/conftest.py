"""
Shared Pytest fixtures and helper functions

NOTE: Typing Generators follow the pattern Generator[YieldType, SendType, ReturnType]
Generator[str, None, None] is equivalent to Iterator[str] but more precise for the
yield based pytest fixtures below. Iterator[str] was used for clarity and simplicity.
https://docs.python.org/3/library/typing.html#typing.Generator
"""
from logging import getLogger

from demo.core.config import core_config
from demo.core.config import CoreConfig


logger = getLogger(__name__)

testing_config: CoreConfig = core_config
