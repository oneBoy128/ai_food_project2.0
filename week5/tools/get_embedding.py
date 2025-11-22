#此脚本是导入本地的allMini-L6-v2的
import torch
import logging


def get_embedding(text, tokenizer, model, device):
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
