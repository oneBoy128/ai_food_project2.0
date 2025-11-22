import os
import torch
from transformers import AutoModel, AutoTokenizer
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# 1. 本地模型路径（你的实际路径）
MODEL_PATH = "/home/wby/projects/model/all-MiniLM-L6-v2"

# 2. 检查GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
logging.info(f"使用设备：{device}")

try:
    # 3. 加载本地分词器和模型（transformers直接读路径，不校验仓库名）
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
    model = AutoModel.from_pretrained(MODEL_PATH, local_files_only=True).to(device)
    logging.info("✅ 模型和分词器加载成功！")

    # 4. 测试生成向量（模拟all-MiniLM的向量生成逻辑）
    def get_embedding(text, tokenizer, model, device):
        # 分词
        inputs = tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="pt"
        ).to(device)
        # 前向传播
        with torch.no_grad():  # 禁用梯度计算，节省内存
            outputs = model(**inputs)
        # 取[CLS] token的向量（all-MiniLM默认用这个做句子嵌入）
        cls_embedding = outputs.last_hidden_state[:, 0, :]
        # 向量归一化（和之前的逻辑一致）
        normalized_embedding = torch.nn.functional.normalize(cls_embedding, p=2, dim=1)
        # 转成numpy数组返回
        return normalized_embedding.cpu().numpy()[0].tolist()

    # 生成测试向量
    test_text = "I want to make lemonade with lemons and sugar."
    embedding = get_embedding(test_text, tokenizer, model, device)
    logging.info(f"✅ 向量生成成功！")
    logging.info(f"向量维度：{len(embedding)}（应为768）")
    logging.info(f"向量前5位：{embedding[:5]}")

except Exception as e:
    logging.error(f"❌ 加载失败：{str(e)}")
    # 打印详细错误（方便定位问题）
    import traceback
    traceback.print_exc()