import ast
from _ast import AST
from sre_constants import ASSERT
def iter_fields(node):
    """
    Yield a tuple of ``(fieldname, value)`` for each field in ``node._fields``
    that is present on *node*.
    """
    for field in node._fields:
        try:
            yield field, getattr(node, field)
        except AttributeError:
            pass


def iter_child_nodes(node):
    """
    Yield all direct child nodes of *node*, that is, all fields that are nodes
    and all items of fields that are lists of nodes.
    """
    for name, field in iter_fields(node):
        if isinstance(field, AST):
            yield field
        elif isinstance(field, list):
            for item in field:
                if isinstance(item, AST):
                    yield item

def my_iter_all(node,annotate_fields=True):
    c_code=''
    for fd in node._fields:
        if fd == 'type_ignores':
            return c_code
        if fd == 'body':
            if len(node.body)>1:
                print("Body has %d instances" %(len(node.body)))
            else:
                if isinstance(node.body[0],ast.FunctionDef):
                    c_code += stmt_FunctionDef(node.body[0])
        # if isinstance(fd,list):
        #     return fd
        # else:
        #     result=my_iter_all(fd)
        #     c_code += result
    return c_code

def read_func_args(args):
    arglist=''
    for i in args:
        if i.arg=='self':
            # 'self' is not useful in C
            continue
        else:
            if arglist!='':
                arglist+=','
            arglist+=(i.arg)
    return arglist


def expr_call(node):
    func_name=node.func.attr
    args=''
    for a in node.args:
        if args!='':
            args+=','
        args+=recursive_value(a)
    for k in node.keywords:
        if args!='':
            args+=','
        args+=str(k.value.value) # TODO: remember to add keyword feature when passing an arg to a func
    return '%s(%s)'%(func_name,args)

def recursive_value(arg):
    name=''
    if 'value' in arg._fields:
        name=recursive_value(arg.value)
    else:
        return arg.id
    return name+'.'+arg.attr


def stmt_assign(node):
    stmt=''
    target=[]
    value=[]
    try:
        for i in node.targets[0].elts:
            target.append(recursive_value(i))
    except AttributeError:
        target.append(recursive_value(node.targets[0]))
    if isinstance(node.value,ast.Tuple):
        try:
            for i in node.value.elts:
                value.append(recursive_value(i))
        except AttributeError:
            value.append(recursive_value(node.value))
    elif isinstance(node.value,ast.Call):
        value.append(expr_call(node.value))
    for t,v in zip(target,value):
        stmt += '%s=%s;\n '%(t,v)
    return stmt
        
def stmt_return(node):
    retrun_stmt='return '
    if isinstance(node.value,ast.Call):
        temp = expr_call(node.value)
    return retrun_stmt+temp+';'

def stmt_FunctionDef(node):
    # function name
    func_name = node.name
    # todo: to add read args function.
    func_args = read_func_args(node.args.args)
    body=''
    for i in node.body:
        if isinstance(i,ast.Assign):
            body+=stmt_assign(i)
        if isinstance(i,ast.Return):
            body+=stmt_return(i)
    if node.decorator_list != []:
        assert False,'To implement later.'
    if node.type_comment is not None:
        assert False,'To implement later.'
    function_format='double %s(%s){\n%s\n}'%(func_name,func_args,body)
    return function_format
            
