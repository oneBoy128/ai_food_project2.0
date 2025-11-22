import torch

final_template = """
用户输入: {{user_query}}

# 任务
判定用户意图：
- 制作意图（输出true）：仅当用户明确询问“如何做某食物”的具体步骤、方法、流程（必须表达“求教程”的诉求），且含以下制作信号：how to、process、steps、way to、explain how、show me the steps、what steps、prep；
- 推荐意图（输出false）：以下所有情况均为推荐，即使含make/cook也返回false：
  1. 无制作意图（未求步骤），仅询问“选什么食物”“用现有食材能做什么”；
  2. 含推荐信号：need dishes、what should i make、what can i cook、any、recommend、suggest、some、i have（食材清单）；
  3. 无制作信号。

# 关键区分（必看）
- 算true：用户问“怎么做”（如“how to make cake”“what steps to cook rice”）；
- 算false：用户问“做什么”（如“I have eggs, what can I make?”“what should I cook for dinner”）。

# 注意事项
1. 仅输出true或false（无其他内容）；
2. 核心优先级：意图＞关键词（哪怕含make/cook，只要是问“做什么”，就返回false）。
"""

#判定用户意图（第二层滤网）
def whatDoYouMean(user_query,model,tokenizer):
    """
    判定用户意图，是直接询问食谱还是做食谱推荐？
    params:
    user_query:用户问题
    model:就是qwen_mode
    tokenizer: 就是qwen_tokenizer
    final_prompt: 提示词
    """
    final_prompt = final_template.replace("{{user_query}}", user_query)
    # 模型生成：关键修改——增大max_new_tokens，关闭截断
    with torch.no_grad():
        inputs = tokenizer.apply_chat_template(
            [   {'role':"system",'content':'你是专业餐厅接待员，精准判断用户是否在求“制作步骤教程”，否则都是推荐需求'},
                {'role':"system","content":"制作词+单个菜品→true；制作词+菜系大类→false；无制作词→false"},
                {"role": "user", "content": final_prompt}
            ],
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)

        # 关键修改：max_new_tokens设为800（足够生成完整推荐），加eos_token_id避免无意义生成
        outputs = model.generate(
            inputs,
            max_new_tokens=10,  # 只需要输出true/false，10个token足够，避免多余内容
            temperature=0.0,    # 极低温度：让模型更“保守”，优先选高概率答案
            do_sample=False,    # 关闭采样：强制按最大概率输出（彻底消除随机性）
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            attention_mask=torch.ones_like(inputs)
        )

    # 修复解码：即使有特殊token，也先保留原始文本再过滤
    final_answer = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)

    final_answer = final_answer.strip().lower()  # 统一小写，避免True/TRUE等格式问题

    """    # 规则兜底（仅处理模型输出无效的情况）
    if final_answer in ['true', 'false']:
        return final_answer
    else:
        # 极端情况：模型输出乱码，按“无教程诉求”返回false
        return 'false'"""

   # 核心修正：精准关键词库
    user_query_lower = user_query.lower()
    # 1. 制作信号（不变）
    make_signals = {'how to', 'make', 'cook', 'process', 'prepare', 'steps', 'way to', 'explain how', 'show me the steps', 'what steps', 'prep'}
    # 2. 推荐信号（不变）
    recommend_signals = {
        'what should i make', 'what can i cook', 'what foods are good for',
        'don’t take too long to make', 'need dishes', 'i need something',
        'any', 'recommend', 'suggest', 'some', 'which foods are suitable for',
        'i have', 'what can i make', 'what should i make', 'any', 'recommend', 'suggest', 'some'
    }
    # 3. 修正：仅保留“菜系大类关键词”（去掉容易误伤的“dishes”“soups”等）
    cuisine_big_category = {
        'cuisine', 'gluten-free lunch', 'fast food', 'low calorie foods',
        'healthy meal', 'street food'  # 只针对“大类”，不包含具体菜品相关词
    }

    # 最终判定逻辑（精准匹配）
    has_make = any(s in user_query_lower for s in make_signals)
    has_recommend = any(s in user_query_lower for s in recommend_signals)
    has_big_category = any(cat in user_query_lower for cat in cuisine_big_category)

    if has_make and not has_recommend and not has_big_category:
        # 制作词 + 无推荐信号 + 非大类 → true（制作单个菜品）
        return 'true'
    elif has_make and has_big_category:
        # 制作词 + 大类 → false（推荐）
        return 'false'
    elif has_recommend:
        # 有推荐信号 → false
        return 'false'
    else:
        # 无制作词 → false
        return 'false'
