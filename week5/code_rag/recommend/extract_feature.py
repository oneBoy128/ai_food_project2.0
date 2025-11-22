import re
import torch

prompt_template = """
# 任务：从用户查询中抽象出食物特征，输出特征数组（无特征则输出空数组）
用户查询（query）：{user_query}

# 特征定义（满足任意一类即可）：
1. 口味：spicy、sweet、salty、sour、mild等描述味道的词
2. 属性：low calorie、high protein、fast、short time等描述食物特点的词/短语
3. 隐含特征：weight loss→low calorie、fitness meal→high protein、short preparation time→fast

# 强制规则：
1. 必须输出数组格式，特征用小写，短语用空格连接
2. 无特征则输出空数组，禁止输出任何额外内容
3. 特征不重复，数量1-3个即可（无需过多）

# 示例：
1. Recommend a few weight loss meals → ['low calorie']
2. Do you have any fitness meal recommendations? → ['high protein']
3. Recommend a sweet food with a short preparation time → ['sweet', 'fast']
4. recommend some spicy food → ['spicy']
5. What can I cook for dinner? → []
6. What kind of food is suitable for family picnic? → ['family food']
7. food for watching horror movies alone → ['finger food', 'easy to eat']


# 输出格式：严格按示例，仅数组！例如：['spicy', 'low calorie'] 或 []
"""

def extract_feature(userquery, qwen_model, qwen_tokenizer):
    final_prompt = prompt_template.replace("{user_query}", userquery)

    # 大模型自主提取（无白名单干扰）
    inputs = qwen_tokenizer.apply_chat_template(
        [
            {'role': "system", "content": '严格按示例和规则提取特征，必须输出数组格式！'},
            {"role": "user", "content": final_prompt}
        ],
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(qwen_model.device)

    with torch.no_grad():
        outputs = qwen_model.generate(
            inputs,
            max_new_tokens=30,  # 足够容纳3个特征的数组
            temperature=0.2,  # 适度随机性，保证输出
            do_sample=False,
            eos_token_id=qwen_tokenizer.eod_id
        )

    # 解析输出（只提取数组内的特征）
    raw_output = qwen_tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True).strip().lower()
    # 提取引号内的所有特征
    features = re.findall(r'[\'\"]([a-z\-\s]+)[\'\"]', raw_output)
    # 清理（去空、去重）
    features = [feat.strip() for feat in features if feat.strip()]
    features = list(set(features))[:3]  # 最多保留3个，避免冗余

    print(f"提取的食物特征：{features or '[]'}")
    return features