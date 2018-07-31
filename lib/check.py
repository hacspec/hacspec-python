#!/usr/bin/env python3

from typed_ast.ast3 import *
from sys import argv
from os import environ
import os

file_dir = None
variables = []

def fail(s):
    print("\n *** " + s + "\n")
    exit(1)

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
                        fail("Couldn't parse function return values: \"" + fun_name+"\"")
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
            fail("Function decorators must be names or calls not " + str(d))
    # Every function must have a typechecked decorator.
    typechecked = False
    for decorator in decorators:
        if decorator == "typechecked":
            typechecked = True
            break
    if not typechecked:
        fail("Every hacpsec function must have a @typechecked decorator: \"" + fun_name+"\"")
    try:
        arg_names.remove("self")
    except:
        pass
    # Every argument must be typed.
    if len(arg_types) != len(arg_names):
        fail("Every hacpsec function argument must be typed: \"" + fun_name+"\"")
    # Check arg_types.
    for arg_type in arg_types:
        if not is_valid_type(arg_type):
            fail("Invalid argument type in function signature " + fun_name + " - " + str(arg_type))
    # Every function must have a return type.
    if rt is -1 or not is_valid_type(rt):
        fail("Every hacpsec function must have a return type: \"" + fun_name+"\"")
    return

def check_variable_is_typed(line):
    # Make sure that all local variables are typed by either:
    # i) annotated assign or
    # ii) typed variable declaration
    global variables
    speclibFunctions = ["array.copy", "array.create", "refine", "bytes"]
    if isinstance(line, Assign):
        if len(line.targets) > 0 and isinstance(line.targets[0], Tuple):
            # This is a tuple assignment. The variables have to be declared
            # before use.
            for target in line.targets[0].elts:
                if not isinstance(target, Name):
                    fail("Tuple values must be names.")
                if not target.id in variables and not target.id is "_":
                    if isinstance(line.value, Call) and \
                       line.value.func.id is "refine":
                        return None
                    fail("Untyped variable used in tuple assignment \"" + str(target.id) + "\"")
        elif len(line.targets) > 1:
            fail("Only tuple assignment or single variable assignments are allowed")
        else:
            target = line.targets[0]
            if isinstance(target, Subscript):
                # Subscripts assign to arrays that are typed in speclib.
                return None
            if not isinstance(target, Name):
                fail("Variable assignment targets have to be variable names.")
            if isinstance(line.value, Call) and \
               isinstance(line.value.func, Name) and \
               (line.value.func.id in ["array"] or line.value.func.id in speclibFunctions):
                # No type for arrays needed.
                variables.append(target.id)
                return None
            if isinstance(line.value, Call) and \
               isinstance(line.value.func, Attribute) and \
               isinstance(line.value.func.value, Name) and \
               line.value.func.value.id +"."+ line.value.func.attr in speclibFunctions:
                # No type for arrays needed.
                variables.append(target.id)
                return None
            if target.id.endswith("_t"):
                # This is a type not a variable. Ignore it.
                return None
            if not target.id in variables:
                fail("Variable assignment doesn't have a type \""+target.id+"\"")
    if isinstance(line, AnnAssign):
        if line.value is None:
            # This is a variable declaration.
            variables.append(line.target.id)
        else:
            if isinstance(line.annotation, Name):
                # We could check the type here of line.annotation.id.
                # But seeing n annotation here is enough for us atm.
                pass
            if not isinstance(line.target, Name):
                fail("Variable ann-assignment target must be a Name \""+str(line.target)+"\"")
            variables.append(line.target.id)

# def read_function_body(body):
#     variables = []
#     for line in body:
#         read_line(line, variables)

def import_is_hacspec(filename):
    if filename.endswith("speclib"):
        # speclib can always be used.
        return True
    # TODO: This currently doesn't work with PYTHONPATH set.
    return True
    if not file_dir:
        fail("No file_dir set :/ Something is wrong.")
    print(filename.split('.'))
    filename = os.path.join(*filename.split('.'))
    filename = os.path.join(file_dir, filename + ".py")
    try:
        with open(filename, 'r', encoding='utf-8') as py_file:
            return True
    except:
        fail("File is not a valid hacspec. Import \"" + filename + "\" is not a local spec.")
    return True

def is_valid_binop(op):
    # hacspec allows all binops.
    return True

def is_valid_compop(op):
    # TODO: check
    if isinstance(op, In):
        # Don't allow in as comparator as it has many meanings in python.
        return False
    return True

def is_expression(node):
    if node is None:
        return True
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
    if isinstance(node, Break):
        return True
    return False

# Check annotation. Must be a type with _t at the end. Can we do better?
def is_valid_type(node):
    if isinstance(node, Name):
        node = node.id
    if node is None:
        return True
    if isinstance(node, Call):
        fun_name = node.func.id
        if fun_name in ("vlarray_t", "result_t", "array_t", "array"):
            return True
    if not isinstance(node, str):
        return False
    if not (node.endswith("_t") or node is "tuple2" or node is "tuple3" \
        or node is "tuple4" or node is "tuple5" or node is "FunctionType" \
        or node is "int" or node is "bool" or node is "refine_t" \
        or node is "vlarray_t"):
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
            fail("Import " + f + " is not a local hacspec file or speclib.")
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
                fail("Invalid assignment " + str(t))
        if not valid_left:
            fail("Invalid assign.")
        # The right side of the assignment can be any expression.
        read(node.value)
        if not is_expression(node.value):
            fail("Invalid assignment. Right side must be expression not " + str(node.value))
        if node.type_comment:
            fail("Type comments are not supported by hacspec.")
        # Check that types are named _t.
        # Types come from _t functions or refine.
        if isinstance(node.value, Call):
            if isinstance(node.value.func, Name):
                fun_name = node.value.func.id
                # Check speclib functions that make types.
                if fun_name is "range_t" or fun_name is "array_t" or \
                   fun_name is "bytes_t" or fun_name is "refine_t":
                    if len(node.targets) > 1:
                        fail("Custom type assignment must have single assignment target " + str(fun_name))
                    type_name = node.targets[0]
                    if not isinstance(type_name, Name) and not isinstance(type_name, Tuple):
                        fail("Custom type assignment has wrong assignment target " + str(type_name))
                    type_name_string = ""
                    if isinstance(type_name, Name):
                        type_name_string = type_name.id
                    else:
                        type_name_string = type_name.elts[0].id
                    if not type_name_string.endswith("_t"):
                        fail("Custom type names must end on _t " + str(type_name.id))
        check_variable_is_typed(node)
        return

    if isinstance(node, AugAssign):
        # Allowed targets are variables and array element update
        read(node.target)
        if isinstance(node.target, Name) or \
           (isinstance(node.target, Subscript) and isinstance(node.target.slice, Index)):
            pass
        else:
            fail("Invalid aug assignment " + str(node.target))
        read(node.op)
        if not is_valid_binop(node.op):
            fail("Invalid aug assignment " + str(node.target))
        read(node.value)
        if not is_expression(node.value):
            fail("Invalid aug assignment. Right side must be expression " + str(node.value))
        return

    if isinstance(node, AnnAssign):
        # Allowed targets are variables.
        read(node.target)
        if not isinstance(node.target, Name):
            fail("Invalid ann assignment (Name) " + str(node.target))
        read(node.annotation)
        if not is_valid_type(node.annotation):
            fail("Invalid ann assignment (annotation) " + str(node.target.id))
        read(node.value)
        if not is_expression(node.value):
            fail("Invalid ann assignment. Right side must be expression " + str(node.value))
        check_variable_is_typed(node)
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
            fail("Not a valid hacspec with " + str(node.op))
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
                fail("For loop body is not a statement "+str(node.body))
        if node.orelse:
            read(node.orelse)
        if node.iter and isinstance(node.iter, Call):
            if not (isinstance(node.iter.func, Name) and node.iter.func.id is "range"):
                fail("For loops must use range(max) as iterator "+str(node.iter))
            if len(node.iter.args) != 1:
                fail("For loops must use range(max) as iterator "+str(node.iter))
            read(node.iter)
        else:
            fail("For loops must use range(max) as iterator "+str(node.iter))
        return
    if isinstance(node, Break):
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
    if isinstance(node, Or):
        return
    if isinstance(node, And):
        return
    if isinstance(node, Compare):
        read(node.left)
        for c in node.comparators:
            read(c)
        return
    if isinstance(node, LShift):
        return

    if isinstance(node, BoolOp):
        read(node.op)
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
        # Reset variables.
        global variables
        variables = []
        read(node.body)
        return

    if isinstance(node, Return):
        read(node.value)
        if not is_expression(node.value):
            fail("Invalid return statement. " + str(node.value))
        return

    if isinstance(node, Call):
        read(node.func)
        if node.args:
            read(node.args)
        if len(node.keywords) > 0:
            fail("Keywords aren't allowed in hacspec function calls.")
        return

    if isinstance(node, bool):
        return

    if isinstance(node, Expr):
        # A simple function call
        read(node.value)
        if not is_expression(node.value):
            fail("Invalid expression " + str(node))
        return

    if isinstance(node, If):
        read(node.test)
        if not is_expression(node.test):
            fail("Invalid if statement (test). " + str(node.test))
        read(node.body)
        if not is_statement(node.body):
            fail("Invalid if statement (body). " + str(node.body))
        read(node.orelse)
        if node.orelse and not is_statement(node.orelse):
            fail("Invalid if statement (orelse). " + str(node.orelse))
        return

    if isinstance(node, While):
        fail("While statements are not allowed in hacspec.")
        # read(node.test)
        # if not is_expression(node.test):
        #     fail("Invalid expression in while test " + str(node.test))
        # read(node.body)
        # if not is_statement(node.body):
        #     fail("Invalid statement in while body " + str(node.body))
        # if node.orelse:
        #     read(node.orelse)
        #     if not is_statement(node.orelse):
        #         fail("Invalid statement in while orelse " + str(node.orelse))
        # return

    if isinstance(node, Str):
        # node.s
        return

    if isinstance(node, arguments):
        for a in node.args:
            read(a)
        if len(node.defaults) != 0:
            fail("Default arguments are not supported in hacspec.")
        if len(node.kwonlyargs) != 0:
            fail("keyword only args are not allowed in hacspec.")
        if node.vararg is not None:
            fail("varargs are not allowed in hacspec")
        if len(node.kw_defaults) != 0:
            fail("keyword defaults are not allowed in hacspec")
        if node.kwarg is not None:
            fail("keyword args are not allowed in hacspec")
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

    fail(str(type(node)) + " is not allowed in hacspecs.")


def main():
    if len(argv) != 2:
        fail("Usage: hacspec-check <hacspec>")
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
