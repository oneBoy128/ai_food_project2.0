from transformers import AutoTokenizer
def tokenizer_loader(qwen_model_path):
    """
    qwen分词器的加载脚本
    :qwen_model_path:qwen大模型地址
    :return:返回分词器
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            qwen_model_path,
            trust_remote_code = True
        )
        qwen_official_chat_template = """
        {% for message in messages %}
            {% if message['role'] == 'user' %}
                <|im_start|>user
                {{ message['content'] }}
                <|im_end|>
            {% elif message['role'] == 'assistant' %}
                <|im_start|>assistant
                {{ message['content'] }}
                <|im_end|>
            {% endif %}
        {% endfor %}
        {% if add_generation_prompt %}
            <|im_start|>assistant
        {% endif %}
        """
        tokenizer.chat_template = qwen_official_chat_template  # 把模板赋值给分词器
        tokenizer.pad_token = tokenizer.eos_token  # 用结束符作为填充符（官方推荐）
        print('Qwen 分词器加载成功！')
        return tokenizer
    except Exception as e:
        print(e)
        return None