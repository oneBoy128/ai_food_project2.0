import torch
from chromadb import PersistentClient
from transformers import AutoModel,AutoTokenizer
import chromadb

from week5.tools.get_embedding import get_embedding
import re


device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_path = '/home/wby/projects/model/all-MiniLM-L6-v2'
model = AutoModel.from_pretrained(model_path).to(device)

db_path = '/home/wby/projects/week5/chroma_db/chroma_recipe_db'
qwen_model_path = '/home/wby/projects/model/Qwen-7B-Chat'
device = 'cuda' if torch.cuda.is_available() else 'cpu'
#连接数据库
chroma_client = PersistentClient(
    path=db_path,
    settings=chromadb.config.Settings(
        anonymized_telemetry=False,
        allow_reset=False
    )
)


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
collection = chroma_client.get_collection(name='recipe_50w_384d_ver2')

def parse_conditions(query):
    """
    从用户查询中提取条件，比如calories < 200  time > 10 转为Chroma支持的过滤格式
    :param query: 询问的参数
    :return: Chroma过滤字典（如{"Calories": {"$lt": 200}, "TotalTime": {"$gt": 10}}）
    """
    field_mapping = {
        # 键：用户可能输入的关键词（小写）；值：元数据中对应的字段名
        "calorie": "Calories",
        "calories": "Calories",
        "kcal": "Calories",
        "time": "TotalTime",
        "totaltime": "TotalTime",
        "duration": "TotalTime",
        "serving": "RecipeServings",
        "servings": "RecipeServings",
        "portion": "RecipeServings",
        "recipe servings": "RecipeServings",
        "RecipeServings": "RecipeServings",
    }

    # 2. 定义运算符映射：用户输入的符号 → Chroma支持的运算符
    operator_mapping = {
        "<": "$lt",
        "<=": "$lte",
        ">": "$gt",
        ">=": "$gte",
        "=": "$eq",
        "==": "$eq",
        'less than':"$lt",
        'greater than':"$gt",
        'less than or equal to':"$lte",
        'greater than or equal to':"$gte",
        'equal to':"$eq",
    }

    # 3. 用正则表达式提取所有条件（支持多条件，用and连接）
    # 匹配格式：[关键词] [运算符] [数字]（如 "calories < 200"、"time >= 10"）
    pattern = r"(\w+\s*\w*)\s*([<>=]{1,2})\s*(\d+\.?\d*)"
    matches = re.findall(pattern, query.lower())  # 转小写，忽略大小写

    #4. 处理提取到的条件，转换为Chroma格式
    conditions = []
    for match in matches:
        # match = (用户输入关键词, 运算符, 数值)
        user_filed, user_op, value = match

        #首先去除关键词中的空格
        # 去除关键词中的空格（如"total time" → "totaltime"）
        user_filed_clean= user_filed.replace(" ","")
        meta_field = None
        for key in field_mapping:
            if key in user_filed_clean:
                meta_field = field_mapping[key]
                break

        if not meta_field:
            continue #不认识的字段直接跳过

         # 4.2 转换运算符（如"<" → "$lt"）
        chroma_op = operator_mapping.get(user_op,None)
        if not chroma_op:
            continue # 不支持的运算符， 跳过

        try:
            value = float(value)
        except:
            continue  #数值无效，跳过

        conditions.append({meta_field: {chroma_op: value}})

    if len(conditions) == 0:
         return None # 没有条件， 后记组合时chroma会过滤的
    elif len(conditions) == 1:
        return conditions[0] # 单个条件直接返回
    else:
        return {'$and':conditions}


tokenizer =  AutoTokenizer.from_pretrained(model_path,trust_remote_code=True)

def rag_retrieve(query,top_k=3):
    """
    基础的rag函数，根据查询返回最最相似的食谱
    :param query: 用户查询的问题
    :param top_k: 返回前k个最相近的结果
    :tokenizer: allMiniLM的分词器
    :collection: chroma数据库的集合
    :model: allMiniLM
    :device: 'cuda' if torch.cuda.is_available() else 'cpu'
    :return 返回包括食谱信息的列表
    """
    query_emb = get_embedding(query,tokenizer, model,device)

    #添加条件
    filter_conditions = parse_conditions(query)

    resluts = collection.query(
        query_embeddings = [query_emb],
        n_results=top_k,
        include=['metadatas','documents','distances'],
        where= filter_conditions
    )
    """print(f"这是一个测试ids{resluts['ids']}")
    print(f"这是一个测试ids{resluts['distances']}")
    print(f"这是一个测试ids{resluts['metadatas']}")
    print(f"这是一个测试documents{resluts['documents']}")"""
    formatted_resluts = []
    for i,(doc_id,distance,meta, doc_text) in enumerate(zip(
        resluts['ids'][0], resluts['distances'][0],
        resluts['metadatas'][0], resluts['documents'][0]
    )):
        formatted_resluts.append({
            'doc_id': doc_id,
            'distance': distance,
            'meta': meta,
            'text': doc_text
        })
    return formatted_resluts