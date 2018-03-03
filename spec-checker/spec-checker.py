#!/usr/bin/python3

from typed_ast.ast3 import *
from sys import argv
from sys import exit
import builtins

ALLOWED_IMPORTS = ["speclib", "functools", "test_vectors.", "json", "ctr"]
DEBUG_PRINT = True


def print(*args, **kwargs):
    if DEBUG_PRINT:
        builtins.print(*args, **kwargs)


def isTypeAllowed(node, typeList):
    for aType in typeList:
        if isinstance(node, aType):
            return True
    return False


def read(node, indent="", allowed=None, previous=None):
    print(indent + "processing: " + str(type(node)) + " ...")
    indent += "  "

    # If we have allowed types, check them.
    if not allowed is None and not isTypeAllowed(node, allowed):
        raise SyntaxError("Operation " + str(node) +
                          " is not allowed in " + str(previous) + ".")

    # Read a module.
    if isinstance(node, Module):
        read(node.body, indent + "  ")

    # Check that imports are only from a known list of imports (see ALLOWED_IMPORTS)
    if isinstance(node, ImportFrom):
        print(indent + "ImportFrom: " + node.module)
        for imp in ALLOWED_IMPORTS:
            if node.module.startswith(imp):
                return
        raise ImportError("Use of disallowed import.")
    if isinstance(node, Import):
        print(indent + "Import: " + str(node.names[0].name))
        for node_name in node.names:
            for imp in ALLOWED_IMPORTS:
                if node_name.name.startswith(imp):
                    return
        raise ImportError("Use of disallowed import.")

    # Normal assignments with types in comments
    if isinstance(node, Assign):
        targets = [read(x, indent + "  ") for x in node.targets]
        print(indent + "targets: " + ', '.join(targets))
        value = read(node.value, indent + "  ",
                     [Call, BinOp, Num, Subscript, Name], node)
        print(indent + "value: " + str(value))
        type_comment = node.type_comment
        if type_comment:
            print(indent + "type_comment: " + type_comment)
    if isinstance(node, AugAssign):
        print(indent + "target: " + str(node.target.id))
        value = read(node.value, indent + "  ",
                     [Call, BinOp, Num, Subscript, Name], node)
        print(indent + "value: " + str(value))
        read(node.op, indent + "  ")
    # Assignments with types as annotations
    if isinstance(node, AnnAssign):
        raise SyntaxError("AnnAssign is not allowed yet.")

    if isinstance(node, BinOp):
        left = read(node.left, indent + "  ",
                    [Num, BinOp, Call, Name, Subscript], node)
        op = read(node.op, indent + "  ", [Add, Sub, Mult, Div,
                                           Mod, Pow, LShift, RShift, BitOr, BitXor, BitAnd], node)
        right = read(node.right, indent + "  ",
                     [Num, BinOp, Call, Name, Subscript], node)
        if left is Num and right is Num:
            return Num
        return BinOp

    # Primitive types
    if isinstance(node, Num):
        print(indent + "Num: " + str(node))
        return Num

    if isinstance(node, Name):
        return node.id

    # Operators
    if isinstance(node, Pow):
        print(indent + "Pow: " + str(node))
        return Pow
    if isinstance(node, Sub):
        print(indent + "Sub: " + str(node))
        return Sub

    if isinstance(node, Subscript):
        return read(node.value, indent + "  ")

    # Functions
    if isinstance(node, FunctionDef):
        print(indent + "Func: " + str(node.name))
        # Check allowed arguments.
        if node.args.args is not None:
            args = [x.arg for x in node.args.args]
            print(indent + "  args: " + ', '.join(args))
        if node.args.defaults is not None:
            defaults = [x.s for x in node.args.defaults]
            print(indent + "  defaults: " + ', '.join(defaults))
        if len(node.args.kwonlyargs) != 0:
            raise SyntaxError("keyword only args are not allowed in hacspec")
        if node.args.vararg is not None:
            raise SyntaxError("varargs are not allowed in hacspec")
        if len(node.args.kw_defaults) != 0:
            raise SyntaxError("keyword defaults are not allowed in hacspec")
        if node.args.kwarg is not None:
            raise SyntaxError("keyword args are not allowed in hacspec")

        # Read function body.
        read(node.body, indent + "  ")
    if isinstance(node, Return):
        read(node.value, indent)

    if isinstance(node, Call):
        read(node.func, indent + "  ")
        if node.args:
            read(node.args, indent + "  ")
        return Call

    if isinstance(node, Expr):
        read(node.value, indent + "  ")

    if isinstance(node, If):
        read(node.test, indent + "  ", [Compare], node)
        read(node.body, indent + "  ")
        read(node.orelse, indent + "  ")

    if isinstance(node, While):
        read(node.test, indent + "  ", [Compare], node)
        read(node.body, indent + "  ")
        read(node.orelse, indent + "  ")

    # Disallowed statements
    if isinstance(node, With):
        raise SyntaxError("With is not allowed in hacspec.")
    if isinstance(node, AsyncWith):
        raise SyntaxError("AsyncWith is not allowed in hacspec.")
    if isinstance(node, AsyncFor):
        raise SyntaxError("AsyncFor is not allowed in hacspec.")
    if isinstance(node, ClassDef):
        raise SyntaxError("Classes are not allowed in hacspec.")
    if isinstance(node, AsyncFunctionDef):
        raise TypeError("AsyncFunctionDef is not allowed in hacspec.")
    if isinstance(node, Raise):
        raise TypeError("Raise is not allowed in hacspec.")
    if isinstance(node, Try):
        raise TypeError("Try is not allowed in hacspec.")
    if isinstance(node, Assert):
        raise TypeError("Assert is not allowed in hacspec.")
    if isinstance(node, Delete):
        raise TypeError("Delete is not allowed in hacspec.")
    if isinstance(node, Global):
        raise TypeError("Global is not allowed in hacspec.")
    if isinstance(node, Nonlocal):
        raise TypeError("Global is not allowed in hacspec.")
    if isinstance(node, Break):
        raise TypeError("Break is not allowed in hacspec.")
    if isinstance(node, Continue):
        raise TypeError("Continue is not allowed in hacspec.")

    # Disallowed expressions
    if isinstance(node, ListComp):
        raise SyntaxError("List comprehensions are not allowed in hacspec.")
    if isinstance(node, Lambda):
        raise SyntaxError("Lambdas are not allowed in hacspec.")
    if isinstance(node, UnaryOp):
        raise SyntaxError("Unary operations are not allowed in hacspec.")
    if isinstance(node, IfExp):
        raise SyntaxError("If expressions are not allowed in hacspec.")

    # List of nodes, read all of them.
    if isinstance(node, list):
        for x in node:
            read(x, indent + "  ")


def check_ast(ast):
    if not isinstance(ast, AST):
        raise TypeError('Expected AST, got %r' % node.__class__.__name__)
    read(ast)


def main(filename):
    with open(filename, 'r', encoding='utf-8') as py_file:
        code = py_file.read()
        ast = parse(source=code, filename=filename)
        check_ast(ast)


if __name__ == "__main__":
    if len(argv) != 2:
        print("Usage: spec-checker.py <your-hacpsec.py>")
        exit(1)
    main(argv[1])
