import re
import torch

JUDGE_PROMPT_TEMPLATE = """
用户输入: {{user_query}}

# 任务
仅输出YES或NO，判定是否为美食相关话题（包括：可食用的食物/食材/菜系/料理/昆虫，制作方法，饮食需求/营养推荐，食材搭配）。

# 关键示例（必须参考）
✅ YES：
- how to make Sichuan cuisine（川菜是食物）
- Italian dishes（意大利菜是食物）
- How to cook insect（昆虫可食用）
- make ice cream（制作食物）
- bake pizza（烤披萨）
- 30 minute kwai（快手菜）
- high-protein low-carb foods（高蛋白低碳水食物推荐）
- vegan dishes under 300 calories（低卡素食推荐）
- food for post-workout recovery（健身后食物）

❌ NO：
- 不可食用的人/物（如trump、phone、stone、rock）
- 与食物无关的内容（如how are you）
- 与食物无关的闲聊/情绪发泄（无食物核心词）

只输出YES或NO！
"""

def is_food_query_final_solution(userquery, model, tokenizer):
    # 步骤1：清理情绪词/脏话，保留核心语义
    dirty_words = {'fuck', 'ass', 'shit', 'bitch', 'hate', 'omfg'}
    userquery_clean = userquery.strip().lower()
    for word in dirty_words:
        userquery_clean = re.sub(rf'\b{word}\b', '', userquery_clean)
    userquery_clean = re.sub(r'\s+', ' ', userquery_clean).strip()
    userquery_clean = re.sub(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', '', userquery_clean)

    # 步骤2：动作+食物对象规则（补充饮食需求相关动作）
    food_actions = {'make', 'cook', 'eat', 'prepare', 'bake', 'fry', 'crave', 'recommend', 'suggest', 'need'}  # 新增recommend/suggest/need
    food_objects = {
        'ice cream', 'cake', 'dish', 'food', 'meal', 'snack', 'insect', 'bug',
        'pizza', 'rice', 'vegetables', 'quinoa', 'protein', 'carb', 'calories', 'vegan'  # 新增营养术语
    }
    words = userquery_clean.split()
    has_food_action = any(action in words for action in food_actions)
    has_food_object = any(obj in words for obj in food_objects)
    if has_food_action and has_food_object:
        print(f"🔍 动作+食物对象匹配：[{userquery}] → 输出：[YES]")
        return 'YES'

    # 步骤3：弱规则过滤（补充饮食需求/营养关键词）
    clear_food_words = {
        'food', 'meal', 'dish', 'snack', 'ingredient', 'recipe',
        'cuisine', 'cuisines', 'dishes',
        'hungry', 'starving', 'craving',
        'cheesecake', 'chess cake', 'milkshake', 'milk shake',
        'insect', 'edible insect', 'bug', 'edible bug', 'quinoa',
        # 新增饮食需求/营养关键词
        'protein', 'carb', 'carbs', 'calorie', 'calories', 'low-carb', 'high-protein',
        'vegan', 'vegetarian', 'keto', 'diet', 'weight loss', 'post-workout', 'recovery',
        'kung pao', 'picnic'
    }
    clear_non_food_words = {
        'trump', 'biden', 'phone', 'car', 'money', 'computer', 'book', 'stone', 'rock', 'dog',
        'toy car', 'homework', 'doll', 'video game', 'pencil', 'crayon', 'weapon', 'weapons', 'gta5'
    }

    # 关键调整：先判定非食物词，再判定食物词
    if any(word in userquery_clean for word in clear_non_food_words):
        print(f"🔍 明确非食物词匹配：[{userquery}] → 输出：[NO]")
        return 'NO'
    if any(word in userquery_clean for word in clear_food_words):
        print(f"🔍 明确食物词匹配：[{userquery}] → 输出：[YES]")
        return 'YES'

    # 步骤4：模型判定（提示词已补充饮食需求示例）
    judge_prompt = JUDGE_PROMPT_TEMPLATE.replace("{{user_query}}", userquery_clean)
    with torch.no_grad():
        inputs = tokenizer.apply_chat_template(
            [
                {'role':"system", "content": '忽略脏话、情绪词、无关事件，只看核心语义是否为食物/饮食需求/营养推荐；只输出YES/NO'},
                {"role": "user", "content": judge_prompt},
            ],
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)

        outputs = model.generate(
            inputs,
            max_new_tokens=2,
            temperature=0.0,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    raw_output = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True).strip()
    clean_output = re.sub(r'[。.\s]', '', raw_output).upper()
    print(f"🔍 模型核心判定：[{userquery}] → 输出：[{clean_output}]")
    return clean_output