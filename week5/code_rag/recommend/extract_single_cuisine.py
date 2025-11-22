import re
import torch

# 高频菜系白名单（兜底用）
COMMON_CUISINES = {
    'chinese', 'sichuan', 'cantonese', 'yunnan', 'shandong', 'chongqing', 'xinjiang',
    'hunan', 'taiwanese', 'guizhou', 'macanese', 'tibetan',
    'japanese', 'italian', 'french', 'indian', 'mexican', 'thai', 'korean', 'american',
    'english', 'burmese', 'australian', 'new zealand', 'german', 'vietnamese',
    'korea', 'germany', 'vietnam'
}

prompt_template = """
# 任务：从用户查询中提取**唯一1个核心菜系**（国家/地区/地方饮食名）
用户查询（query）：{user_query}

# 规则：
1. 优先提取第一个出现的核心菜系（如Hunan和Sichuan，先提hunan）
2. 仅输出1个小写单词，非菜系词/无菜系则输出空
3. 禁止输出xinjiang（除非查询含该词）、禁止输出任何符号/换行/乱码

# 输出格式：仅1个纯单词（无符号、无换行）或空，无任何额外内容！
"""


def extract_single_cuisine(userquery, qwen_model, qwen_tokenizer):
    """
    提取用户菜系函数
    params:
    userquery:用户询问问题
    qwen_model:千问大模型
    qwen_tokenizer: 千问大模型分词器

    """
    user_input = userquery.lower()
    final_prompt = prompt_template.replace("{user_query}", userquery)

    # 步骤1：大模型优先提取
    inputs = qwen_tokenizer.apply_chat_template(
        [
            {'role': "system", "content": '严格按规则提取，仅输出纯单词，无符号/换行/乱码，非菜系输出空'},
            {"role": "user", "content": final_prompt}
        ],
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(qwen_model.device)

    with torch.no_grad():
        outputs = qwen_model.generate(
            inputs,
            max_new_tokens=4,  # 仅允许1个单词长度
            temperature=0.0,  # 完全确定性输出，减少乱码
            do_sample=False,
            eos_token_id=qwen_tokenizer.eod_id
        )

    # 解码并清理输出（关键步骤：剔除乱码和多余字符）
    raw_output = qwen_tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True).strip().lower()
    # 1. 过滤乱码（保留字母、空格，剔除其他特殊字符）
    clean_output = re.sub(r'[^\a-z\s]', '', raw_output)
    # 2. 只保留第一个单词（避免多词输出）
    clean_output = clean_output.split()[0] if clean_output.strip() else ""
    # 3. 过滤非菜系词和错误输出
    non_cuisine_pattern = r'(gluten|low|tomato|weight|soup|cal|free|loss|breakfast|lunch)'
    if re.search(non_cuisine_pattern, clean_output) or (clean_output == 'xinjiang' and 'xinjiang' not in user_input):
        clean_output = ""

    # 大模型提取成功（纯单词+有效菜系），直接返回
    if clean_output:
        print(f"大模型提取：{clean_output}")
        return clean_output

    # 步骤2：大模型提取失败，白名单兜底（按出现顺序取第一个）
    print(f"大模型未提取到，白名单兜底匹配")
    for cuisine in COMMON_CUISINES:
        if re.search(rf'\b{cuisine}\b', user_input):
            result = 'korean' if cuisine == 'korea' else cuisine
            print(f"白名单匹配：{result}")
            return result

    # 均未匹配，返回None
    print(f"无匹配菜系：None")
    return None