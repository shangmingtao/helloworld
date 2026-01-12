import os
from langchain_core.documents import Document
from tree_sitter import Parser
from tree_sitter_languages import get_language


def load_code_bytes(file_path: str) -> bytes:
    with open(file_path, "rb") as f:
        return f.read()


def extract_class_name(node, code_bytes: bytes) -> str:
    """提取Java类名"""
    for child in node.children:
        if child.type == "identifier":
            start, end = child.start_byte, child.end_byte
            return code_bytes[start:end].decode("utf-8")
    return None


def extract_method_name(node, code_bytes: bytes) -> str:
    """提取Java方法名"""
    for child in node.children:
        if child.type == "identifier":
            start, end = child.start_byte, child.end_byte
            return code_bytes[start:end].decode("utf-8")
    return None


def extract_field_name(node, code_bytes: bytes) -> str:
    """提取Java字段名"""
    for child in node.children:
        if child.type == "variable_declarator":
            for subchild in child.children:
                if subchild.type == "identifier":
                    start, end = subchild.start_byte, subchild.end_byte
                    return code_bytes[start:end].decode("utf-8")
        elif child.type == "identifier":
            start, end = child.start_byte, child.end_byte
            return code_bytes[start:end].decode("utf-8")
    return None


def extract_interface_name(node, code_bytes: bytes) -> str:
    """提取Java接口名"""
    for child in node.children:
        if child.type == "identifier":
            start, end = child.start_byte, child.end_byte
            return code_bytes[start:end].decode("utf-8")
    return None


def is_java_file(file_path: str) -> bool:
    """判断是否为Java文件"""
    return file_path.endswith(".java")


def walk_tree(node, code_bytes: bytes, file_path: str, documents: list, class_stack: list, interface_stack: list, enum_stack: list):
    """遍历AST树，提取代码片段"""
    
    # 处理类定义
    if node.type == "class_declaration":
        class_name = extract_class_name(node, code_bytes)
        class_stack.append(class_name)
        
        # 将整个类定义也作为一个document
        start, end = node.start_byte, node.end_byte
        class_code = code_bytes[start:end].decode("utf-8", errors="ignore")
        
        documents.append(
            Document(
                page_content=class_code,
                metadata={
                    "file_path": file_path,
                    "language": "java",
                    "chunk_type": "class",
                    "class_name": class_name,
                    "interface_name": interface_stack[-1] if interface_stack else None,
                    "enum_name": enum_stack[-1] if enum_stack else None,
                    "start_line": node.start_point[0] + 1,
                    "end_line": node.end_point[0] + 1,
                }
            )
        )
    
    # 处理接口定义
    if node.type == "interface_declaration":
        interface_name = extract_interface_name(node, code_bytes)
        interface_stack.append(interface_name)
        
        # 将整个接口定义也作为一个document
        start, end = node.start_byte, node.end_byte
        interface_code = code_bytes[start:end].decode("utf-8", errors="ignore")
        
        documents.append(
            Document(
                page_content=interface_code,
                metadata={
                    "file_path": file_path,
                    "language": "java",
                    "chunk_type": "interface",
                    "class_name": class_stack[-1] if class_stack else None,
                    "interface_name": interface_name,
                    "enum_name": enum_stack[-1] if enum_stack else None,
                    "start_line": node.start_point[0] + 1,
                    "end_line": node.end_point[0] + 1,
                }
            )
        )

    # 处理枚举定义
    if node.type == "enum_declaration":
        for child in node.children:
            if child.type == "identifier":
                start, end = child.start_byte, child.end_byte
                enum_name = code_bytes[start:end].decode("utf-8")
                enum_stack.append(enum_name)

                # 将整个枚举定义也作为一个document
                start, end = node.start_byte, node.end_byte
                enum_code = code_bytes[start:end].decode("utf-8", errors="ignore")

                documents.append(
                    Document(
                        page_content=enum_code,
                        metadata={
                            "file_path": file_path,
                            "language": "java",
                            "chunk_type": "enum",
                            "class_name": class_stack[-1] if class_stack else None,
                            "interface_name": interface_stack[-1] if interface_stack else None,
                            "enum_name": enum_name,
                            "start_line": node.start_point[0] + 1,
                            "end_line": node.end_point[0] + 1,
                        }
                    )
                )
                break

    # 处理方法定义
    if node.type == "method_declaration":
        start, end = node.start_byte, node.end_byte
        method_code = code_bytes[start:end].decode("utf-8", errors="ignore")
        method_name = extract_method_name(node, code_bytes)
        
        documents.append(
            Document(
                page_content=method_code,
                metadata={
                    "file_path": file_path,
                    "language": "java",
                    "chunk_type": "method",
                    "function_name": method_name,
                    "class_name": class_stack[-1] if class_stack else None,
                    "interface_name": interface_stack[-1] if interface_stack else None,
                    "enum_name": enum_stack[-1] if enum_stack else None,
                    "start_line": node.start_point[0] + 1,
                    "end_line": node.end_point[0] + 1,
                }
            )
        )

    # # 处理字段声明
    # if node.type == "field_declaration":
    #     start, end = node.start_byte, node.end_byte
    #     field_code = code_bytes[start:end].decode("utf-8", errors="ignore")
    #     field_name = extract_field_name(node, code_bytes)
    #
    #     documents.append(
    #         Document(
    #             page_content=field_code,
    #             metadata={
    #                 "file_path": file_path,
    #                 "language": "java",
    #                 "chunk_type": "field",
    #                 "field_name": field_name,
    #                 "class_name": class_stack[-1] if class_stack else None,
    #                 "interface_name": interface_stack[-1] if interface_stack else None,
    #                 "enum_name": enum_stack[-1] if enum_stack else None,
    #                 "start_line": node.start_point[0] + 1,
    #                 "end_line": node.end_point[0] + 1,
    #             }
    #         )
    #     )

    # 处理构造函数
    if node.type == "constructor_declaration":
        start, end = node.start_byte, node.end_byte
        constructor_code = code_bytes[start:end].decode("utf-8", errors="ignore")
        
        # 构造函数名通常与类名相同
        constructor_name = extract_method_name(node, code_bytes)
        
        documents.append(
            Document(
                page_content=constructor_code,
                metadata={
                    "file_path": file_path,
                    "language": "java",
                    "chunk_type": "constructor",
                    "function_name": constructor_name,
                    "class_name": class_stack[-1] if class_stack else None,
                    "interface_name": interface_stack[-1] if interface_stack else None,
                    "enum_name": enum_stack[-1] if enum_stack else None,
                    "start_line": node.start_point[0] + 1,
                    "end_line": node.end_point[0] + 1,
                }
            )
        )
    
    # 递归遍历子节点
    for child in node.children:
        walk_tree(child, code_bytes, file_path, documents, class_stack, interface_stack, enum_stack)
    
    # 弹出栈
    if node.type == "class_declaration":
        class_stack.pop()
    if node.type == "interface_declaration":
        interface_stack.pop()
    if node.type == "enum_declaration":
        enum_stack.pop()


def process_java_file(file_path: str, parser) -> list:
    """处理单个Java文件"""
    if not is_java_file(file_path):
        return []
    
    code_bytes = load_code_bytes(file_path)
    tree = parser.parse(code_bytes)
    root = tree.root_node
    
    documents = []
    class_stack = []
    interface_stack = []
    enum_stack = []
    
    walk_tree(root, code_bytes, file_path, documents, class_stack, interface_stack, enum_stack)
    
    return documents


def vectorize_java_project(project_path: str) -> list:
    """
    对Java项目进行向量化存储
    
    Args:
        project_path: Windows文件夹路径，包含Java项目代码
    
    Returns:
        documents: 向量化后的文档列表，每个Document包含代码内容和元数据
    """
    # 初始化Java解析器 - tree-sitter-languages 1.10.2 使用 Language 类
    try:
        java_language = get_language("java")
        parser = Parser()
        parser.set_language(java_language)
    except ImportError:
        # 降级方案：尝试使用旧API
        from tree_sitter_languages import get_parser
        parser = get_parser("java")
    
    documents = []
    
    # 遍历项目文件夹中的所有Java文件
    for root_dir, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith(".java"):
                file_path = os.path.join(root_dir, file)
                file_documents = process_java_file(file_path, parser)
                documents.extend(file_documents)
    
    return documents


# 使用示例
if __name__ == "__main__":
    # 替换为你的Java项目路径
    # java_project_path = r"C:\Users\shang\Desktop\项目\detective-demo2"
    # java_project_path = r"/Users/milo/Desktop/detective/java/detective-demo"
    java_project_path = r"C:\Users\shang\Desktop\detective\java\detective-demo"

    # 进行向量化
    documents = vectorize_java_project(java_project_path)
    
    # 输出结果
    print(f"共生成 {len(documents)} 个文档")
    new_documents = documents
    for i, doc in enumerate(documents[:50], 1):  # 只打印前5个作为示例
        print(f"\n--- 文档 {i} ---")
        print(f"类型: {doc.metadata.get('chunk_type')}")
        print(f"文件路径: {doc.metadata.get('file_path')}")
        print(f"类名: {doc.metadata.get('class_name')}")
        print(f"方法/字段名: {doc.metadata.get('function_name') or doc.metadata.get('field_name')}")
        print(f"行号: {doc.metadata.get('start_line')}-{doc.metadata.get('end_line')}")
        print(f"总行数: {doc.metadata.get('end_line')-doc.metadata.get('start_line')}")
        print(f"代码长度: {len(doc.page_content)}")
        # print(f"生成的documents长度: {len(doc)}")
        print(f"代码预览: {doc.page_content[:200000]}...")
