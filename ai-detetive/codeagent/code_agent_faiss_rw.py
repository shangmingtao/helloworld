import faiss
import numpy as np
from langchain_core.documents import Document
from typing import List


def save_documents_to_faiss(documents: List[Document]):
    """
    将文档通过向量模型向量化并存入FAISS索引
    
    Args:
        documents: 待向量化的文档列表，每个Document包含page_content和metadata
    
    Returns:
        None
    """
    if not documents:
        print("警告: 文档列表为空，无需向量化")
        return
    
    # 配置阿里云百炼API
    # TODO: 请在此处设置阿里云百炼API Key
    api_key = "sk-b5f310af8681408dafc4ee99f278c18e"
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 初始化OpenAI客户端 - 使用阿里云百炼的 text-embedding-v4 模型
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)

    def aliyun_embed_texts(texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            # print(f"当前待向量化内容长度： {len(text)}")
            #已知长度19677可以过，已知长度57807不过，还有个长度69242的，编号5642，2.1w，2.3w，3.1w，7w，3.7w
            # if len(text) > 8100:
            #     print(f"当前待向量化内容长度过长，跳过，跳过内容{text}")
            #     continue
            try:
                response = client.embeddings.create(
                    model="text-embedding-v4",
                    input=text
                )
                embeddings.append(response.data[0].embedding)
                print(f"当前已经存入embeddings长度： {len(embeddings)}")
            except Exception as e:
                print(f"当前待向量化内容长度过长，跳过，跳过内容{text}, 长度： {len(text)}，错误信息： {e}")
                continue

        return embeddings
    
    # 提取文档内容
    texts = [doc.page_content for doc in documents]
    
    print(f"开始向量化 {len(documents)} 个文档...")
    
    # 生成向量嵌入
    try:
        embeddings = aliyun_embed_texts(texts)
    except Exception as e:
        print(f"向量生成失败: {e}")
        print("请确保已正确配置阿里云百炼API Key")
        raise
    
    # 将嵌入转换为numpy数组
    vectors = np.array(embeddings, dtype='float32')
    
    # 获取向量维度
    dimension = vectors.shape[1]
    print(f"向量维度: {dimension}")
    
    # 创建FAISS索引 (使用L2距离)
    index = faiss.IndexFlatL2(dimension)
    
    # 将向量添加到索引中
    index.add(vectors)
    
    # 保存索引到文件
    index_file = "../faiss_index.bin"
    faiss.write_index(index, index_file)
    print(f"FAISS索引已保存到: {index_file}")
    
    # 保存文档元数据 (可选，用于后续检索时获取原始文档)
    import pickle
    metadata_file = "../faiss_metadata.pkl"
    with open(metadata_file, 'wb') as f:
        pickle.dump(documents, f)
    print(f"文档元数据已保存到: {metadata_file}")
    
    print(f"成功将 {len(documents)} 个文档存入FAISS索引")


if __name__ == "__main__":
    # 测试示例 - 需要先有documents
    from code_agent_treesitter_ast import vectorize_java_project
    
    # 替换为你的Java项目路径
    # java_project_path = r"C:\Users\shang\Desktop\项目\detective-demo2"
    # java_project_path = r"C:\Users\shang\Desktop\项目code\stock-shop-affair"
    # java_project_path = r"/Users/milo/Desktop/detective/java/detective-demo"
    java_project_path = r"C:\Users\shang\Desktop\detective\java项目code\detective-demo"

    # 生成documents
    print("正在生成documents...")
    documents = vectorize_java_project(java_project_path)
    
    # 存入FAISS
    print("正在存入FAISS...")
    save_documents_to_faiss(documents)
