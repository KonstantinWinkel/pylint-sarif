# Author: Konstantin M.J. Winkel

"""This File contains the class definitions for the converter"""

import argparse
import json
import logging
import subprocess
import sys

from copy import deepcopy

from src.paths import SARIF_TEMPLATE_PATH, RULE_TEMPLATE_PATH, ARTEFACT_TEMPLATE_PATH, RESULT_TEMPLATE_PATH
from src.pylint_types import PylintMessage, pylint_confidence_from_string, PYLINT_MESSAGE_KEYS
from src.sarif_types import SarifSeverity, sarif_severity_to_string

logger = logging.getLogger(__name__)

class PylintSarifConverter:
    """This class handles the conversion from pylint json to sarif"""
    def __init__(self):

        # parser setup
        parser = argparse.ArgumentParser()

        parser.add_argument("-v", "--verbose", action="count", default=0,
                            help="Increase verbosity (-v, -vv, -vvv)")
        parser.add_argument("-i", "--input", type=str, required=True,
                            help="Path to the input json file")
        parser.add_argument("-o", "--output", type=str, required=True,
                            help="Path to the output sarif file")

        self.args = parser.parse_args()

        # logging setup
        logging_levels = { 0: logging.WARNING,
                           1: logging.INFO,
                           2: logging.DEBUG
                         }

        logging.basicConfig(level=logging_levels.get(self.args.verbose, logging.DEBUG),
                            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

        # internal variables
        self.json_content = []
        self.sarif_content = {}

    def run(self) -> None:
        """This method runs the whole conversion algorithm"""

        # load pylint json file
        self.load_json_file(self.args.input)

        # load templates
        sarif_template = self.load_template(str(SARIF_TEMPLATE_PATH))
        rule_template = self.load_template(str(RULE_TEMPLATE_PATH))
        result_template = self.load_template(str(RESULT_TEMPLATE_PATH))
        artefact_template = self.load_template(str(ARTEFACT_TEMPLATE_PATH))

        # build parts
        rules = self._get_sarif_rule_definitions(rule_template)
        results = self._get_sarif_result_definitions(result_template)
        artifacts = self._get_sarif_artifact_definitions(artefact_template)

        # build final sarif file

        self._build_sarif_file(sarif_template, rules, results, artifacts)

        # safe sarif file
        self.save_sarif_file(self.args.output)


    def _get_sarif_severity_from_message_id(self, message_id: str) -> SarifSeverity:
        """
        Extracts the severity according to the SARIF standard from the message id provided by
        pylint. Information is found in the first letter of the message id.
        """

        conversion_dict = {
            'F': SarifSeverity.ERROR,   # Failure
            'E': SarifSeverity.ERROR,   # Error
            'W': SarifSeverity.WARNING, # Warning
            'C': SarifSeverity.NOTE,    # Convention
            'R': SarifSeverity.NOTE,    # Refactor
            'I': SarifSeverity.NOTE,    # Informational
            }

        if message_id[0] not in conversion_dict:
            logger.warning("Message ID %s does not start with a known letter, defaulting to Failure", message_id)
            return SarifSeverity.ERROR

        return conversion_dict[message_id[0]]

    def _get_sarif_severity_from_type(self, pylint_type: str) -> SarifSeverity:
        """
        Extracts the severity according to the SARIF standard directly from the type of a pylint
        message.
        """

        conversion_dict = {
                'failure':     SarifSeverity.ERROR,
                'error':       SarifSeverity.ERROR,
                'warning':     SarifSeverity.WARNING,
                'convention':  SarifSeverity.NOTE,
                'refactor':    SarifSeverity.NOTE,
                'information': SarifSeverity.NOTE,
                }

        if pylint_type not in conversion_dict:
            logger.warning("Type %s does not match conversion, defaulting to Failure", pylint_type)
            return SarifSeverity.ERROR

        return conversion_dict[pylint_type]

    def _get_sarif_rule_definitions(self, rule_template: dict) -> list:
        """
        This method builds the rule definitions for the final SARIF file
        by collecting all rules present in the pylint json file
        """

        rules_dict = {}

        for message in self.json_content:
            if message.message_id in rules_dict:
                continue

            template_copy = deepcopy(rule_template)

            template_copy["id"] = message.message_id
            template_copy["name"] = message.symbol
            template_copy["helpUri"] = "https://pylint.readthedocs.io/en/latest/user_guide/messages/" + message.type + "/" + message.symbol
            template_copy["fullDescription"]["text"] = message.message
            template_copy["messageStrings"]["default"]["text"] = message.message + "."
            template_copy["defaultConfiguration"]["level"] = sarif_severity_to_string(self._get_sarif_severity_from_type(message.type))

            rules_dict[message.message_id] = template_copy

        rules = []
        for _, rule in rules_dict.items():
            rules.append(rule)


        return rules

    def _get_sarif_result_definitions(self, result_template: dict) -> list:
        """
        This method builds the result definitions for the final SARIF file
        by collecting all messages present in the pylint json file
        """

        results = []

        for message in self.json_content:

            template_copy = deepcopy(result_template)

            # fill content
            template_copy["ruleId"] = message.message_id
            template_copy["message"]["text"] = message.message
            template_copy["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] = message.absolute_path
            template_copy["locations"][0]["physicalLocation"]["region"]["startLine"] = message.line
            template_copy["locations"][0]["physicalLocation"]["region"]["startColumn"] = message.column
            template_copy["locations"][0]["physicalLocation"]["region"]["endLine"] = message.end_line
            template_copy["locations"][0]["physicalLocation"]["region"]["endColumn"] = message.end_column

            # check if values satisfy lower limits of SARIF

            def _check_and_delete(dictionary: dict, key: str):
                if key not in dictionary:
                    return

                if dictionary[key] is None:
                    del dictionary[key]
                    return

                if dictionary[key] < 1:
                    del dictionary[key]
                    return

            if template_copy["locations"][0]["physicalLocation"]["region"]["startLine"] < 1:
                template_copy["locations"][0]["physicalLocation"]["region"]["startLine"] = 1

            _check_and_delete(template_copy["locations"][0]["physicalLocation"]["region"], "startColumn")
            _check_and_delete(template_copy["locations"][0]["physicalLocation"]["region"], "endLine")
            _check_and_delete(template_copy["locations"][0]["physicalLocation"]["region"], "endColumn")

            results.append(template_copy)

        return results

    def _get_sarif_artifact_definitions(self, artefact_template: dict) -> list:
        """
        This method builds the artefact definitions for the final SARIF file
        """

        artefact_dict = {}

        for message in self.json_content:
            if message.path in artefact_dict:
                continue

            template_copy = deepcopy(artefact_template)

            template_copy["location"]["uri"] = message.path

            artefact_dict[message.path] = template_copy

        artefacts = []

        for _, artefact in artefact_dict.items():
            artefacts.append(artefact)

        return artefacts

    def _get_pylint_version(self) -> str:
        """calls pylint --version and extracts the pylint version"""

        output = subprocess.run(["pylint", "--version"], capture_output=True, check=False)
        lines = output.stdout.splitlines()
        return str(lines[0][7:].decode('utf-8'))

    def _build_sarif_file(self, sarif_template: dict, rules: list, results: list, artifacts: list) -> None:
        """
        This method builds the final sarif file using a given template and
        the results of the previous steps, i.e. list of rules, results and artifacts
        """

        self.sarif_content = deepcopy(sarif_template)

        self.sarif_content["runs"][0]["tool"]["driver"]["version"] = self._get_pylint_version()
        self.sarif_content["runs"][0]["tool"]["driver"]["rules"] = rules
        self.sarif_content["runs"][0]["artifacts"] = artifacts
        self.sarif_content["runs"][0]["results"] = results

    def load_json_file(self, path:str) -> None:
        """This method loads the json content"""

        file_content = None

        with open(path, 'r', encoding='utf-8') as f:
            file_content = json.load(f)

        if file_content is None:
            logging.error("Unable to read JSON file %s", path)
            sys.exit()

        for message in file_content['messages']:

            all_keys_available = True
            for key in PYLINT_MESSAGE_KEYS:
                if key not in message.keys():
                    all_keys_available = False
                    logger.warning("Skipping message with missing key %s: %s", key, message)
                    break

            if all_keys_available is False:
                continue

            pylint_message = PylintMessage(message['type'],
                                           message['symbol'],
                                           message['message'],
                                           message['messageId'],
                                           pylint_confidence_from_string(message['confidence']),
                                           message['module'],
                                           message['obj'],
                                           message['line'],
                                           message['column'],
                                           message['endLine'],
                                           message['endColumn'],
                                           message['path'],
                                           message['absolutePath']
                                           )

            self.json_content.append(pylint_message)

    def load_template(self, path: str) -> dict:
        """This method is used to load the template json files"""

        file_content = None

        with open(path, 'r', encoding='utf-8') as f:
            file_content = json.load(f)

        if file_content is None:
            logging.error("Unable to read JSON file %s", path)
            sys.exit()

        return file_content

    def save_sarif_file(self, path:str) -> None:
        """This method saves the result list as a SARIF file"""

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.sarif_content, f, ensure_ascii=False, indent=4)
