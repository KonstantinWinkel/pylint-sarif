Author: Konstantin M.J. Winkel, M.Sc.

# pylint_sarif

This projects presents a simple and easy to use python implementation of a converter that creates SARIF files from pylint's json2 format. It was created as a replacement for [this reporisory](https://github.com/GrammaTech/pylint-sarif). 

## Setup
To clone and setup this repository run the following commands.

```bash
git clone https://github.com/KonstantinWinkel/pylint_sarif.git
cd pylint_sarif
git submodule update --init shell_utils
./project_utils.sh setup
```

## Example Usage as CLI tool
The commands below show how to analyze the files in the example directory with pylint, and then create a SARIF file from the results by using this tool as CLI tool.

```bash
pylint -f json2 --output example/output.json example/*.py
python3 -m src.main -i output.json -o output.sarif
```

For further customization, many CLI options are available, see the table below.

| Option | Long Option       | Type | Required | Description |
| ------ | -----------       | ---- | -------- | ----------- |
| -i     | --input           | Path | Yes      | Path to the input json file |
|        | --max-artifacts   | Int  | No       | The maximum number of unique artifacts to process |
|        | --max-input-size  | Int  | No       | The maximum size of the input json file, in megabyte |
|        | --max-messages    | Int  | No       | The maximum number of unique Pylint rules to process |
|        | --max-output-size | Int  | No       | The maximum size of the output sarif file, in megabyte |
|        | --max-rules       | Int  | No       | The maximum number of Pylint messages to process |
| -o     | --output          | Path | Yes      | Path to the output sarif file |
| -v     | --verbose         |      | No       | Increase verbosity (-v, -vv, -vvv) |

## Example Usage as a Python Module
This tool can also be directly integrated into existing python projects as a module. Simply clone it into your project and import it using the following code:

```python
from pylint_sarif import *
```

It supplies a single method `convert` which does the conversion. The arguments of the method are identical to the CLI argmuments.

## Further information
- [The SARIF Standard](https://sarifweb.azurewebsites.net/)
- [Pylint](https://www.pylint.org/)

