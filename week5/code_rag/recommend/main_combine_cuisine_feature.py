"""
该模块是菜系特点的总合并模块, 该模块包括:
    1. 提取菜系
    2. 提取特点
    3. 翻译特点
    4. 合并菜系特点
"""
from week5.code_rag.recommend.extract_single_cuisine import extract_single_cuisine
from week5.code_rag.recommend.extract_feature import extract_feature

#词句翻译
books = {
        # 核心热量/营养（保留原有+补充隐含词）
    'low calorie': ['low calorie', 'weight loss', 'loss weight', 'diet', 'slim', 'reduce weight', 'weight control', 'low cal' ],
    'high calorie': ['high calorie', 'high cal', 'energy-rich'],
    'high protein': ['high protein', 'protein-rich', 'fitness meal', 'post-workout', 'muscle gain'],
    'low protein': ['low protein', 'protein-poor'],
    'high carb': ['high carb', 'carb-rich'],
    'low carb': ['low carb', 'carb-poor', 'keto'],

    # 饮食限制/特殊需求（新增高频场景）
    'vegan': ['vegan', 'plant-based', 'no animal products'],
    'vegetarian': ['vegetarian', 'no meat'],
    'gluten-free': ['gluten-free', 'no gluten'],
    'dairy-free': ['dairy-free', 'no dairy', 'lactose-free'],
    'no sugar': ['no sugar', 'sugar-free', 'no added sugar'],

    # 场景/标签（补充家庭/聚会/便携等）
    'family food': ['family food', 'family meal', 'family picnic', 'for family'],
    'fast food': ['fast food', 'fast', 'short time', 'quick', 'easy to make', '30 minute', 'no-oven'],
    'finger food': ['finger food', 'party food', 'for party', 'snacks for gathering'],
    'picnic food': ['picnic food', 'for picnic', 'outdoor food'],
    'portable food': ['portable', 'easy to carry', 'travel food', 'road trip food'],
}

special_words={
    "low calorie" : 'calories < 250',
    "high calorie" : 'calories > 250',
    "family food": 'RecipeServings > 3',
    "fast food": 'TotalTime < 60',
}

#把特征翻译映射
def translate(feature_list):
    mappers = [feat for feat,keywords in books.items() if  any(kw in fea for kw in keywords for fea in feature_list)] #使用双循环判定
    for i in range(len(mappers)):
        for kw,v in special_words.items():
            if kw in mappers[i]:
                mappers[i] = v

    unmappers = [feat for feat in feature_list if not any(kw in feat for _,keywords in books.items() for kw in keywords)]
    return mappers + unmappers

#合并cuisine和feature
def combine_cuisine_feature(feature_list,cuisine):
    #如果检测到仅仅只推荐特征
    if cuisine is None:
        strs = ' and '.join(feature_list)
        return strs

    mapper_list = [feat for feat in feature_list if not (cuisine in feat)]
    strs = ' and '.join(mapper_list)
    #如果仅仅只是推荐菜系
    if len(mapper_list) == 0:
        return cuisine + ' cuisine '

    #又有菜系又有特征
    cuisine = cuisine + ' that is '
    return cuisine + strs

#总合并函数——这是主函数
def main_combine_cuisine_feature(userquery, qwen_model, qwen_tokenizer):
    cuisine = extract_single_cuisine(userquery, qwen_model, qwen_tokenizer)
    feature_list = extract_feature(userquery, qwen_model, qwen_tokenizer)
    translate_list = translate(feature_list)
    result = combine_cuisine_feature(translate_list,cuisine)
    print(f"最终问题{userquery + 'and' + result}")
    return userquery + 'and' + result