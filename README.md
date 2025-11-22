# 文件说明
recipe-test是前端代码，week5是后端代码

# 项目的思维链
<img width="2375" height="715" alt="总思维链" src="https://github.com/user-attachments/assets/6d08b3cc-2fe6-4f0a-bcd5-ec5cf2a20550" />


# 重要文件说明
week5/code_rag/rag_test.ipynb 是整个项目的核心文件，它记录着我的大模型的很多子模块实验 <br>
week5/code_rag/mode_tiao.ipynb 是微调代码 <br>
整个向量数据库用的是chroma， 检索model是all-MiniLM-L6-V2, 使用的大模型是QWEN-7B-Chat测试版 <br>
week5/tools/batch_store_to_chroma，是把当前批次的embedding存入到chroma数据库里<br>
week5/code_rag/data_batch_loader，是总的把embedding存入到chroma数据库里的总脚本<br>
week5/code_rag/clean2.ipynb，是数据清洗实验的jupyter文件<br>
wee5/tools/test_connect，是跑后端服务器的脚本
