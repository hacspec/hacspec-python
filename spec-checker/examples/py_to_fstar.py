from typed_ast.ast3 import *
from sys import argv

def dump(node, annotate_fields=True, include_attributes=False):
    """
    Return a formatted dump of the tree in *node*.  This is mainly useful for
    debugging purposes.  The returned string will show the names and the values
    for fields.  This makes the code impossible to evaluate, so if evaluation is
    wanted *annotate_fields* must be set to False.  Attributes such as line
    numbers and column offsets are not dumped by default.  If this is wanted,
    *include_attributes* can be set to True.
    """

    def _tuple(vs):
        if len(vs) == 0:
            return "()"
        else:
            return "("+",".join(vs)+")"

    def _lvalues(node):
        if (isinstance(node, Assign) and
            isinstance(node.value,Call) and
            isinstance(node.value.func,Name) and
            node.value.func.id == 'NewType'):
            return []
        elif isinstance(node, Assign):
            return [_format(x) for x in node.targets]
        elif isinstance(node, AugAssign):
            return [node.target]
        elif isinstance(node, list):
            return [x for y in node for x in _lvalues(y)]
        else:
            return []
        
    def _operator(o):
        if isinstance(o,Pow):
            return "**"
        elif isinstance(o,Sub):
            return "-"
        elif isinstance(o,Add):
            return "+"
        elif isinstance(o,Mult):
            return "*"
        elif isinstance(o,BitAnd):
            return "&"
        elif isinstance(o,BitXor):
            return "^"
        elif isinstance(o,Mod):
            return "%"
        elif isinstance(o,Eq):
            return "="
        else:
            return " <unknown_op> "

    def _sep(top): 
        if top:
            return "; "
        else:
            return " in "
        
    def _format(node,top=False):
       # if isinstance(node, AST):
       #     fields = [(a, _format(b)) for a, b in iter_fields(node)]
       #     rv = '%s(%s' % (node.__class__.__name__, (',\n').join(
       #         ('%s=%s' % field for field in fields)
       #         if annotate_fields else
       #         (b for a, b in fields)
       #     ))
       #     if include_attributes and node._attributes:
       #         rv += fields and ',\n' or ' '
       #         rv += ', '.join('%s=%s' % (a, _format(getattr(node, a)))
       #                         for a in node._attributes)
       #     return rv + ')'
       # else:
        if isinstance(node, Module):
            return _format(node.body,True)
        if isinstance(node, ImportFrom):
            return "open "+node.module+";"
        if (isinstance(node, Assign) and
            isinstance(node.value,Call) and
            isinstance(node.value.func,Name) and
            node.value.func.id == 'NewType'):
            vs = [_format(x,top) for x in node.targets]
            ty = node.value.args[1].id
            nty = vs[0]+"_t"
            return ("type "+nty+" = "+ty+";\n"+
                    "let "+vs[0]+" (x:"+ty+") : "+nty+" = x")
        if (isinstance(node, Assign) and
            len(node.targets) == 1 and
            isinstance(node.targets[0],Subscript) and
            isinstance(node.targets[0].slice,Index)) :
            arr = _format(node.targets[0].value);
            idx = _format(node.targets[0].slice.value);
            return "let "+arr+" = "+ arr+".["+idx+"] <- "+_format(node.value)+_sep(top)
        if (isinstance(node, Assign) and
            len(node.targets) == 1 and
            isinstance(node.targets[0],Subscript) and
            isinstance(node.targets[0].slice,Slice)) :
            arr = _format(node.targets[0].value);
            low = _format(node.targets[0].slice.lower);
            high = _format(node.targets[0].slice.upper);
            return "let "+arr+" = update_slice "+ arr + " " + low +" " + high + " " +_format(node.value)+_sep(top)
        if isinstance(node, Assign):
            vs = [_format(x,top) for x in node.targets]
            sep = _sep(top)
            if (len(vs) == 1):
                return "let "+vs[0]+" = "+_format(node.value)+sep
            else:
                return "let "+_tuple(vs)+" = "+_format(node.value)+sep
        if isinstance(node, AugAssign):
            v = _format(node.target,top)
            sep = _sep(top)
            return "let "+v+" = "+v+" " + _operator(node.op) + " " + _format(node.value)+sep
        if isinstance(node, BinOp):
            return "(" + _format(node.left) + " " + _operator(node.op) + " " + _format(node.right) + ")"
        if isinstance(node, Compare):           
            return "(" + _format(node.left) + " " + _operator(node.ops) + " " + _format(node.comparators) + ")"
        if isinstance(node, Num):
            return hex(node.n)
        if isinstance(node, Str):
            return "\""+str(node.s)+"\""
        if isinstance(node,FunctionDef):
            vs = [x.arg for x in node.args.args]
            return "let "+node.name+" "+_tuple(vs)+" =\n  "+_format(node.body)+_sep(top)
        if isinstance(node,Return):
            return _format(node.value)
        if isinstance(node,Call):
            vs = [_format(x) for x in node.args]
            return _format(node.func) + " " + _tuple(vs)
        if isinstance(node,Expr):
            return _format(node.value)+";"
        if isinstance(node,Assert):
            return "assert ("+_format(node.test)+");"
        if isinstance(node,Name):
            return node.id
        if isinstance(node,Attribute):
            return _format(node.value) + "." + node.attr
        if isinstance(node,Subscript) and isinstance(node.slice,Index):
            return _format(node.value) + ".[" + _format(node.slice.value) +"]"
        if isinstance(node,Subscript) and isinstance(node.slice,Slice):
            return "slice " + _format(node.value) + " " + _format(node.slice.lower) +" " + _format(node.slice.upper) 
        if isinstance(node,For):
            vs = [_format(x) for x in _lvalues(node.body)]
            acc = _tuple(vs)
            return "repeati (" + _format(node.iter) + ") (fun "+_format(node.target)+" "+acc+" -> " + _format(node.body) + " " + acc + ") " + acc
        if isinstance(node,List):
            return "[ "+ ", ".join(_format(x,top) for x in node.elts)+" ]"
        elif isinstance(node, AST):
            fields = [(a, _format(b)) for a, b in iter_fields(node)]
            rv = '%s(%s' % (node.__class__.__name__, (',\n').join(
                ('%s=%s' % field for field in fields)
                if annotate_fields else
                (b for a, b in fields)
            ))
            if include_attributes and node._attributes:
                rv += fields and ',\n' or ' '
                rv += ', '.join('%s=%s' % (a, _format(getattr(node, a)))
                                for a in node._attributes)
            return rv + ')'
        elif isinstance(node, list):
            return '\n'.join(_format(x,top) for x in node)
        return repr(node)
    if not isinstance(node, AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    return _format(node)


def main(path):
#    print("opening file:",path)
    with open(path, 'r', encoding='utf-8') as py_file:
#        print("opened file:",path)
        code = py_file.read()
        ast = parse(source=code, filename=path)
        print(dump(ast))

if __name__ == "__main__":
    main(argv[1])
