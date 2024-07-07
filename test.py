import ast
import transform


transformer = transform.Transformer695()
node = ast.parse("class Foo[X, Y](Base, keyword=1): pass")

print(ast.unparse(transformer.visit(node)))
