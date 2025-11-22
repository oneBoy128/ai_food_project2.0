#该脚本是用来创建chroma数据库的
import logging
from pathlib import Path
from chromadb import PersistentClient
from chromadb.config import Settings

LOG_DIR = '/home/wby/projects/week5/log'
LOG_FILE = 'chroma_store_log.txt'
LOG_FULL_PATH = Path(LOG_DIR) / LOG_FILE

logging.basicConfig(
    filename=LOG_FULL_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

def init_chroma(
        db_path: str = '/home/wby/projects/week5/chroma_db/chroma_recipe_db2',
        collection_name: str = 'recipe_50w_384d'
)-> "PersistentClient.Collection":
    """
    初始化chroma数据库，不存在则创建，存在则直接获取
    :param db_path: chroma数据库的持久化路径
    :param collection_name: chroma数据库的集合名称
    :return: 返回chroma对象
    """
    # 创建持久化客户端
    chroma_client = PersistentClient(
        db_path,
        settings=Settings(
            anonymized_telemetry=False,  # 关闭匿名统计
            allow_reset=False,  # 禁止重置数据库（防误删）
            persist_directory=db_path  # 明确持久化路径
        )
    )

    #collection也有元数据
    collection = chroma_client.get_or_create_collection(
        collection_name,
        metadata={
            'description': '50万食谱数据',
            'vector_dimension': 384,
            "model_name": "nreimers/MiniLM-L6-H384-uncased",  # 记录用的模型
            "data_source": "recipes.csv"   # 数据来源
        }
    )

    # 打印/记录初始化信息
    logging.info(f"✅ Chroma初始化完成！")
    logging.info(f"  - 存储路径：{db_path}")
    logging.info(f"  - 集合名称：{collection_name}")
    logging.info(f"  - 当前集合已有向量数：{collection.count()}")  # 查看是否有历史数据
    print(f"Chroma初始化完成！当前集合已有向量数：{collection.count()}")
    return collection

if __name__ == '__main__':
    init_chroma(db_path= '/home/wby/projects/week5/chroma_db/chroma_recipe_db',
        collection_name= 'recipe_50w_384d_ver2')