# document https://docs.python.org/3.9/library/ast.html#compiler-flags
import ast
from ast_utility import iter_child_nodes, my_iter_all
src='''
def forward(self, data):
    x, edge_index = data.x, data.edge_index
    x = self.conv1(x, edge_index)
    x = F.relu(x)
    x = F.dropout(x, training=self.training)
    x = self.conv2(x, edge_index)

    return F.log_softmax(x, dim=1)
'''


ast_node = ast.parse(src, "msg.log", mode="exec")
c_code=my_iter_all(ast_node)
print(c_code)
print(ast.dump(ast_node))