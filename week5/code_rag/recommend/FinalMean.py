"""
该模块是判定用户需要什么样的推荐（第三层滤网）
根据食材？
根据菜系特点？
根据特殊场景？

"""
import torch


#最后滤网的提示词
final_mean_propmt = """
输入: {{user_query}}
任务：仅输出1个标签（ingredient/scene/cuisine_feature），多一个字都错！
判定规则：
1. 输入不含"i have" → 绝对不能输出ingredient
2. 输入是“在某个地点/活动吃什么” → 输出scene（比如ride/journey/visit都是活动）
3. 其他情况 → 输出cuisine_feature
示例：
- "food for a hot air balloon ride" → scene
- "recommend gluten-free meals" → cuisine_feature
仅输出标签，无任何额外内容！
"""


def FinalMean(user_query,model,tokenizer):
    """
    判定用户意图，是根据食材来推荐食谱还是根据菜系或特点来推荐食谱还是根据特殊场景来推荐？
    params:
    user_query:用户问题
    model:就是qwen_mode
    tokenizer: 就是qwen_tokenizer
    """
    user_query_lower = user_query.lower()
    final_prompt = final_mean_propmt.replace("{{user_query}}", user_query)

    # 步骤1：规则优先（原逻辑不变）
    if "i have" in user_query_lower:
        return "ingredient"
    scene_keywords = {
        'school', 'outside', 'picnic', 'office', 'party','camping', 'road trip','hiking trip',
        'late-night study session', 'boat trip', 'weekend getaway', 'rooftop dinner',
        'dormitory cooking', 'backpacking', 'music festival', 'early morning commutes',
        'hiking', 'bbq', 'camping trip', 'study session', 'getaway', 'rooftop', 'dormitory', 'overtime',
        'exercise', 'workout', 'beach picnic', 'family picnic','dormitories'
    }
    if any(keyword in user_query_lower for keyword in scene_keywords):
        return "scene"
    cuisine_keywords = {'chinese', 'low cal', 'low calorie', 'fast food', 'spicy', 'weight loss',
                       'vegan', 'no-cook', 'easy-to-carry', 'gluten-free', 'authentic', 'nutritious',
                       'easy-to-make', 'traditional', 'protein-rich', 'low-carb', 'mild-flavored',
                       'recipe', 'prepare', 'quick', 'creamy', 'suitable for eating after'}
    if any(keyword in user_query_lower for keyword in cuisine_keywords):
        return "cuisine_feature"

    # 步骤2：模型调用（原逻辑不变）
    with torch.no_grad():
        inputs = tokenizer.apply_chat_template(
            [
                {'role': "system", 'content': """
                你是只会输出3个标签的机器，必须遵守：
                    1. 只输出1个标签，绝不能输出2个；
                    2. 不含"i have"，绝对不能输出ingredient；
                    3. 输出后立刻停止，不加任何字、符号、换行。
                    """
                },
                {"role": "user", "content": final_prompt}
            ],
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)

        outputs = model.generate(
            inputs,
            max_new_tokens=5,
            temperature=0.0,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    # 步骤3：优化输出处理（关键修改：格式清洗+判定纠错）
    final_answer = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True).strip()

    # 3.1 格式清洗：先去除换行、###、空格（保留字母，包括output后缀）
    clean_answer = final_answer.replace('\n', '').replace('###', '').replace(' ', '').lower()

    #截断犯人的子串
    if 'output' in clean_answer:
        clean_answer = clean_answer.replace('output','')

    print(f"大模型输出{clean_answer}")
    # 3.2 标签提取：兼容“标签+output”格式，精准匹配核心标签
    valid_labels = {'ingredient', 'cuisine_feature', 'scene'}
    correct_label = None
    # 遍历有效标签，只要clean_answer包含标签（不管后面有没有output），就提取
    for label in valid_labels:
        if label in clean_answer:
            correct_label = label
            break

    # 3.3 最终校验（你的简化逻辑不变）
    if correct_label:
        if correct_label == 'ingredient':
            return "ingredient"  # 无i have，强制修正
        if correct_label == 'scene':
            return 'scene'
        return correct_label
    else:
        return "cuisine_feature"