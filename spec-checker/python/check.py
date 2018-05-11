from typed_ast.ast3 import *
from sys import argv


class FunctionSignature():
    def __init__(self):
        self.fun_name = ""
        self.argtypes = []
        self.argnames = []
        self.returntype = None
        self.class_ = ""

    def __str__(self) -> str:
        return_types = self.returntype
        if return_types and len(return_types) == 1:
            return_types = return_types[0]
        args = " ("
        for (arg,t) in zip(self.argnames, self.argtypes):
            args += arg + ":" + t + ","
        if len(args) > 2:
            args = args[:-1]
        args += ")"
        return self.fun_name + args + " -> " + str(return_types)

    @staticmethod
    def create(fun_name, arg_types, arg_names, rt, cl=""):
        fs = FunctionSignature()
        fs.argnames = arg_names
        fs.argtypes = arg_types
        fs.returntype = rt
        fs.fun_name = fun_name
        fs.class_ = cl
        return fs

    def add_arg(self, arg):
        self.argnames.append(arg)

    def set_return_type(self, t):
        self.returntype = t

    def get_args(self):
        return self.argnames

    def get_arg_types(self):
        return self.argtypes

    def get_return_type(self):
        return self.returntype

    def get_fun_name(self):
        name = ""
        if self.class_:
            name += str(self.class_) + "."
        name += self.fun_name
        return name

    def get_class_name(self):
        return str(self.class_)


class AstItem():
    def __init__(self, t, args=None):
        self.t = t
        self.args = []
        if args is not None:
            if isinstance(args, str):
                self.args.append(args)
            else:
                for a in args:
                    self.args.append(a)

    def __str__(self):
        return str(self.t) + ": " + str(self.args)

    def __repr__(self):
        return str(self)

    def get_function_signature(self):
        assert(self.t.__name__ == "FunctionDef")
        assert(isinstance(self.args[0], FunctionSignature))
        return self.args[0]

    def get_function_call(self):
        assert(self.t.__name__ == "Call")
        fun = self.args[0]
        # print(type(fun.args[0]))
        if type(fun.args[0]) == str:
            name = fun.args[0]
        elif type(fun.args[0]).__name__ == "AstName":
            name = fun.args[0].args[0]
        else:
            assert(False)
        args = self.args[1]
        assert(args.t.__name__ == "List")
        types = []
        for arg in args.args:
            # TODO: Arguments that are variables are names. We have to get the type
            # if arg.t.__name__ == "Name":
            #     print(arg.args[-1].t)
            #     print(arg.args[0].args[0])
            types.append(arg.t)
        class_ = ""
        if len(fun.args) > 1:
            class_ = fun.args[1].args[0]
        return (class_, name, types)


class AstName(AstItem):
    def __init__(self, name):
        super().__init__(str, [name])
        self.type = None
        self.element_type = None

    def __str__(self):
        t = ""
        if self.type:
            t = ":" + str(self.type)
        return str(self.args[0]) + t

    def __repr__(self):
        return str(self)

    def set_type(self, t):
        if not (type(t) is type or type(t) is str):
            print("set_type only works with type or str ("+str(type(t))+")")
            exit(1)
        self.type = t

    def set_element_type(self, t):
        if not (type(t) is type or type(t) is str):
            print("set_type only works with type or str ("+str(type(t))+")")
            exit(1)
        self.element_type = t

    def get_type(self):
        return self.type

    def get_name(self):
        return str(self.args[0])


class AstAttribute(AstItem):
    def __init__(self, name, cl):
        assert(type(name) == str)
        super().__init__(Attribute, [cl, AstName(name)])
        self.name = name
        self.class_ = cl

    def __str__(self):
        return str(self.class_) + "." + str(self.class_)

    def __repr__(self):
        return str(self)

    def get_function_name(self):
        return self.name

    def get_class_name(self):
        return self.class_


class Variable(AstItem):
    def __init__(self, t, name):
        assert(type(name) == str)
        super().__init__(t, [name])

    def __str__(self):
        return str(self.args[0]) + ": " + str(self.t)

    def __repr__(self):
        return str(self)

    def set_type(self, d):
        if type(d) is not FunctionSignature:
            print("set_type only works with FunctionSignature")
            exit(1)
        print(d)


class VariableTuple(AstItem):
    def __init__(self, names):
        assert(type(names) == list)
        super().__init__(Tuple, names)
        self.types = []

    def __str__(self):
        return str(self.args) + ": " + str(self.types)

    def __repr__(self):
        return str(self)

    def set_type(self, t):
        if type(t) is not list:
            print("Tuple.set_types type has to be a list.")
            exit(1)
        self.types = t

    def get_type(self):
        return self.types

    def get_name(self):
        return self.args


class VariableSubscript(AstName):
    def __init__(self, name, sl, slt):
        assert(type(name) == str)
        super().__init__(name)
        # TODO: verify slice
        self.slice = sl
        self.slice_type = slt

    def __str__(self):
        return str(self.args[0])

    def __repr__(self):
        return str(self)


class FunctionCall(AstItem):
    def __init__(self, f):
        assert(type(f) == FunctionSignature)
        super().__init__(Call)
        self.fun = f

    def __str__(self):
        return str(self.fun)

    def __repr__(self):
        return str(self)

    def get_function_signature(self):
        return self.fun


class AstIf(AstItem):
    def __init__(self, test, body, orelse):
        super().__init__(If, [test, body, orelse])
        self.test = test
        self.body = body
        self.orelse = orelse

    def __str__(self):
        return "if " + str(self.test) + " then " + str(self.body) + " else " + str(self.orelse)

    def __repr__(self):
        return str(self)


class AstType(AstItem):
    def __init__(self, name, base, refinement):
        super().__init__(type, [name, base, refinement])
        self.name = name
        self.base = base
        self.refinement = refinement

    def __str__(self):
        return str(self.name) + " := " + str(self.base) + "(" + str(self.refinement) + ")"

    def __repr__(self):
        return str(self)


class AstBinOp(AstItem):
    def __init__(self, left, op, right):
        super().__init__(BinOp, [left, op, right])
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return str(self.left) + " " + str(self.op) + " " + str(self.right)

    def __repr__(self):
        return str(self)


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
                    tmp2.append(x.id)
                rt += str(tmp2)
            else:
                rt += str(tmp)
        elif isinstance(f.returns, NameConstant):
            rt = f.returns.value
        elif isinstance(f.returns, Call):
            rt = f.returns.func.id
    decorators = [read(x, fun_name) for x in f.decorator_list]
    # Every function must have a typechecked decorator.
    if len(decorators) != 1 or decorators[0].get_name() != "typechecked":
        print("Every hacpsec function must have a @typechecked decorator: \"" + fun_name+"\"")
        exit(1)
    try:
        arg_names.remove("self")
    except:
        pass
    # Every argument must be typed.
    if len(arg_types) != len(arg_names):
        print("Every hacpsec function argument must be typed: \"" + fun_name+"\"")
        exit(1)
    # Every function must have a return type.
    if rt is -1:
        print("Every hacpsec function must have a return type: \"" + fun_name+"\"")
        exit(1)
    return FunctionSignature.create(fun_name, arg_types, arg_names, rt)


def read(node, cl=None):
    # FIXME: this shouldn't be allowed
    if node is None:
        print(" >>>>>>>>> none node in spec (something is probably wrong)")
        return

    if isinstance(node, Module):
        return AstItem(Module, [read(node.body)])

    if isinstance(node, ImportFrom):
        return AstItem(ImportFrom, [node.module])

    if isinstance(node, Tuple):
        tuples = []
        for e in node.elts:
            tuples.append(str(read(e)))
        return VariableTuple(tuples)

    # Normal assignments with types in comments
    if isinstance(node, Assign):
        args = [read(t) for t in node.targets]
        args.append(read(node.value))
        if node.type_comment:
            print("Type comments are not supported by hacspec")
            exit(1)
        return AstItem(Assign, args)

    if isinstance(node, AugAssign):
        target = read(node.target)
        op = read(node.op)
        value = read(node.value)
        return AstItem(AugAssign, [target, op, value])

    if isinstance(node, AnnAssign):
        args = [read(node.target)]
        if node.value:
            args.append(read(node.value))
        args.append(read(node.annotation))
        return AstItem(AnnAssign, args)

    if isinstance(node, List):
        l = []
        for elt in node.elts:
            l.append(read(elt))
        return AstItem(List, l)

    if isinstance(node, Attribute):
        return AstAttribute(node.attr, read(node.value))

    if isinstance(node, BinOp):
        left = read(node.left)
        op = read(node.op)
        right = read(node.right)
        return AstBinOp(left, op, right)

    # Primitive types
    if isinstance(node, Num):
        return AstItem(Num, [node.n])

    if isinstance(node, Name):
        return AstName(node.id)

    if isinstance(node, Load):
        return AstItem(Load)
    if isinstance(node, Store):
        return AstItem(Store)
    if isinstance(node, AugStore):
        return AstItem(AugStore)
    if isinstance(node, AugLoad):
        return AstItem(AugLoad)

        # Loops
    if isinstance(node, For):
        args = [read(node.target)]
        if node.body:
            args.append(read(node.body))
        if node.orelse:
            args.append(read(node.orelse))
        if node.iter:
            args.append(read(node.iter))
        return AstItem(For, args)

    # Operators
    if isinstance(node, Pow):
        return AstItem(Pow)
    if isinstance(node, Sub):
        return AstItem(Sub)
    if isinstance(node, Mult):
        return AstItem(Mult)
    if isinstance(node, Add):
        return AstItem(Add)
    if isinstance(node, Mod):
        return AstItem(Mod)
    if isinstance(node, FloorDiv):
        return AstItem(FloorDiv)
    if isinstance(node, Div):
        return AstItem(FloorDiv)
    if isinstance(node, BitXor):
        return AstItem(BitXor)
    if isinstance(node, RShift):
        return AstItem(RShift)
    if isinstance(node, BitAnd):
        return AstItem(BitAnd)
    if isinstance(node, BitOr):
        return AstItem(BitOr)
    if isinstance(node, UnaryOp):
        return AstItem(UnaryOp)
    if isinstance(node, Compare):
        comp = [read(node.left)]
        for c in node.comparators:
            comp.append(read(c))
        return AstItem(Compare, comp)
    if isinstance(node, LShift):
        return AstItem(LShift)

    if isinstance(node, BoolOp):
        values = [node.op]
        for ex in node.values:
            values.append(read(ex))
        return AstItem(BoolOp, values)

    if isinstance(node, Subscript):
        r = VariableSubscript(str(read(node.value)),
                              node.slice, type(node.slice))
        return r

    # Functions
    if isinstance(node, FunctionDef):
        sig = read_function_signature(node)
        body = read(node.body)
        # if cl:
        #     print(str(cl) + "::" + str(sig))
        # else:
        #     print(sig)
        return AstItem(FunctionDef, [sig, body])

    if isinstance(node, ClassDef):
        bases = [read(x, node.name) for x in node.bases]
        bodies = [read(x, node.name) for x in node.body]
        keywords = [read(x, node.name) for x in node.keywords]
        decorators = [read(x, node.name) for x in node.decorator_list]
        # print("class: " + str(node.name))
        return AstItem(ClassDef, [node.name, bases, bodies, decorators])

    if isinstance(node, Return):
        return AstItem(Return, [read(node.value)])

    if isinstance(node, Call):
        args = [read(node.func)]
        if node.args:
            args.append(read(node.args))
        # build function signature
        name = args[0]
        cl = ""
        if isinstance(name, AstAttribute):
            cl = name.get_class_name()
            name = name.get_function_name()
        f = FunctionSignature.create(str(name), [], args[1:], None, cl)
        r = FunctionCall(f)
        # TODO: read keywords?
        return r

    if isinstance(node, Expr):
        return AstItem(Expr, [read(node.value)])

    if isinstance(node, If):
        test = read(node.test)
        body = read(node.body)
        orelse = read(node.orelse)
        return AstIf(test, body, orelse)

    if isinstance(node, While):
        test = read(node.test)
        body = read(node.body)
        orelse = read(node.orelse)
        return AstItem(While, [test, orelse, body])

    if isinstance(node, Str):
        return AstItem(Str, [node.s])

    if isinstance(node, arguments):
        args = [read(a) for a in node.args]
        if len(node.defaults) != 0:
            print("Default arguments are not supported in hacspec.")
            exit(1)
        if len(node.kwonlyargs) != 0:
            print("keyword only args are not allowed in hacspec.")
            exit(1)
        if node.vararg is not None:
            print("varargs are not allowed in hacspec")
            exit(1)
        if len(node.kw_defaults) != 0:
            print("keyword defaults are not allowed in hacspec")
            exit(1)
        if node.kwarg is not None:
            print("keyword args are not allowed in hacspec")
            exit(1)
        return AstItem(arguments, args)

    if isinstance(node, arg):
        return AstItem(arg)

    if isinstance(node, Lambda):
        args = read(node.args)
        body = read(node.body)
        return AstItem(Lambda, [args, body])

    # List of nodes, read all of them.
    if isinstance(node, list):
        nodes = []
        for x in node:
            nodes.append(read(x))
        return AstItem(List, nodes)

    return

def filter(parsed, obj, to_find):
    filtered = []
    def rec(x, obj, item=None):
        if isinstance(x, AstItem):
            for y in x.args:
                if isinstance(x.t, type) and x.t.__name__ == to_find:
                    if item not in filtered:
                        filtered.append(x)
                        return
                rec(y, obj, x)
        elif isinstance(x, list):
            for y in x:
                rec(y, obj)
        else:
            if item and isinstance(item.t, type) and item.t.__name__ == to_find:
                if item not in filtered:
                    filtered.append(item)
                    return
    for a in parsed.args:
        rec(a, obj)
    return filtered

def read_objects(ast, obj):
    mod = ast.body
    if mod is None:
        # ast root has to be Module.
        return []
    if not isinstance(mod, list):
        # The ast module is a list of nodes.
        return []
    parsed = read(ast)
    filtered = filter(parsed, obj, obj.__name__)
    return filtered

def main(path):
    with open(path, 'r', encoding='utf-8') as py_file:
        code = py_file.read()
        ast = parse(source=code, filename=path)

        imports = read_objects(ast, ImportFrom)
        # TODO: this doesn't read nested functions properly.
        functions = read_objects(ast, FunctionDef)

        PRINT = False
        if PRINT:
            print("\nFile: " + path)
            print("\nImports: ")
            for i in imports:
                print(i)
            print("\nFunctions: ")
            for f in functions:
                print(f.get_function_signature())


if __name__ == "__main__":
    main(argv[1])
