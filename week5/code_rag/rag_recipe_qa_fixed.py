#根据食材回答用户
import torch
import chromadb

from week5.code_rag.build_recipe_prompt import build_recipe_prompt
from week5.code_rag.is_food_query_final_solution import is_food_query_final_solution
from week5.code_rag.rag_retrieve import rag_retrieve
from chromadb import PersistentClient
from week5.tools.tokenizer_loader import tokenizer_loader
from week5.code_rag.parse_conditions_first import parse_conditions_first
from week5.code_rag.extract_taste_words import extract_taste_words
from week5.code_rag.is_food_list import is_food_list

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

#加载qwen_7B的分词器
qwen_tokenizer = tokenizer_loader(qwen_model_path)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
collection = chroma_client.get_collection(name='recipe_50w_384d_ver2')

rag_name_lists = []
rag_lists = []

#过滤函数，过滤出提取的哪些单词是食物
def filter_list(result_list, qwen_model, qwen_tokenizer):
    print(result_list)
    final_results = []
    for result in result_list:
        if is_food_query_final_solution(result, qwen_model, qwen_tokenizer) == 'YES':
            final_results.append(result)
    return final_results

# 去重
def del_same(arrlist):
    seen = set()
    result = []
    for arr in arrlist:
        if arr not in seen:
            seen.add(arr)
            result.append(arr)
    return result


def rag_recipe_qa_fixed(user_query,model, tokenizer, prompt_template, top_k=3):
    """
    修复后的完整RAG问答函数：解决解码空白问题
    """
    print(f"🔍 正在处理查询：{user_query}")
    # 1. 检索结果（不变）
    #提取一句话中食物的单词
    test_list = extract_taste_words(user_query)
    result_list = is_food_list(user_query, model, tokenizer)
    filtered_results = del_same(test_list+result_list)
    print(f"过滤后的数组{filtered_results}")
    querystr = ' '.join(filtered_results)
    print(f"过滤后的结果{querystr}")
    retrieved_results = rag_retrieve(query=querystr, top_k=top_k)

    for i in range(len(retrieved_results)):
        rag_name_lists.append(retrieved_results[i]['meta']['Name'])
        rag_lists.append(retrieved_results[i])
    if not retrieved_results:
        return "抱歉，暂时没有找到符合您需求的美食"

    # 2. 拼接提示词（不变）
    final_prompt = build_recipe_prompt(
        query=user_query,
        retrieved_results=retrieved_results,
        prompt_template=prompt_template
    )
    # 3. 模型生成：关键修改——增大max_new_tokens，关闭截断
    with torch.no_grad():
        inputs = tokenizer.apply_chat_template(
            [   {'role':"system",'content':'你是一个专业的厨师，向用户推荐你的食谱, 并且你能详细的有逻辑的描述你的理由'},
                {"role": "user", "content": final_prompt}
            ],
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)

        # 关键修改：max_new_tokens设为800（足够生成完整推荐），加eos_token_id避免无意义生成
        outputs = model.generate(
            inputs,
            max_new_tokens=2000,  # 从500增至800，确保生成完整
            min_new_tokens=50,   # 强制生成至少50个token（避免太短）
            temperature=0.6,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,  # 遇到结束符停止，避免冗余
            attention_mask=torch.ones_like(inputs)
        )

    # 修复解码：即使有特殊token，也先保留原始文本再过滤
    final_answer = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)


    print(f"\n🎉 最终过滤后回答：\n{final_answer}")
    print(type(final_answer))
    return final_answer if final_answer.strip() else "模型已生成内容，但需调整解码逻辑（见原始内容）"