#优先提取条件，哪怕这个话题不是食物
import re

def parse_conditions_first(query):
    """
    从用户查询中提取条件，比如calories < 200  time > 10 ,哪怕这个话题不是食物
    :param query: 询问的参数
    :return: Chroma过滤字典（如["Calories",'<','200']）
    """
    field_mapping = {
        "calorie": "Calories", "calories": "Calories", "kcal": "Calories",
        "time": "TotalTime", "totaltime": "TotalTime", "duration": "TotalTime",
        "serving": "RecipeServings", "servings": "RecipeServings", "portion": "RecipeServings"
    }
    operator_mapping = {
        "<": "<", "<=": "<=", ">": ">", ">=": ">=", "=": "=", "==": "=",
        'less than': "<", 'greater than': ">", 'less than or equal to': "<=",
        'greater than or equal to': ">=", 'equal to': "="
    }

    pattern = r"(\w+\s*\w*)\s*([<>=]{1,2}|\w+\s+\w+(\s+\w+)?)\s*(\d+\.?\d*)"  # 补充匹配英文运算符（如less than）
    matches = re.findall(pattern, query.lower())
    conditions = []

    for match in matches:
        # 修正：match结构因补充英文运算符变了，取第0个为关键词、第1个为运算符、第3个为数值
        user_filed, user_op, _, value = match
        user_filed_clean = user_filed.replace(" ", "")
        meta_field = None
        for key in field_mapping:
            if key in user_filed_clean:
                meta_field = field_mapping[key]
                break
        if not meta_field:
            continue
        # 处理英文运算符（如"less than"）
        chroma_op = operator_mapping.get(user_op.strip(), None)
        if not chroma_op:
            continue
        conditions.append([meta_field, chroma_op, str(value)])  # 每个条件都是列表

    if len(conditions) == 0:
        return None
    elif len(conditions) >= 1:
        # 修复：初始化合并列表，循环添加后续条件+and
        merged_conditions = conditions[0]  # 先拿第一个条件（列表）
        for cond in conditions[1:]:  # 遍历剩余条件
            merged_conditions += ['and'] + cond  # 列表拼接：[A]+[and]+[B]
        return merged_conditions

