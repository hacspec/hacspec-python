#!/usr/bin/python
import sys
import json

# pip install jsonschema
from jsonschema import validate

schema = {
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "input_len": {
        "type": "string"
      },
      "input": {
        "type": "string"
      },
      "key": {
        "type": "string"
      },
      "tag": {
        "type": "string"
      }
    },
    "required": [
      "input_len",
      "input",
      "key",
      "tag"
    ],
    "maxProperties": 4
  }
}

if len(sys.argv) != 3:
    print("Usage: check_schema.py [mac|enc] <file-name>")
    sys.exit(1)

if sys.argv[1] == "mac":
    with open(sys.argv[2]) as json_data:
        data = json.load(json_data)
        validate(data, schema)
        print("Validation successful")
        sys.exit(0)

if sys.argv[1] == "enc":
    print("Sorry, enc is not supported yet.")
    sys.exit(1)


print("Usage: check_schema.py [mac|enc] <file-name>")
sys.exit(1)
