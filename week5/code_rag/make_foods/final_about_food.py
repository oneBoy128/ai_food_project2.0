"""
该模块回答某个具体的美食制作。比如how to make kung pao chicken or how to make ice cream等具体某类或某个食物
"""

import random
import json
import torch
from week5.code_rag.rag_retrieve import rag_retrieve

#构建推荐提示词
prompt_template_food = """
# 立即执行：精准查询并返回食谱信息（绝对禁止多余内容）
用户查询（query）：{{query}}
你的唯一任务：
1. 输出逻辑（非A即B，无第三种可能）：
   - A. 检索结果含相关食谱（如含“kung pao chicken”）：仅输出1个JSON对象，包含且仅包含6个字段（Name、Categories、Total Time、Calories、Ingredients and Quantities、Cooking steps），字段值严格来自检索结果，无任何额外文字；
2. 字段格式铁律：
   - Ingredients and Quantities：每个食材用\\n分隔（如"a:1\\nb:2"），禁止空格/逗号连接；
   - Cooking steps：每个步骤用\\n分隔（如"1. x\\n2. y"），保留原始编号，禁止合并步骤；
   - 所有字段用双引号，无中文，无多余符号（如换行、空格）；
3. 终极禁令：
   - 绝对不允许同时输出A和B；
   - 绝对不允许输出任何解释性文字（如“The query did not return...”）；
   - 绝对不允许重复字段或步骤。

### 可用的RAG检索结果（仅基于此生成）
{{retrieved_results}}

### 输出格式（仅以下两种之一）：
{
    "Name": "{Name}",
    "Categories": "{RecipeCategory}",
    "Total Time": "{TotalTime}",
    "Calories": "{Calories}",
    "Ingredients and Quantities": "ingredient1:amount\\ningredient2:amount\\n...",
    "Cooking steps": "1. Step 1\\n2. Step 2\\n...\\nN. Step N"
}
"""

# 回答具体菜谱
def final_about_food(user_query, model, tokenizer):
    """
    修复后的完整RAG问答函数：解决解码空白问题
    """
    print(f"🔍 正在处理查询：{user_query}")
    # 2. RAG检索（处理空结果）
    rags_list = rag_retrieve(user_query, 1)
    rags_list = rags_list if rags_list else []  # 确保是列表格式
    rags_list_str = json.dumps(rags_list, ensure_ascii=False, indent=2) #转为字符串


    # 4. 填充prompt
    prompt_food = prompt_template_food.replace("{{retrieved_results}}", rags_list_str).replace("{{query}}", user_query)

    # 5. 模型生成（优化参数：提升稳定性）
    with torch.no_grad():
        inputs = tokenizer.apply_chat_template(
            [
                {'role': "system", 'content': '你是专业厨师，严格按JSON格式推荐食谱，回答好这个美食怎么做'},
                {"role": "user", "content": prompt_food}
            ],
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            truncation=True,  # 开启截断（避免输入过长报错）
            max_length=4096   # 适配长RAG结果
        ).to(model.device)

        outputs = model.generate(
            inputs,
            max_new_tokens=1000,
            min_new_tokens=20,  # 确保生成足够内容
            temperature=0.7,     # 适度随机性，兼顾自然和准确
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            attention_mask=torch.ones_like(inputs),
            repetition_penalty=1.2  # 减少重复内容
        )

    # 6. 解码+格式修复（关键：处理JSON格式错误）
    final_answer = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)

    print(f"✅ 结果完成")
    return final_answer