#!/usr/bin/python
import sys
import json

# pip install jsonschema
from jsonschema import validate

poly1305_test_vectors = [
{'input_len': '34',
 'input'    : '43727970746f6772617068696320466f72756d2052657365617263682047726f7570',
 'key'    : '85d6be7857556d337f4452fe42d506a80103808afb0db2fd4abff6af4149f51b',
 'tag'    : 'a8061dc1305136c6c22b8baf0c0127a9'},
{'input_len': '2',
 'input'    : 'f3f6',
 'key'    : '851fc40c3467ac0be05cc20404f3f700580b3b0f9447bb1e69d095b5928b6dbc',
 'tag'    : 'f4c633c3044fc145f84f335cb81953de'},
{'input_len': '0',
 'input'    : '',
 'key'    : 'a0f3080000f46400d0c7e9076c834403dd3fab2251f11ac759f0887129cc2ee7',
 'tag'    : 'dd3fab2251f11ac759f0887129cc2ee7'}
 ]

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
        d = json.load(json_data)
        validate(d, schema)
        print("Validation successful")
        sys.exit(0)

if sys.argv[1] == "enc":
    print("Sorry, enc is not supported yet.")
    sys.exit(1)


print("Usage: check_schema.py [mac|enc] <file-name>")
sys.exit(1)
