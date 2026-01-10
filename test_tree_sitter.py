import tree_sitter_languages

# 测试 get_parser（旧版本 API）
try:
    from tree_sitter_languages import get_parser
    parser = get_parser("java")
    print(f"get_parser('java') 成功!")
    print(f"parser 类型: {type(parser)}")
    
    # 测试解析
    code = b"public class Test {}"
    tree = parser.parse(code)
    print(f"AST 根节点类型: {tree.root_node.type}")
    
except Exception as e:
    print(f"get_parser 测试错误: {e}")
    import traceback
    traceback.print_exc()
