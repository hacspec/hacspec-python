#!/usr/bin/python
import sys
import json

# pip install jsonschema
from jsonschema import validate

mac_schema = {
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

enc_schema = {
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "input_len": {
        "type": "number"
      },
      "input": {
        "type": "string"
      },
      "key": {
        "type": "string"
      },
      "nonce": {
        "type": "string"
      },
      "counter": {
        "type": "number"
      },
      "output": {
        "type": "string"
      }
    },
    "required": [
      "input_len",
      "input",
      "key",
      "nonce",
      "counter",
      "output"
    ]
  },
  "maxProperties": 6
}

if len(sys.argv) != 3:
    print("Usage: check_schema.py [mac|enc] <file-name>")
    sys.exit(1)

if sys.argv[1] == "mac":
    with open(sys.argv[2]) as json_data:
        data = json.load(json_data)
        validate(data, mac_schema)
        print("Validation successful")
        sys.exit(0)

if sys.argv[1] == "enc":
    with open(sys.argv[2]) as json_data:
        data = json.load(json_data)
        validate(data, enc_schema)
        print("Validation successful")
        sys.exit(0)


print("Usage: check_schema.py [mac|enc] <file-name>")
sys.exit(1)
