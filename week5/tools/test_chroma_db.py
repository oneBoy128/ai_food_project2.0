from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModel

from week5.tools.get_embedding import get_embedding
from week5.tools.create_chroma import init_chroma

DATA_PATH = Path("/home/wby/projects/week5/data/recipes.csv")
MODEL_PATH = "/home/wby/projects/model/all-MiniLM-L6-v2"

device = 'cuda' if torch.cuda.is_available() else 'cpu' #设备初始化
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True) #allMini分词器初始化
model = AutoModel.from_pretrained(MODEL_PATH, local_files_only=True).to(device) #allMini模型初始化
recipe_collection = init_chroma()
def test_chroma_retrieval(collection, tokenizer, model, device):
    test_query = "Find recipes of Banana Flambe with TotalTime < 30 minutes"
    query_emb = get_embedding(test_query, tokenizer, model, device)

    # 关键：添加where参数，指定筛选条件（只保留TotalTime < 30的食谱）
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=4,
        include=["metadatas", "documents", "distances"],
        where={"TotalTime": {"$lt": 30}}  # $lt表示“小于”，对应查询中的“< 30”
    )

    print("\n=== 检索测试结果 ===")
    for i, (doc_id, distance, meta, doc_text) in enumerate(zip(
        results["ids"][0], results["distances"][0],
        results["metadatas"][0], results["documents"][0]
    )):
        print(f"\n第{i+1}个相似结果：")
        print(f"ID：{doc_id}")
        print(f"相似度：{round(distance, 4)}")
        print(f"食谱名称：{meta['Name']} | 耗时：{meta['TotalTime']}分钟")  # 打印耗时，验证是否符合条件
        print(f"文本内容：{doc_text[:150]}...")

# 调用测试函数
test_chroma_retrieval(recipe_collection, tokenizer, model, device)