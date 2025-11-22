import torch
from week5.tools.model_loader import model_loader
from week5.tools.tokenizer_loader import tokenizer_loader
from week5.code_rag.run_rag import parse_model_output
from peft import PeftModel



prompt_template = """
###任务：严格根据用户JSON中的Name字段，返回对应食谱的完整信息（缺一不可）
1. 只读取用户JSON里的"Name"值，忽略其他字段；
2. 输出必须包含所有字段：Name（和输入Name完全一致）、RecipeCategory、RecipeServings、TotalTime、Ingredients、Step；
3. 仅输出JSON，无任何多余内容，字段值用英文。

###示例：
用户查询：{"Name":"chicken salad","Calories":250}
输出：
{
    "Name": "chicken salad",
    "RecipeCategory": "Low Calorie",
    "RecipeServings": "4",
    "TotalTime": "30",
    "ingredients": "chicken breast:1 lb\nmayo:1/2 cup\ndill pickles:6 slices\nred onion:1/4 cup",
    "cookingSteps": "1. Cook chicken and shred.\n2. Mix with mayo, pickles and onion.\n3. Chill before serving."
}

###用户查询：
{query}

###输出（必须包含Step字段）：
"""

# 若检索不出用户提到的菜名，则让模型自己检索
def is_food_teach(query, qwen_model, qwen_tokenizer):
    """
    基于 QWen-7B 模型，用QWEN-7B自己来给RAG检索之外的答案
    :param query: 用户查询（字符串）
    :param qwen_model: 加载好的 QWen-7B 模型
    :param qwen_tokenizer: 加载好的 QWen 分词器
    :return:
    """
    # 1. 构造提示词模板（替换 {{query}} 为实际用户查询）

    # 填充用户查询到提示词中
    #prompt = prompt_template.format(query=query)
    final_prompt = prompt_template.replace('{query}', query)

    # 2. 用 QWen 分词器处理提示词（适配 QWen 聊天格式）
    inputs = qwen_tokenizer.apply_chat_template(
        [
            {'role':"system", "content": '你是一个专业的美食顾问，你需要根据用户询问，判定他是需要你推荐美食还是提供这道菜的食谱'},
            {"role": "user", "content": final_prompt}
        ],  # 按 QWen 要求的聊天格式组织
        add_generation_prompt=True,  # 自动添加模型回复的前缀
        return_tensors="pt"  # 返回 PyTorch 张量
    ).to(qwen_model.device)  # 移到模型所在设备（GPU/CPU）

    # 3. 模型生成结果（控制输出长度，避免冗余）
    with torch.no_grad():  # 禁用梯度计算，节省内存
        outputs = qwen_model.generate(
            inputs,
            max_new_tokens=4000,  # 食物列表长度有限，50个token足够
            temperature=0.1,  # 降低随机性，确保输出格式稳定
            top_p=0.9,
            do_sample=False,  # 确定性生成，避免重复结果
            eos_token_id=qwen_tokenizer.eod_id  # 遇到结束符停止生成
        )

    # 4. 解码输出并提取食物列表
    # 提取模型生成的部分（排除输入提示词）
    generated_ids = outputs[:, inputs.shape[1]:]
    raw_output = qwen_tokenizer.decode(generated_ids[0], skip_special_tokens=True).strip()

    return raw_output


if __name__ == '__main__':
    qwen_model_path = '/home/wby/projects/model/Qwen-7B-Chat'
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    qwen_tokenizer = tokenizer_loader(qwen_model_path)

    # 加载模型
    base_model = model_loader(qwen_model_path)
    qwen_model = PeftModel.from_pretrained(base_model, "/home/wby/projects/week5/data/qwen_food_lora3/final_lora")

