import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, __version__ as transformers_version
from peft import __version__ as peft_version  # 顺便打印peft版本（微调会用到）

# 1. 打印基础库版本

print("="*50)
print(f"Torch 版本: {torch.__version__}")
print(f"Transformers 版本: {transformers_version}")
print(f"PEFT 版本: {peft_version}")
print(f"CUDA 是否可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU 型号: {torch.cuda.get_device_name(0)}")
    print(f"GPU 显存: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
print("="*50)

# 这里填你加载 QWen-7B-Chat 的路径（本地路径或 "Qwen/Qwen-7B-Chat"）
MODEL_PATH = '/home/wby/projects/model/Qwen-7B-Chat'

try:
    # 加载分词器和模型（不加载完整权重，只看配置）
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model_config = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        load_in_4bit=False,  # 不加载量化权重，快且省内存
        device_map="cpu"     # 用CPU加载，避免占用GPU
    ).config

    # 输出关键信息
    print("="*50)
    print("1. QWen 模型配置信息：")
    print(f"   - 模型维度（hidden_size）：{model_config.hidden_size}")
    print(f"   - 注意力头数（num_attention_heads）：{model_config.num_attention_heads}")
    print(f"   - 模型层数（num_hidden_layers）：{model_config.num_hidden_layers}")
    print("="*50)
    print("2. 依赖库版本：")
    print(f"   - torch 版本：{torch.__version__}")
    from transformers import __version__ as transformers_version
    print(f"   - transformers 版本：{transformers_version}")
    try:
        from peft import __version__ as peft_version
        print(f"   - peft 版本：{peft_version}")
    except ImportError:
        print(f"   - peft 版本：未安装")
    try:
        from bitsandbytes import __version__ as bnb_version
        print(f"   - bitsandbytes 版本：{bnb_version}")
    except ImportError:
        print(f"   - bitsandbytes 版本：未安装")
    print("="*50)

except Exception as e:
    print(f"查看信息出错：{e}")
    print(f"如果是本地模型，请确认 MODEL_PATH 路径正确（如 './Qwen-7B-Chat'）")