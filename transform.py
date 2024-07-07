# A script to transform code which is using PEP-695-like syntax
# to python versions below the 3.12


import ast
from typing import List, TypeVar


def transform_bases(prev_bases: list[ast.AST], type_variables: list[TypeVar]) -> list[ast.AST]:
    if len(type_variables) > 1:
            # For some reason inside of x[y, z] part [y, z] is represented as 
            # slice=Tuple(elts=[x, y])
            # as well as the x[y,]
            # but x[y] is represented as slice=y
            # ...It is what it is.
        slice_ = ast.Tuple(
            elts=[
                ast.Name(
                    id=type_variable.name,
                    ctx=ast.Load(),
                ) for type_variable in type_variables
            ],
            ctx=ast.Load(),
        )
    else:
        slice_ = ast.Name(id=type_variables[0].name, ctx=ast.Load())   
    return prev_bases + [ast.Subscript(value=ast.Name(id='Generic', ctx=ast.Load()), slice=slice_, ctx=ast.Load())]

class Transformer695(ast.NodeTransformer):
    typevars = set()
    need_typing = False

    
    def visit_Module(self, node: ast.Module):
        print(self.need_typing)
        return ast.Module(
            body=[ast.ImportFrom(module='typing', names=[ast.alias(name='Generic'), ast.alias(name='TypeVar')], level=0)] + node.body,
            type_ignores=node.type_ignores,
        )
        
    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        if not node.type_params:
            return node
        self.need_typing = True
        return ast.ClassDef(
               name=node.name,
               bases=transform_bases(node.bases, node.type_params), 
               keywords=node.keywords,
               body=node.body,
               decorator_list=node.decorator_list
        )
   
#tree = ast.parse("class Foo: pass")

#transformer = Transformer695()
#tree = transformer.visit(tree)
#print(ast.dump(tree))
