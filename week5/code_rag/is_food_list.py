# 提取一句话中的所有食物相关的单词
import torch
import re

# 1. 核心搭配提取（不变，处理带动作的query）
def extract_core_pair(query):
    food_actions = ["eat", "cook","cooking", "make", "bake", "fry", "prepare", "taste"]
    # 1. 先清理特殊符号（问号、小于号等）
    query_clean = re.sub(r'[?.,!;<>≤≥]', '', query).strip().lower()
    # 2. 过滤“时间/热量”等非食物条件词（关键新增）
    condition_words = ["time", "min", "minute", "hour"]
    for word in condition_words:
        query_clean = re.sub(rf'\b{word}\b\s*[0-9]*', '', query_clean).strip()

    # 3. 提取“动作+食物”核心搭配
    for action in food_actions:
        pattern = rf'\b{action}\b\s*(.*)'
        match = re.search(pattern, query_clean)
        if match:
            core_object = match.group(1).strip()
            stop_words = ["some", "the", "a", "an", "my", "your"]
            for stop in stop_words:
                core_object = re.sub(rf'\b{stop}\b', '', core_object).strip()
            if core_object:
                core_pair = f"{action} {core_object}"
                print(f"🎯 提取核心搭配：[{query}] → [{core_pair}]")
                return core_pair
    return query_clean

def is_food_list(query, qwen_model, qwen_tokenizer):
    """
    基于 QWen-7B 模型，提取查询中的食物名词列表
    :param query: 用户查询（字符串）
    :param qwen_model: 加载好的 QWen-7B 模型
    :param qwen_tokenizer: 加载好的 QWen 分词器
    :return: 食物名词列表（如 ['apple pie']）
    """
    core_query = extract_core_pair(query)
    # 1. 构造提示词模板（替换 {{query}} 为实际用户查询）
    prompt_template = f"""###任务：基于用户的询问，提取话语中的与食物相关的名词（只能提取食物名词, 若没有则返回[]）
    用户查询（query）：{core_query}

    ### 示例：
    1. query = 'i want to cook french fries' 输出：['french fries']
    2. query = 'i want to cook apple pie and orange' 输出：['apple pie' , 'orange']
    3. query = 'i want to make apple pie and Trump' 输出：['apple pie']

    ### 注意事项:
    1. 你只能提取与食物有关的单词。
    2. 不能提取与食物无关的单词（例如人名、地名）
    3. 若没有提取到，你不能乱提取，没有提取到的只能返回空数组[]

    ###输出格式
    请按照以下格式输出：
    ['food1','food2','food3']"""

    # 填充用户查询到提示词中
    #prompt = prompt_template.format(query=query)

    # 2. 用 QWen 分词器处理提示词（适配 QWen 聊天格式）
    inputs = qwen_tokenizer.apply_chat_template(
        [
            {'role':"system", "content": '你是一个专业的吃货，需要从用户的一段话里提取出所有与食物有关的单词'},
            {"role": "user", "content": prompt_template}
        ],  # 按 QWen 要求的聊天格式组织
        add_generation_prompt=True,  # 自动添加模型回复的前缀
        return_tensors="pt"  # 返回 PyTorch 张量
    ).to(qwen_model.device)  # 移到模型所在设备（GPU/CPU）

    # 3. 模型生成结果（控制输出长度，避免冗余）
    with torch.no_grad():  # 禁用梯度计算，节省内存
        outputs = qwen_model.generate(
            inputs,
            max_new_tokens=50,  # 食物列表长度有限，50个token足够
            temperature=0.1,  # 降低随机性，确保输出格式稳定
            top_p=0.9,
            do_sample=False,  # 确定性生成，避免重复结果
            eos_token_id=qwen_tokenizer.eod_id  # 遇到结束符停止生成
        )

    # 4. 解码输出并提取食物列表
    # 提取模型生成的部分（排除输入提示词）
    generated_ids = outputs[:, inputs.shape[1]:]
    raw_output = qwen_tokenizer.decode(generated_ids[0], skip_special_tokens=True).strip()

    # 用正则表达式提取 ['food1','food2'] 格式的内容
    # 匹配单引号/双引号包裹的字符串，支持中英文食物名
    food_pattern = r"['\"]([^'\"]+)['\"]"
    food_list = re.findall(food_pattern, raw_output)

    # 5. 过滤空值（避免模型输出格式异常导致的空元素）
    food_list = [food.strip() for food in food_list if food.strip()]
    print(f"提取出的食物关键词{food_list}")

    return food_list