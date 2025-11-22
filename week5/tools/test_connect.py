# test_server.py（服务器上新建这个文件）
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  # 用于请求体数据验证

from week5.tools.model_loader import model_loader
import torch
from transformers import AutoTokenizer, AutoModel
from week5.tools.tokenizer_loader import tokenizer_loader
from week5.code_rag.is_food_teach import is_food_teach
from peft import PeftModel


#最后的函数
from week5.code_rag.run_rag import run_final

# 1. 初始化最小FastAPI应用
app = FastAPI()

# 2. 配置跨域（允许你本地前端地址，必须和Vue地址一致）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # 你的Vue前端本地地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3，在运行服务器的时候，模型是已经加载好的,先让这些该加载的东西都加载了
user_query = "i have milk and egg and apple. What kinds of food can i make?"
qwen_model_path = '/home/wby/projects/model/Qwen-7B-Chat'
device = 'cuda' if torch.cuda.is_available() else 'cpu'
qwen_tokenizer = tokenizer_loader(qwen_model_path)

#加载模型
base_model = model_loader(qwen_model_path)
qwen_model = PeftModel.from_pretrained(base_model, "/home/wby/projects/week5/data/qwen_food_lora3/final_lora")


# 4.定义问题类
class requerQuery(BaseModel):
    query: str #输入问题


# 4. 接口工程

#测试接口
@app.get("/test_connect")
async def test_connect():
    return {
        "code": 200,
        "message": "服务器连接成功！",
        "data": "Hello from 实验室服务器"
    }

#测试输出
@app.post('/test_post')
async def test_post(request: requerQuery):
    return {
        "code": 200,
        "message":"请求成功！",
        "data":{
            'query':request.query,
        }
    }

# 用户输入问题
@app.post('/send_query')
async def send_query(request: requerQuery):
    """
    final_obj = {
        'data': None,  # 存储json或文本结果
        'rag_list': [],  # 存储RAG检索列表
        'code': 400,  # 状态码：400非食物，200具体菜，201食材推荐，202特定推荐
        'message': ""  # 新增：错误或提示信息
    }
    """
    final_obj = run_final(request.query,qwen_model, qwen_tokenizer)


    return {
        "code": final_obj['code'],
        'message': final_obj['message'],
        'data': {
            'final_answer': final_obj['data'],
            'rag_lists': final_obj['rag_list'],
        }
    }

# 当大模型靠自己推荐食品时
@app.post('/by_myself')
async def by_myself(request: requerQuery):
    result = is_food_teach(request.query, qwen_model, qwen_tokenizer)
    return result

# 4. 启动服务器（用空闲端口，比如8888）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)  # host=0.0.0.0必须加