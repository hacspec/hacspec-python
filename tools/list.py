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

def print_constant(node):
    target = str(node.targets)
    if isinstance(node.targets[0], Name):
        target = node.targets[0].id
    if isinstance(node.targets[0], Tuple):
        elts = node.targets[0].elts
        target = ", ".join([e.id for e in elts])
    value = str(node.value)
    if isinstance(node.value, Name):
        value = node.value.id
    if isinstance(node.value, Call):
        if isinstance(node.value.func, Attribute):
            value = node.value.func.value.id
        if isinstance(node.value.func, Name):
            value = node.value.func.id
    print(target + " := " + value)

if len(argv) != 2:
    print("Usage: list.py <file>")
    exit(1)
filename = argv[1]
with open(filename) as file:
    node = parse(file.read())

functions = [n for n in node.body if isinstance(n, FunctionDef)]
classes = [n for n in node.body if isinstance(n, ClassDef)]
constants = [n for n in node.body if isinstance(n, Assign)]

print(" === Functions ===")
for function in functions:
    print_function(function, "")

print(" === Classes ===")
for class_ in classes:
    print(class_.name + ":")
    methods = [n for n in class_.body if isinstance(n, FunctionDef)]
    for method in methods:
        print_function(method)

print(" === Constants & Aliases ===")
for const in constants:
    print_constant(const)
