"""
该模块是根据菜系_特点推荐的总模块, 该模块功能包括:
    1. 调用main_combine_cuisine_feature进行菜系词、特征词的提取以及特点词的翻译以及最终的合并.
    2. 调用RAG检索，随机返回3个检索结果.
    3. 调用大模型回答用户问题.
"""

import random
import json
import torch

from week5.code_rag.recommend.main_combine_cuisine_feature import main_combine_cuisine_feature
from week5.code_rag.rag_retrieve import rag_retrieve
from week5.code_rag.recommend.rag_recipe_qa_fixed import rag_name_lists,rag_lists


#构建推荐提示词
prompt_template_recommend = """
# 立即执行：基于检索结果推荐食谱（理由需自然改写,理由需包含检索数据中的 1 个具体食材或步骤。禁止生硬复制）
用户查询（query）：{{query}}
你的唯一任务：
1. 每个推荐必须包含**固定字段名（严格大小写！）**："doc_id"、"Name"、"Calories"、"Total Time"、"Reason"、"taste"（缺一不可！）；
2. 重点：推荐理由需满足以下2点（这是关键）：
   a. 信息来源：基于检索结果的text字段（如食材、步骤特点、口感相关描述），禁止编造任何未提及的内容（如没提“低糖”就不能说）；
   b. 语言创作：不能生硬复制text原文，要把text信息和用户需求（香蕉、时间<30分钟）结合，用自然的英文重新组织（比如把“premash the banana”改成“you can premash the banana in advance for easier mixing”）；
3. 最终回答用英文，只输出推荐列表（至少1个最多3个,尽量3个，如果一个都没有则输出没有推荐的食谱），不输出模板文字或多余内容。
4. "taste"字段必须填（从列表选：sour/sweet/bitter/spicy/salty/略XX），不能为空！

### 可用的RAG检索结果(若不符合用户提问的菜谱，你可以根据你自己的数据库来推荐你的食谱, 不可以说不知道！请根据你个人数据库回答)
{{retrieved_results}}

### 输出格式（字段名大小写错/漏字段直接无效！）
仅输出以下JSON数组，**禁止添加任何其他文字、代码、注释**，输出后立即停止：
[
{   
    "doc_id": "{doc_id}",
    "Name": "{Name}",
    "Calories": {Calories},
    "Total Time": "{TotalTime}",
    "Reason": "自然改写的理由",
    "taste": "指定口味"
}
]
"""

# 根据特点进行推荐
def final_recommend(user_query, model, tokenizer):
    """
    修复后的完整RAG问答函数：解决解码空白问题
    """
    print(f"🔍 正在处理查询：{user_query}")
    # 1. 解析用户需求（菜系+特征翻译）
    result = main_combine_cuisine_feature(user_query, model, tokenizer)
    # 2. RAG检索（处理空结果）
    rags_list = rag_retrieve(result, 8)
    rags_list = rags_list if rags_list else []  # 确保是列表格式

    # 3. 随机选3个（适配空列表/短列表）
    sample_count = min(3, len(rags_list))
    random_3 = random.sample(rags_list, sample_count) if sample_count > 0 else []
    random_3_str = json.dumps(random_3, ensure_ascii=False, indent=2)

    for i in range(len(random_3)):
        rag_name_lists.append(random_3[i]['meta']['Name'])
        rag_lists.append(random_3[i])

    # 4. 填充prompt
    prompt_recommend = prompt_template_recommend.replace("{{retrieved_results}}", random_3_str).replace("{{query}}", user_query)

    # 5. 模型生成（优化参数：提升稳定性）
    with torch.no_grad():
        inputs = tokenizer.apply_chat_template(
            [
                {'role': "system", 'content': '你是专业厨师，严格按JSON格式推荐食谱，满足用户所有核心需求，理由自然详细，口味符合指定选项'},
                {"role": "user", "content": prompt_recommend}
            ],
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            truncation=True,  # 开启截断（避免输入过长报错）
            max_length=4096   # 适配长RAG结果
        ).to(model.device)

        outputs = model.generate(
            inputs,
            max_new_tokens=2000,
            min_new_tokens=100,  # 确保生成足够内容
            temperature=0.7,     # 适度随机性，兼顾自然和准确
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            attention_mask=torch.ones_like(inputs),
            repetition_penalty=1.2  # 减少重复内容
        )

    # 6. 解码+格式修复（关键：处理JSON格式错误）
    final_answer = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)

    """# 7. 简单格式校验（避免明显错误）
    try:
        # 尝试解析JSON，若失败返回友好提示
        json.loads(final_answer)
    except json.JSONDecodeError:
        # 修复常见格式问题（如缺少逗号、多余逗号）
        final_answer = re.sub(r',\s*]', ']', final_answer)  # 去掉列表末尾多余逗号
        final_answer = re.sub(r'\n\s*,', ',', final_answer)  # 修复换行后的多余逗号
        try:
            json.loads(final_answer)
        except:
            final_answer = '[{"Name":"out put error please try again","Calories":"","Total Time":"","Reason":"Failed to generate valid recipes","taste":""}]'"""

    print(f"✅ 推荐生成完成")
    return (final_answer, rag_lists) if final_answer.strip() else "模型已生成内容，但需调整解码逻辑（见原始内容）"