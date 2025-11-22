from transformers import AutoModelForCausalLM
import torch
def model_loader(qwen_model_path):
    """
    加载大模型的函数
    :param qwen_model_path:qwen大模型地址
    :return:返回大模型
    """
    try:
        print("开始加载模型，模型较大，耐心等待，祈祷没人占用GPU")
        model = AutoModelForCausalLM.from_pretrained(
            qwen_model_path,
            device_map = 'auto',
            trust_remote_code = True,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
        ).eval()
        print('Qwen-7B-Chat 模型加载成功')
        return model

    except Exception as e:
        error_msg = str(e)
        if "out of memory" in error_msg.lower():
            print(f"❌ 显存不足！解决方案：1. 改用 CPU 加载（把 device_map 设为 'cpu'）；2. 用 Int4 量化模型（需装 auto-gptq）")
        elif "No such file or directory" in error_msg:
            print(f"❌ 模型路径错误！请确认 {qwen_model_path} 下有 config.json、pytorch_model-*.bin 等文件")
        else:
            print(f"❌ 模型加载失败：{error_msg}")
        return None