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
        elif len(vs) == 1:
            return vs[0]
        else:
            return "("+",".join(vs)+")"

    def _curried(vs):
        if len(vs) == 0:
            return ""
        else:
            return " ".join(vs)

    def _curried_args(vs):
        if len(vs) == 0:
            return ""
        else:
            def ty_annot(v):
                if v[1] is None:
                    return v[0]
                else:
                    return "("+v[0] +":"+_format(v[1])+")"
            return " ".join([ty_annot(v) for v in vs])


    def _func(x):
        f = _format(x)
        if f == 'uint8':
           return 'u8' 
        if f == 'uint16':
           return 'u16' 
        if f == 'uint32':
           return 'u32' 
        if f == 'uint64':
           return 'u64' 
        if f == "uint128":
           return "u128"
        if f == "array":
           return "createL"
        if f == "vlarray.length":
           return "length"
        if f == "vlbytes.length":
           return "length"
        if f == "vlarray.split_blocks":
           return "split_blocks"
        if f == "vlbytes.split_blocks":
           return "split_blocks"
        if f == "vlarray.concat_blocks":
           return "concat_blocks"
        if f == "vlbytes.concat_blocks":
           return "concat_blocks"
        if f == "array.copy":
           return "copy"
        if f == "bytes.copy":
           return "copy"
        if f == "vlbytes.copy":
           return "vlcopy"
        if f == "vlarray.copy":
           return "vlcopy"
        if f == "bytes.to_uint32s_le":
           return "uints_from_bytes_le #U32"
        if f == "bytes.from_uint32s_le":
           return "uints_to_bytes_le #U32"
        else:
           return f

    def _is_uintn(x):
        f = _format(x)
        return (f in ['bit','uint8','uint16','uint32','uint64','uint128'])

    def _cast_uintn(x):
        f = _format(x)
        if f == 'uint8':
           return 'u8' 
        if f == 'uint16':
           return 'u16' 
        if f == 'uint32':
           return 'u32' 
        if f == 'uint64':
           return 'u64' 

   
    def _lvalues(node):
        if (isinstance(node, Assign) and
            isinstance(node.value,Call) and
            isinstance(node.value.func,Name) and
            node.value.func.id == 'NewType'):
            return []
        if (isinstance(node, Assign) and
            len(node.targets) == 1 and
            isinstance(node.targets[0],Subscript)):
            return [node.targets[0].value]
        elif isinstance(node, Assign):
            return [x for x in node.targets]
        elif isinstance(node, Subscript):
            return [node.value]
        if (isinstance(node, AugAssign) and
            isinstance(node.target,Subscript)):
            return [node.target.value]
        elif isinstance(node, AugAssign):
            return [node.target]
        elif isinstance(node, list):
            return [x for y in node for x in _lvalues(y)]
        else:
            return []
        
    def _operator(o):
        if isinstance(o,Pow):
            return "**."
        elif isinstance(o,Sub):
            return "-."
        elif isinstance(o,Add):
            return "+."
        elif isinstance(o,Mult):
            return "*."
        elif isinstance(o,BitAnd):
            return "&."
        elif isinstance(o,BitXor):
            return "^."
        elif isinstance(o,Mod):
            return "%."
        elif isinstance(o,Eq):
            return "="
        elif isinstance(o,Gt):
            return ">"
        elif isinstance(o,Lt):
            return "<"
        elif isinstance(o,list) and len(o) == 1:
            return _operator(o[0])
        else:
            return " <unknown_op> "+type(o)

    def _sep(top): 
        if top:
            return " "
        else:
            return " in "

    def _sp(n):
        return " "*n
        
    def _format(node,top=False,ind=0,paren=False):
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
            return _format(node.body,True,ind)
        if isinstance(node, ImportFrom):
            return "open "+node.module.title()
        if (isinstance(node, Assign) and
            isinstance(node.value,Call) and
            isinstance(node.value.func,Name) and
            node.value.func.id == 'NewType'):
            vs = [_format(x,top,ind,paren) for x in node.targets]
            ty = node.value.args[1].id
            nty = vs[0]+"_t"
            return ("type "+nty+" = "+ty+";\n"+
                    _sp(ind)+"let "+vs[0]+" (x:"+ty+") : "+nty+" = x")
        if (isinstance(node, Assign) and
            len(node.targets) == 1 and
            isinstance(node.targets[0],Subscript) and
            isinstance(node.targets[0].slice,Index)) :
            arr = _format(node.targets[0].value,top,ind,paren);
            idx = _format(node.targets[0].slice.value,top,ind,paren);
            return "let "+arr+" = "+ arr+".["+idx+"] <- "+_format(node.value,top,ind,paren)+_sep(top)
        if (isinstance(node, Assign) and
            len(node.targets) == 1 and
            isinstance(node.targets[0],Subscript) and
            isinstance(node.targets[0].slice,Slice)) :
            arr = _format(node.targets[0].value,top,ind,paren);
            low = _format(node.targets[0].slice.lower,top,ind,paren);
            high = _format(node.targets[0].slice.upper,top,ind,paren);
            return "let "+arr+" = update_slice "+ arr + " " + low +" " + high + " " +_format(node.value,top,ind,True)+_sep(top)
        if (isinstance(node, Assign) and
            len(node.targets) == 1 and
            isinstance(node.targets[0],Tuple)):
            vs = [_format(x,top,ind,paren) for x in node.targets[0].elts]
            sep = _sep(top)
            if (len(vs) == 1):
                return "let "+vs[0]+" = "+_format(node.value,top,ind,paren)+sep
            else:
                return "let "+_tuple(vs)+" = "+_format(node.value,top,ind,paren)+sep
        if isinstance(node, Assign):
            vs = [_format(x,top,ind,paren) for x in node.targets]
            sep = _sep(top)
            if (len(vs) == 1):
                return "let "+vs[0]+" = "+_format(node.value,top,ind,paren)+sep
            else:
                return "let "+_tuple(vs)+" = "+_format(node.value,top,ind,paren)+sep
        if isinstance(node, AnnAssign):
            sep = _sep(top)
            return "let "+_format(node.target,top,ind,paren)+" : "+_format(node.annotation,top,ind,paren)+" = "+_format(node.value,top,ind,paren)+sep

        if (isinstance(node, AugAssign) and
            isinstance(node.target,Subscript) and
            isinstance(node.target.slice,Index)) :
            sep = _sep(top)
            arr = _format(node.target.value,top,ind,paren);
            idx = _format(node.target.slice.value,top,ind,paren);
            return "let "+arr+" = "+ arr+".["+idx+"] <- "+  arr+".["+idx+"]" + " " + _operator(node.op) + " " + _format(node.value,ind,paren) + sep

        if isinstance(node, AugAssign):
            v = _format(node.target,top,ind,paren)
            sep = _sep(top)
            return "let "+v+" = "+v+" " + _operator(node.op) + " " + _format(node.value,top,ind,paren)+sep
        if (isinstance(node, BinOp) and
            _operator(node.op) in ["<<",">>"]):
            return "(" + _format(node.left,top,ind,paren) + " " + _operator(node.op) + " " + "(u32 "+_format(node.right,top,ind,paren) + "))"
        if isinstance(node, BinOp):
            return "(" + _format(node.left,top,ind,paren) + " " + _operator(node.op) + " " + _format(node.right,top,ind,paren) + ")"
        if isinstance(node, Compare):           
            return "(" + _format(node.left,top,ind,paren) + " " + _operator(node.ops) + " " + _format(node.comparators,top,ind,paren) + ")"
        if isinstance(node, Num):
            return hex(node.n)
        if isinstance(node, Str):
            return "\""+str(node.s)+"\""
        if isinstance(node,FunctionDef):
            vs = [(x.arg,x.annotation) for x in node.args.args]
            return "let "+node.name+" "+_curried_args(vs)+" : "+_format(node.returns,top,ind,paren)+" =\n"+_sp(ind+2)+_format(node.body,not top,ind + 2,paren)+_sep(top)
        if isinstance(node,Return):
            return _format(node.value,top,ind,paren)
        if (isinstance(node,Call) and _func(node.func) in ["rotate_left","rotate_right"]):
            vs = [_format(x,top,ind,True) for x in node.args]
            if paren == True:
                return "("+_func(node.func)+" "+ vs[0]+" "+"(u32 "+vs[1]+"))"
            else:
                return _func(node.func)+" "+ vs[0]+" "+"(u32 "+vs[1]+")"
        if isinstance(node,Call):
            vs = [_format(x,top,ind,True) for x in node.args]
            if paren == True:
                return "("+_func(node.func) + " " + _curried(vs)+")"
            else:
                return _func(node.func) + " " + _curried(vs)
        if isinstance(node,Expr):
            return _format(node.value,top,ind,paren)+";"
        if isinstance(node,Assert):
            return _sp(ind)+"assert ("+_format(node.test,top,ind,paren)+");"
        if isinstance(node,Name):
            return node.id
        if isinstance(node,Attribute) and _format(node.value,top,ind,paren) == "uint32":
            return node.attr
        if isinstance(node,Attribute) and _format(node.value,top,ind,paren) == "array":
            return node.attr
        if isinstance(node,Attribute):
            return _format(node.value,top,ind,paren) + "." + node.attr
        if isinstance(node,Subscript) and _format(node.value,top,ind,paren) == "array":
            return "array" + " " + _format(node.slice.value,top,ind,paren)
        if isinstance(node,Subscript) and isinstance(node.slice,Index):
            return _format(node.value,top,ind,paren) + ".[" + _format(node.slice.value,top,ind,paren) +"]"
        if isinstance(node,Subscript) and isinstance(node.slice,Slice):
            return "slice " + _format(node.value,top,ind,paren) + " " + _format(node.slice.lower,top,ind,paren) +" " + _format(node.slice.upper,top,ind,paren) 
        if isinstance(node,If) and node.orelse is None:
            vs = [_format(x,top,ind,paren) for x in _lvalues(node.body)]
            acc = _tuple(vs)
            return "let "+acc+" = "+"if (" + _format(node.test,top,ind,paren) + ") then ("+_format(node.body,top,ind,paren)+acc+" ) else "+acc+_sep(top)
        if isinstance(node,If):
            vs = [_format(x,top,ind,paren) for x in _lvalues(node.body)]
            vs += [_format(x,top,ind,paren) for x in _lvalues(node.orelse)]
            acc = _tuple(vs)
            return "let "+acc+" = "+"if (" + _format(node.test,top,ind,paren) + ") then ("+_format(node.body,top,ind,paren)+acc+" ) else ("+_format(node.orelse,top,ind,paren)+acc+")"+_sep(top)
        if isinstance(node,For):
            vs = [_format(x,top,ind,paren) for x in _lvalues(node.body)]
            acc = _tuple(vs)
            return "let "+acc+" = "+"repeati (" + _format(node.iter,top,ind,paren) + ") (fun "+_format(node.target,top,ind,paren)+" "+acc+" -> " + _format(node.body,top,ind,paren) + " " + acc + ") " + acc + _sep(top)
        if isinstance(node,List):
            return "[ "+ "; ".join(_format(x,top,ind,paren) for x in node.elts)+" ]"
        elif isinstance(node, AST):
            fields = [(a, _format(b,not top,ind,paren)) for a, b in iter_fields(node)]
            rv = '%s(%s' % (node.__class__.__name__, (',\n'+_sp(ind)).join(
                ('%s=%s' % field for field in fields)
                if annotate_fields else
                (b for a, b in fields)
            ))
            if include_attributes and node._attributes:
                rv += fields and ',\n' or ' '
                rv += ', '.join('%s=%s' % (a, _format(getattr(node, a),top,ind,paren))
                                for a in node._attributes)
            return rv + ')'
        elif isinstance(node, list):
            return ('\n'+_sp(ind)).join(_format(x,top,ind,paren) for x in node)
        return repr(node)
    if not isinstance(node, AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    return _format(node)

import ntpath
def main(path):
#    print("opening file:",path)
    with open(path, 'r', encoding='utf-8') as py_file:
#        print("opened file:",path)
        code = py_file.read()
        ast = parse(source=code, filename=path)
        print("module",ntpath.splitext(ntpath.basename(path))[0].title())
        print('#set-options "--z3rlimit 20 --max_fuel 0"')
        print("open Spec.Lib.IntTypes")
        print("open Spec.Lib.IntSeq")
        print(dump(ast))

if __name__ == "__main__":
    main(argv[1])
