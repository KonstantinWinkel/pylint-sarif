Author: Konstantin M.J. Winkel, M.Sc.

# pylint-sarif

This projects presents a simple and easy to use python implementation of a converter that creates SARIF files from pylint's json2 format. It was created as a replacement for [this reporisory](https://github.com/GrammaTech/pylint-sarif). 

## Example Usage
The commands below show how to analyze the files in the example directory with pylint, and then create a SARIF file from the results.

```bash
pylint -f json2 --output output.json example/*.py
python3 -m src.main -i output.json -o output.sarif
```

## Further information
- [The SARIF Standard](https://sarifweb.azurewebsites.net/)
- [Pylint](https://www.pylint.org/)

