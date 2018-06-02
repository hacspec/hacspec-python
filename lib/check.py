#!/usr/bin/env python3

from typed_ast.ast3 import *
from sys import argv
from os import environ
import os

file_dir = None

def read_function_signature(f):
    fun_name = f.name
    rt = -1
    arg_names = []
    arg_types = []
    if f.args.args is not None:
        for x in f.args.args:
            if x.annotation and x is Name:
                arg_types.append(x.annotation.id)
            elif x.annotation and isinstance(x.annotation, Name):
                arg_types.append(x.annotation.id)
            elif x.annotation and isinstance(x.annotation, Str):
                arg_types.append(x.annotation.s)
            elif x.annotation and isinstance(x.annotation, Call):
                arg_types.append(x.annotation.func.id)
            arg_names.append(x.arg)
    if f.returns is not None:
        if isinstance(f.returns, Name):
            rt = f.returns.id
        elif isinstance(f.returns, Subscript):
            tmp = f.returns.slice.value
            rt = f.returns.value.id
            if isinstance(tmp, Name):
                rt += "["+tmp.id+"]"
            elif isinstance(tmp, list):
                tmp2 = []
                for x in tmp:
                    tmp2.append(x.elts)
                rt +=str(tmp2)
            elif isinstance(tmp, Tuple):
                tmp2 = [] 
                for x in tmp.elts:
                    if isinstance(x, Name):
                        tmp2.append(x.id)
                    elif isinstance(x, NameConstant):
                        tmp2.append(x.value)
                    else:
                        print("\n *** Couldn't parse function return values: \"" + fun_name+"\"")
                        exit(1)
                rt += str(tmp2)
            else:
                rt += str(tmp)
        elif isinstance(f.returns, NameConstant):
            rt = f.returns.value
        elif isinstance(f.returns, Call):
            rt = f.returns.func.id
    decorators = []
    for d in f.decorator_list:
        if isinstance(d, Name):
            decorators.append(d.id)
        elif isinstance(d, Call):
            decorators.append(d.func.id)
        else:
            print("\n *** Function decorators must be names or calls not " + str(d))
            exit(1)
    # Every function must have a typechecked decorator.
    typechecked = False
    for decorator in decorators:
        if decorator == "typechecked":
            typechecked = True
            break
    if not typechecked:
        print("\n *** Every hacpsec function must have a @typechecked decorator: \"" + fun_name+"\"")
        exit(1)
    try:
        arg_names.remove("self")
    except:
        pass
    # Every argument must be typed.
    if len(arg_types) != len(arg_names):
        print("\n *** Every hacpsec function argument must be typed: \"" + fun_name+"\"")
        exit(1)
    # Check arg_types.
    for arg_type in arg_types:
        if not is_valid_type(arg_type):
            print("\n *** Invalid argument type in function signature " + fun_name + " - " + str(arg_type))
            exit(1)
    # Every function must have a return type.
    if rt is -1 or not is_valid_type(rt):
        print("\n *** Every hacpsec function must have a return type: \"" + fun_name+"\"")
        exit(1)
    return


def import_is_hacspec(filename):
    if filename.endswith("speclib"):
        # speclib can always be used.
        return True
    # TODO: This currently doesn't work with PYTHONPATH set.
    return True
    if not file_dir:
        print(" *** No file_dir set :/ Something is wrong. ***")
        exit(1)
    print(filename.split('.'))
    filename = os.path.join(*filename.split('.'))
    filename = os.path.join(file_dir, filename + ".py")
    try:
        with open(filename, 'r', encoding='utf-8') as py_file:
            return True
    except:
        print(" *** File is not a valid hacspec. Import \"" + filename + "\" is not a local spec.")
        exit(1)
    return True

def is_valid_binop(op):
    # hacspec allows all binops.
    return True

def is_valid_compop(op):
    # TODO: check
    return True

def is_expression(node):
    if isinstance(node, Lambda):
        # TODO: do we want to check the lambda?
        return True
    if isinstance(node, BinOp) and is_valid_binop(node.op) and \
        is_expression(node.left) and is_expression(node.right):
        return True
    if isinstance(node, Compare) and is_expression(node.left):
        for op in node.ops:
            if not is_valid_compop(op):
                return False
        for comp in node.comparators:
            if not is_expression(comp):
                return False
        return True
    if isinstance(node, BoolOp):
        for value in node.values:
            if not is_expression(value):
                return False
        return True
    if isinstance(node, Attribute) and is_expression(node.value):
        return True
    if isinstance(node, UnaryOp) and is_expression(node.operand):
        return True
    if isinstance(node, NameConstant):
        if node.value is True or node.value is False or node.value is None:
            return True
        return False
    if not (isinstance(node, Call) or isinstance(node, Subscript) \
        or isinstance(node, Name) or isinstance(node, Num) or \
        isinstance(node, Tuple)):
        # Python lists are only allowed when passing them to hacspec arrays.
        return False
    return True

def is_statement(node):
    if isinstance(node, list):
        # Read all the lines.
        if len(node) < 1:
            return False
        for n in node:
            if not is_statement(n):
                return False
        return True
    if isinstance(node, Assign):
        if len(node.targets) < 1:
            return False
        for target in node.targets:
            if not isinstance(target, Name) \
               and not isinstance(target, Tuple) \
               and not isinstance(target, Subscript):
                return False
        return True
    if isinstance(node, AugAssign):
        if not isinstance(node.target, Name) \
           and not isinstance(node.target, Tuple) \
           and not isinstance(node.target, Subscript):
            return False
        return True
    if isinstance(node, AnnAssign):
        if not isinstance(node.target, Name) \
           and not isinstance(node.target, Tuple):
            return False
        return True
    if isinstance(node, Return):
        return True
    if isinstance(node, Expr) and isinstance(node.value, Call):
        return True
    if isinstance(node, If):
        return True
    if isinstance(node, For):
        return True
    return False

# Check annotation. Must be a type with _t at the end. Can we do better?
def is_valid_type(node):
    if isinstance(node, Name):
        node = node.id
    if node is None:
        return True
    if not isinstance(node, str):
        return False
    if not (node.endswith("_t") or node is "tuple2" or node is "tuple3" \
        or node is "tuple4" or node is "tuple5" or node is "FunctionType" \
        or node is "int" or node is "bool"):
        return False
    return True

def read(node) -> None:
    if node is None:
        # This can happen when reading a None NameConstant
        return

    if isinstance(node, Module):
        return read(node.body)

    if isinstance(node, ImportFrom):
        # Check that the imported file is a local hacspec or speclib.
        if not import_is_hacspec(node.module):
            print("Import " + f + " is not a local hacspec file or speclib.")
            exit(1)
        return

    if isinstance(node, Tuple):
        for e in node.elts:
            read(e)
        return

    # Normal assignments.
    if isinstance(node, Assign):
        # Allowed targets are variables, tuples, array element update,
        # array slice update.
        read(node.targets)
        valid_left = False
        for t in node.targets:
            if isinstance(t, Name) or isinstance(t, Subscript) or isinstance(t, Tuple):
                valid_left = True
                break
            else:
                print("\n *** Invalid assignment " + str(t))
                exit(1)
        if not valid_left:
            print("\n *** Invalid assign.")
            exit(1)
        # The right side of the assignment can be any expression.
        read(node.value)
        if not is_expression(node.value):
            print("\n *** Invalid assignment. Right side must be expression not " + str(node.value))
            exit(1)
        if node.type_comment:
            print("\n *** Type comments are not supported by hacspec.")
            exit(1)
        # Check that types are named _t.
        # Types come from _t functions or refine.
        if isinstance(node.value, Call):
            if isinstance(node.value.func, Name):
                fun_name = node.value.func.id
                # Check speclib functions that make types.
                if fun_name is "range_t" or fun_name is "array_t" or \
                   fun_name is "bytes_t" or fun_name is "refine":
                    if len(node.targets) > 1:
                        print("\n *** Custom type assignment must have single assignment target " + str(fun_name))
                        exit(1)
                    type_name = node.targets[0]
                    if not isinstance(type_name, Name) and not isinstance(type_name, Tuple):
                        print("\n *** Custom type assignment has wrong assignment target " + str(type_name))
                        exit(1)
                    type_name_string = ""
                    if isinstance(type_name, Name):
                        type_name_string = type_name.id
                    else:
                        type_name_string = type_name.elts[0].id
                    if not type_name_string.endswith("_t"):
                        print("\n *** Custom type names must end on _t " + str(type_name.id))
                        exit(1)
        return

    if isinstance(node, AugAssign):
        # Allowed targets are variables and array element update
        read(node.target)
        if isinstance(node.target, Name) or \
           (isinstance(node.target, Subscript) and isinstance(node.target.slice, Index)):
            pass
        else:
            print("\n *** Invalid aug assignment " + str(node.target))
            exit(1)
        read(node.op)
        if not is_valid_binop(node.op):
            print("\n *** Invalid aug assignment " + str(node.target))
            exit(1)
        read(node.value)
        if not is_expression(node.value):
            print("\n *** Invalid aug assignment. Right side must be expression " + str(node.value))
            exit(1)
        return

    if isinstance(node, AnnAssign):
        # Allowed targets are variables.
        read(node.target)
        if not isinstance(node.target, Name):
            print("\n *** Invalid ann assignment (Name) " + str(node.target))
            exit(1)
        read(node.annotation)
        if not is_valid_type(node.annotation):
            print("\n *** Invalid ann assignment (annotation) " + str(node.target))
            exit(1)
        read(node.value)
        if not is_expression(node.value):
            print("\n *** Invalid ann assignment. Right side must be expression " + str(node.value))
            exit(1)
        return

    # Lists are ok as long as they aren't assigned directly.
    if isinstance(node, List):
        for elt in node.elts:
            read(elt)
        return

    if isinstance(node, Attribute):
        # TODO: can we check something here?
        #       This is for example array.length()
        # node.attr is str
        read(node.value)
        return

    if isinstance(node, BinOp):
        read(node.left)
        read(node.op)
        if not is_valid_binop(node.op):
            print("\n *** Not a valid hacspec with " + str(node.op))
            exit(1)
        read(node.right)
        return

    # Primitive types
    if isinstance(node, Num):
        # node.n
        return

    if isinstance(node, Name):
        # node.id
        return
    if isinstance(node, NameConstant):
        return read(node.value)

    # We don't really care about these.
    if isinstance(node, Load):
        return
    if isinstance(node, Store):
        return
    if isinstance(node, AugStore):
        return
    if isinstance(node, AugLoad):
        return

    if isinstance(node, For):
        read(node.target)
        if node.body:
            read(node.body)
            if not is_statement(node.body):
                print("\n *** For loop body is not a statement "+str(node.body))
                exit(1)
        if node.orelse:
            read(node.orelse)
            print(node.orelse)
        if node.iter:
            read(node.iter)
        return

    # Operators
    if isinstance(node, Pow):
        return
    if isinstance(node, Sub):
        return
    if isinstance(node, Mult):
        return
    if isinstance(node, Add):
        return
    if isinstance(node, Mod):
        return
    if isinstance(node, FloorDiv):
        return
    if isinstance(node, Div):
        return
    if isinstance(node, BitXor):
        return
    if isinstance(node, RShift):
        return
    if isinstance(node, BitAnd):
        return
    if isinstance(node, BitOr):
        return
    if isinstance(node, UnaryOp):
        return
    if isinstance(node, Compare):
        read(node.left)
        for c in node.comparators:
            read(c)
        return
    if isinstance(node, LShift):
        return

    if isinstance(node, BoolOp):
        # node.op
        for ex in node.values:
            read(ex)
        return

    if isinstance(node, Subscript):
        # TODO: is there anything we can check for subscript?
        read(node.value)
        return

    # Functions
    if isinstance(node, FunctionDef):
        read_function_signature(node)
        read(node.body)
        return

    if isinstance(node, Return):
        read(node.value)
        if not is_expression(node.value):
            print("\n *** Invalid return statement. " + str(node.value))
            exit(1)
        return

    if isinstance(node, Call):
        read(node.func)
        if node.args:
            read(node.args)
        if len(node.keywords) > 0:
            print("\n *** Keywords aren't allowed in hacspec function calls.")
            exit(1)
        return

    if isinstance(node, bool):
        return

    if isinstance(node, Expr):
        # A simple function call
        read(node.value)
        if not is_expression(node.value):
            print("\n *** Invalid expression " + str(node))
            exit(1)
        return

    if isinstance(node, If):
        read(node.test)
        if not is_expression(node.test):
            print("\n *** Invalid if statement (test). " + str(node.test))
            exit(1)
        read(node.body)
        if not is_statement(node.body):
            print("\n *** Invalid if statement (body). " + str(node.body))
            exit(1)
        read(node.orelse)
        if node.orelse and not is_statement(node.orelse):
            print("\n *** Invalid if statement (orelse). " + str(node.orelse))
            exit(1)
        return

    if isinstance(node, While):
        print("\n *** While statements are not allowed in hacspec.")
        exit(1)

    if isinstance(node, Str):
        # node.s
        return

    if isinstance(node, arguments):
        for a in node.args:
            read(a)
        if len(node.defaults) != 0:
            print("\n *** Default arguments are not supported in hacspec.")
            exit(1)
        if len(node.kwonlyargs) != 0:
            print("\n *** keyword only args are not allowed in hacspec.")
            exit(1)
        if node.vararg is not None:
            print("\n *** varargs are not allowed in hacspec")
            exit(1)
        if len(node.kw_defaults) != 0:
            print("\n *** keyword defaults are not allowed in hacspec")
            exit(1)
        if node.kwarg is not None:
            print("\n *** keyword args are not allowed in hacspec")
            exit(1)
        return

    if isinstance(node, arg):
        return

    if isinstance(node, Lambda):
        # TODO: check lambda for contract and refine.
        read(node.args)
        read(node.body)
        return

    # List of nodes, read all of them.
    if isinstance(node, list):
        for x in node:
            read(x)
        return

    print("\n *** " + str(type(node)) + " is not allowed in hacspecs.\n")
    exit(1)


def main():
    if len(argv) != 2:
        print("Usage: hacspec-check <hacspec>")
        exit(1)
    path = argv[1]
    with open(path, 'r', encoding='utf-8') as py_file:
        global file_dir
        file_dir = os.path.dirname(os.path.abspath(path))
        code = py_file.read()
        ast = parse(source=code, filename=path)
        parsed = read(ast)
        print(path + " is a valid hacspec.")


if __name__ == "__main__":
    main()
