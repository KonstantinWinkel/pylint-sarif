# Author: Konstantin M.J. Winkel, M.Sc.

"""Public API for the Pylint JSON2 to SARIF converter."""

from os import PathLike, fspath
from types import SimpleNamespace
from typing import Union

from .cli import (
    DEFAULT_MAX_ARTIFACTS,
    DEFAULT_MAX_INPUT_SIZE_MIB,
    DEFAULT_MAX_MESSAGES,
    DEFAULT_MAX_OUTPUT_SIZE_MIB,
    DEFAULT_MAX_RULES,
)
from .pylint_sarif_converter import PylintSarifConverter

PathValue = Union[str, PathLike]

def convert(
        input_path: PathValue,
        output_path: PathValue,
        *,
        max_input_size_mib: int = DEFAULT_MAX_INPUT_SIZE_MIB,
        max_output_size_mib: int = DEFAULT_MAX_OUTPUT_SIZE_MIB,
        max_messages: int = DEFAULT_MAX_MESSAGES,
        max_rules: int = DEFAULT_MAX_RULES,
        max_artifacts: int = DEFAULT_MAX_ARTIFACTS) -> None:
    """Convert a Pylint JSON2 report to a SARIF file.

    The output path must not already exist. Conversion and validation errors are
    raised to the caller so an embedding application can handle them directly.
    """

    limits = {
        "max_input_size_mib": max_input_size_mib,
        "max_output_size_mib": max_output_size_mib,
        "max_messages": max_messages,
        "max_rules": max_rules,
        "max_artifacts": max_artifacts,
    }
    for name, value in limits.items():
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")

    args = SimpleNamespace(
        input=fspath(input_path),
        output=fspath(output_path),
        max_input_size=max_input_size_mib,
        max_output_size=max_output_size_mib,
        max_messages=max_messages,
        max_rules=max_rules,
        max_artifacts=max_artifacts,
    )
    PylintSarifConverter(args).run()


__all__ = ["convert", "PylintSarifConverter"]

