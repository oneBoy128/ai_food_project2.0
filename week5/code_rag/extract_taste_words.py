import re
#提取口味
def extract_taste_words(query):
    # 1. 定义所有口味相关关键词（包含基础和“偏XX”表达）
    taste_keywords = [
        "sour", "tart", "slightly sour",  # 酸/偏酸
        "sweet", "sugary", "slightly sweet",  # 甜/偏甜
        "bitter", "slightly bitter",  # 苦/偏苦
        "spicy", "hot", "peppery", "slightly spicy", "mildly spicy",  # 辣/偏辣
        "salty", "slightly salty"  # 咸/偏咸
    ]

    # 2. 清理特殊符号，统一转为小写
    query_clean = re.sub(r'[?.,!;<>≤≥]', '', query).strip().lower()

    # 3. 构建正则模式：优先匹配多词短语（如 slightly sour），避免被拆分为单字
    # 按关键词长度（空格数）排序，多词在前，单词在后
    sorted_keywords = sorted(taste_keywords, key=lambda x: len(x.split()), reverse=True)
    # 转义特殊字符，用|拼接，添加单词边界\b确保精准匹配
    pattern = r'\b(' + '|'.join(re.escape(key) for key in sorted_keywords) + r')\b'

    # 4. 提取所有匹配的口味词，去重并保持出现顺序
    matched_tastes = re.findall(pattern, query_clean)
    # 去重（保留首次出现的词）
    seen = set()
    result = []
    for taste in matched_tastes:
        if taste not in seen:
            seen.add(taste)
            result.append(taste)

    return result