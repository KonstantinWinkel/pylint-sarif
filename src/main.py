# Author: Konstantin M.J. Winkel, M.Sc.

"""This file contains the main entry point for the pylint-to-sarif converter."""

from src.pylint_sarif_converter import PylintSarifConverter

def main():
    """Main Entry Point"""
    converter = PylintSarifConverter()

    converter.run()

if __name__ == "__main__":
    main()
