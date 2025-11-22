def build_recipe_prompt(query, retrieved_results, prompt_template):
    """"
    构建提示词函数
    :param query: 问题
    :param retrieved_results: 检索结果
    :param prompt_template: 提示词模板
    """
    retrieved_str = ""
    for i,result in enumerate(retrieved_results,1):
        doc_id = result['doc_id']
        distance = round(result['distance'],1)
        recipe_name = result['meta']['Name']
        total_time = round(result['meta']['TotalTime'],1)
        doc_text = result['text'][:200]
        calories = round(result['meta']['Calories'],1)
        category = result['meta']['RecipeCategory']

        #拼接单条数据
        retrieved_str += f"""
        第{i}条数据结果：
        - 文档ID: {doc_id}
        - 相似度: {distance}
        -  名称: {recipe_name}
        -  种类: {category}
        - 总时间: {total_time} min
        -  热量: {calories} 卡
        -食谱核心: {doc_text}
        """

    final_template = prompt_template.replace("{{query}}", query).replace("{{retrieved_results}}", retrieved_str)
    return final_template