from pathlib import Path

import pandas as pd
import re

import torch
from transformers import AutoModel, AutoTokenizer

from langchain_core.documents import Document
from week5.tools.batch_store_to_chroma import batch_store_to_chroma #存入数据库的脚本
from week5.tools.create_chroma import init_chroma #初始化数据库的脚本

#引入自定义的allMini
from week5.tools.get_embedding import get_embedding


from sqlalchemy.testing.plugin.plugin_base import logging

DATA_PATH = Path("/home/wby/projects/week5/data/recipes.csv")
MODEL_PATH = "/home/wby/projects/model/all-MiniLM-L6-v2"

device = 'cuda' if torch.cuda.is_available() else 'cpu' #设备初始化
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True) #allMini分词器初始化
model = AutoModel.from_pretrained(MODEL_PATH, local_files_only=True).to(device) #allMini模型初始化
BATCH_SIZE = 10000
KEY_FIELD = [
        "RecipeId",                  # 食谱唯一ID（关联片段与原数据，必选）
        "Name",                      # 食谱名称（生成回答时展示，必选）
        "RecipeIngredientQuantities",# 食材用量（如“500g”，核心检索字段）
        "RecipeIngredientParts",     # 食材名称（如“鸡肉”，核心检索字段）
        "RecipeCategory",            # 食物类别
        "RecipeInstructions",        # 烹饪步骤（生成回答的核心内容，必选）
        "TotalTime",                 # 总耗时（用户可能筛选“30分钟内”，可选）
        "Calories",                  # 热量（用户可能筛选“低热量”，可选）
        "RecipeServings"             # 份数（后续Agent单位转换用，可选）
    ]

"""#文档分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 300,
    chunk_overlap = 50,
    separators=['\n\n','\n',' ',', ']
)"""

#获取食物集合
recipe_collection = init_chroma(
        db_path= '/home/wby/projects/week5/chroma_db/chroma_recipe_db',
        collection_name= 'recipe_50w_384d_ver2')

# 食品时间对照表
null_cat_time_map = {
    # 第一类：食材/菜品类型
    "Papaya": 15,
    "Strawberry": 15,
    "Penne": 25,
    "Yam/Sweet Potato": 35,
    "Whole Turkey": 180,
    "Rabbit": 90,
    # 第二类：地域菜系
    "Japanese": 30,
    "Thai": 35,
    "Vietnamese": 30,
    "Lebanese": 45,
    "Swiss": 50,
    "Canadian": 45,
    # 第三类：饮食场景/需求
    "Kid Friendly": 20,
    "Potluck": 60,
    "Vegan": 35,
    "Native American": 40,
    "Medium Grain Rice": 30,
    "Elk": 90
}

# 食品数量对照表
serving_map = {
    # 第一类：食材量/菜品规模
    "Whole Turkey": 10,
    "Berries": 4,
    "Citrus": 4,
    "Strawberry": 4,
    "Papaya": 4,
    "Perch": 2,
    # 第二类：饮食场景/需求
    "Kid Friendly": 2,
    "Easy": 2,
    "No Cook": 2,
    "Lactose Free": 4,
    "Spicy": 4,
    # 第三类：地域/食材类型
    "Chinese": 4,
    "Hungarian": 4,
    "Southwest Asia (middle East)": 4,
    "Grains": 4
}

#食品卡路里对照表
calorie_map = {
    # 饮品/酱料类（低卡）
    "Beverages": 80,          # 拿铁咖啡约80大卡
    "Herbal Vinegar": 5,      # 草本醋几乎无热量，取5大卡
    "Gelatin": 70,            # 果冻约70大卡
    "Cookie Icing": 120,      # 糖霜约120大卡/份
    "Lemon Marmalade": 100,   # 柠檬酱约100大卡

    # 蔬菜/水果类（中低卡）
    "Vegetable": 60,          # 蔬菜派约60大卡
    "Peppers": 30,            # 烤甜椒约30大卡
    "Fruit": 50,              # 水果类约50大卡
    "Native American": 80,    # 南瓜约80大卡
    "Vegan": 90,              # 纯素南瓜泥约90大卡

    # 主食/肉类/甜点（中高卡）
    "Chicken Breast": 200,    # 炸鸡条约200大卡
    "Chicken": 220,           # 鸡肉料理约220大卡
    "Meat": 300,              # 烤肉约300大卡
    "Cheese": 180,            # 奶酪约180大卡
    "European": 250,          # 意大利面/烤面包约250大卡
    "Dessert": 350,           # 自制糕点约350大卡
    "Lunch/Snacks": 200,      # 三明治/芝士条约200大卡
    "Very Low Carbs": 150     # 低卡蜂蜜约150大卡（含少量糖）
}

# 用修复后的临时文件读取
batchs = pd.read_csv(
            DATA_PATH,
            chunksize=BATCH_SIZE,
            usecols=KEY_FIELD,
            encoding="utf-8",
            sep=",",  # 指定逗号分隔
            on_bad_lines="skip",  # 跳过极坏行
            engine="python"  # 必须用 python 引擎
        )


#初始化df的各种格式
def init_df(df):
    df['TotalTime'] =df["TotalTime"].apply(iso_to_minutes)
    df["Ingredient_list"] = df["RecipeIngredientParts"].apply(parse_r_list)
    df["Quantity_list"] = df["RecipeIngredientQuantities"].apply(parse_r_list)
    df['Ingredient_list'] = df['Ingredient_list'].apply(del_same)

#获取平均数
def getAvager(df,colum):
    avager = df.groupby('RecipeCategory')[colum].mean()
    return avager

# 时间转化为分钟--apply（已用于初始化）
def iso_to_minutes(iso_str):
    # 第一步：先处理“非字符串类型”（数字、布尔值等）
    if not isinstance(iso_str, str):
        # 如果是NaN，返回None（保持你原有的空值逻辑）
        if pd.isna(iso_str):
            return None
        # 如果是数字（如30、60.5），直接返回整数（假设数字已是分钟数）
        elif isinstance(iso_str, (int, float)):
            return round(iso_str) if iso_str >= 0 else None
        # 其他类型（如布尔值），返回None
        else:
            return None

    # 第二步：处理字符串类型（你的原有逻辑，保持不变）
    if iso_str.strip() == 'PT0S':  # 加strip()避免空字符干扰（如' PT0S '）
        return None

    pattern = r"(\d+\.?\d*)([DHMS])"
    matches = re.findall(pattern, iso_str)

    total_time = 0.0
    for time, unit in matches:
        try:  # 加try-except，避免time不是数字的情况（如'abcH'）
            num = float(time)
        except ValueError:
            continue  # 遇到无效数字，跳过该匹配

        if unit == 'D':
            total_time += num * 1440  # 天→分钟：1天=1440分钟
        elif unit == 'H':
            total_time += num * 60     # 小时→分钟
        elif unit == 'M':
            total_time += num          # 分钟直接加
        elif unit == 'S':
            total_time += num / 60     # 秒→分钟

    # 避免出现0分钟（可能是匹配失败），返回None
    return round(total_time) if total_time > 0 else None

# 清洗TotalTime数据
def rush_time(df):

    #先进行人工表的输入
    for cat,time in null_cat_time_map.items():
        mask = (df['RecipeCategory'] == cat) & (df['TotalTime'].isna())
        df.loc[mask, 'TotalTime'] = time

    #后进行平均值的摄入
    avager = getAvager(df, 'TotalTime')
    for cat,time in avager.items():
        if pd.isna(time):
            continue
        mask = (df['RecipeCategory'] == cat) & (df['TotalTime'].isna())
        df.loc[mask, 'TotalTime'] = time

    #最后进行全局中位数填充
    global_median_time = df['TotalTime'].median()
    mask = df['TotalTime'].isna()
    df.loc[mask, 'TotalTime'] = global_median_time

# 清洗RecipeServings数据
def rush_serving(df):
    #先考虑人工表
    for cat,num in serving_map.items():
        mask = (df['RecipeCategory'] == cat) & (df['RecipeServings'].isna())
        df.loc[mask, 'RecipeServings'] = num

    #再考虑平均值
    avager = getAvager(df, 'RecipeServings').round()
    for cat,num in avager.items():
        if pd.isna(num):
            continue
        mask = (df['RecipeCategory'] == cat) & (df['RecipeServings'].isna())
        df.loc[mask, 'RecipeServings'] = num

    #最后用全局中位数
    global_median_num = df['RecipeServings'].median()
    mask = df['RecipeServings'].isna()
    df.loc[mask, 'RecipeServings'] = global_median_num

# 清洗卡路里数据
def rush_calorie(df):
    df['Calories'] = pd.to_numeric(df['Calories'], errors='coerce')
    for cat,cal in calorie_map.items():
        mask = (df['RecipeCategory'] == cat) & ((df['Calories']<=0)|(df['Calories'].isna()))
        df.loc[mask, 'Calories'] = cal

    avager = getAvager(df, 'Calories').round()
    for cat,num in avager.items():
        if pd.isna(num) or num <= 0:
            continue
        mask = (df['RecipeCategory'] == cat) & ((df['Calories']<=0)|(df['Calories'].isna()))
        df.loc[mask, 'Calories'] = num

    global_median_cal = df['Calories'].median()
    mask = df['Calories'].isna()|df['Calories']<=0
    df.loc[mask, 'Calories'] = global_median_cal

#分割数组的函数--apply(已用于初始化)
def parse_r_list(r_str):
    if pd.isna(r_str):
        return []

    cleaned = re.sub(r'^c\(|(?<=\D)\)$', '', r_str)  # 去掉 "c(" 和 非数字结尾的 ")"
    raw_items = cleaned.split(',') #['orange','"apple"','nan']

    valid_items = []
    for item in raw_items:
        strs = item.strip().strip('"')
        if strs != '' and strs.upper()!='NA':
            valid_items.append(strs)
    return valid_items

# 食谱去重--apply(已用于初始化)
def del_same(row):
    """
    pd.isna()解决的是元素是否缺失，而不是判定数组是否为空
    # 对列表中的每个元素判断是否为缺失值
    result = pd.isna(['a', 'b', 'na'])
    print(result)  # 输出：[False False False]
    row = []
    print(pd.isna(row))  # 输出：array([], dtype=bool)
    """
    if len(row) == 0 or not row:
        return []

    maps = dict()
    for v in row:
        if v not in maps:
            maps[v] = v
    return list(maps.values())

# 多余者切除--已用于切除函数里
def cut_long(longer_list,smaller_list):
    return longer_list[:len(smaller_list)]

# 切除函数
def cut_list(df):
    #空表防护
    df['Ingredient_list'] = df['Ingredient_list'].apply(lambda x: ['无'] if len(x) == 0 else x)
    df['Quantity_list'] = df['Quantity_list'].apply(lambda x: ['适量'] if len(x) == 0 else x)
    #先切割食谱大于食量的
    df['Ingredient_len'] = df['Ingredient_list'].apply(len)
    df['Quantity_len'] = df['Quantity_list'].apply(len)
    mask = (df['Ingredient_len']>df['Quantity_len'])
    df.loc[mask,'Ingredient_list'] = df.apply(lambda row: cut_long(
        row['Ingredient_list'],
        row['Quantity_list']
    ), axis=1)
    mask = (df['Ingredient_len']<df['Quantity_len'])
    df.loc[mask,'Quantity_list'] = df.apply(lambda row: cut_long(
        row['Quantity_list'],
        row['Ingredient_list']
    ),axis=1)

    #更新
    df['Ingredient_len'] = df['Ingredient_list'].apply(len)
    df['Quantity_len'] = df['Quantity_list'].apply(len)

#跳过错误行
def skip_and_warn(bad_line):
    print(f"跳过错误行：{bad_line}")  # 打印错误行内容
    return None  # 返回None表示跳过该行

#转为文本结构--apply
def conver_row_to_text(row):
    basic_info = f"""
RecipeId:{row['RecipeId']}
Name:{row['Name']}
TotalTime:{row['TotalTime']}
RecipeCategory:{row['RecipeCategory']}
Calories:{row['Calories']}
RecipeServings:{row['RecipeServings']}
""".strip()

    ingredient_parirs = []
    for ing, quant in zip(row['Ingredient_list'], row['Quantity_list']):
        strs = f"{ing}:{quant}"
        ingredient_parirs.append(strs)
    ingredient_info = f"Ingredients and Quantities:" + '\n' + '\n'.join(ingredient_parirs)

    instructions = row['RecipeInstructions'] if pd.notna(row['RecipeInstructions']) else 'No detailed steps available'
    instruction_info = instructions.strip().lstrip('c(').rstrip(')')
    steps_strings = instruction_info.split('", "')
    steps = []

    for s in steps_strings:
        clean_step = s.strip().strip('"')
        steps.append(clean_step)

    instruction_complete_list = [f'{i + 1}. {step}' for i, step in enumerate(steps)]
    instruction_comlete = 'Cooking steps:' + '\n' + '\n'.join(instruction_complete_list)

    full_text = basic_info + '\n' + ingredient_info.strip() + '\n' + instruction_comlete.strip()
    return full_text

# 清洗总函数
def rush_all(batch):
    init_df(batch)
    rush_time(batch)
    rush_calorie(batch)
    rush_serving(batch)
    cut_list(batch)
    batch.dropna(inplace=True)#清洗后还有的数据不要了

#建立元数据 --apply
def create_baseInfor(row):
    return {
        'RecipeId':row['RecipeId'],
        'Name':row['Name'],
        'TotalTime':row['TotalTime'],
        'RecipeCategory':row['RecipeCategory'],
        'Calories':row['Calories'],
        'RecipeServings':row['RecipeServings']
    }

#进行文档切割，切割版本
"""def create_chunks(df,text_splitter):
    chunks_list = []
    for i in range(df.shape[0]):
        chunks = text_splitter.create_documents(
            texts = [df['text'].iloc[i]],
            metadatas = [df['baseInfo'].iloc[i]],
        )
        chunks_list.extend(chunks)
    return chunks_list"""
#进行文本创建，未切割版本
def create_chunks(df):
    chunks_list = []
    for i in range(df.shape[0]):
        chunks = Document(
            page_content = df['text'].iloc[i],
            metadata = df['baseInfo'].iloc[i],
        )
        chunks_list.append(chunks)
    return chunks_list


chunks_lists = []
try:
    nums = 0
    for batch in batchs:
        try:
            print(f"开始{nums+1}批数据")
            rush_all(batch)
            batch['text'] = batch.apply(conver_row_to_text, axis=1)
            batch['baseInfo'] = batch.apply(create_baseInfor, axis=1)
            chunks_lists = create_chunks(batch) #document列表
            batch_store_to_chroma(recipe_collection, chunks_lists,tokenizer, model, device)
            """print(f"第{nums+1}批数据情况如下:"
                  f"食谱不等者{batch[batch['Ingredient_len'] != batch['Quantity_len']].shape[0]}  "
                  f"卡路里为0者{batch[batch['Calories'] == 0].shape[0]}  "
                  f"TotalTime为0者{batch['TotalTime'].isna().sum()}  "
                  f"Recipes为na者{batch['RecipeServings'].isna().sum()}")"""


        except Exception as e:
            print(f"第{nums+1}批出错：{e}")
        finally:
            del batch
            del chunks_lists
            import gc;gc.collect()

        #直接上强度
        nums += 1
        """nums += 1
        if nums == 8:
            break"""
except Exception as e:
    print(f"读取阶段出错：{e}")