# Author: Konstantin M.J. Winkel, M.Sc.

"""This file contains the main entry point for the pylint-to-sarif converter."""

import json
import logging
import sys

from src.cli import configure_logging, parse_arguments
from src.pylint_sarif_converter import PylintSarifConverter


def main() -> int:
    """Main Entry Point"""
    try:
        args = parse_arguments()
        configure_logging(args.verbose)
        converter = PylintSarifConverter(args)
        converter.run()
    except (FileExistsError, json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
        logging.getLogger(__name__).error("Conversion failed: %s", exc)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
