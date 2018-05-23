from ast import *
from sys import argv

def print_function(functionNode, indent="    "):
    print(indent + functionNode.name + "(", end="")
    for arg in functionNode.args.args:
        annotation = ":"
        if isinstance(arg.annotation, Name):
            annotation += arg.annotation.id
        elif isinstance(arg.annotation, Str):
            annotation += arg.annotation.s
        elif not arg.annotation:
            annotation = ""
        elif isinstance(arg.annotation, Subscript):
            annotation += arg.annotation.value.id
        print(arg.arg + annotation + " ", end="")
    return_type = ") -> "
    if isinstance(functionNode.returns, NameConstant):
        return_type += str(functionNode.returns.value)
    elif isinstance(functionNode.returns, Name):
        return_type += str(functionNode.returns.id)
    elif isinstance(functionNode.returns, Str):
        return_type += functionNode.returns.s
    print(return_type, end="")
    print("")

if len(argv) != 2:
    print("Usage: list.py <file>")
    exit(1)
filename = argv[1]
with open(filename) as file:
    node = parse(file.read())

functions = [n for n in node.body if isinstance(n, FunctionDef)]
classes = [n for n in node.body if isinstance(n, ClassDef)]

for function in functions:
    print_function(function, "")

for class_ in classes:
    print(class_.name + ":")
    methods = [n for n in class_.body if isinstance(n, FunctionDef)]
    for method in methods:
        print_function(method)
