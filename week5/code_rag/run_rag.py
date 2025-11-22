from peft import PeftModel

from week5.code_rag.is_food_query_final_solution import is_food_query_final_solution
from week5.code_rag.recommend.rag_recipe_qa_fixed import rag_recipe_qa_fixed
from tools.tokenizer_loader import tokenizer_loader
from week5.tools.model_loader import model_loader
from week5.code_rag.recommend.whatDoYouMean import whatDoYouMean
from week5.code_rag.make_foods.final_about_food import final_about_food
from week5.code_rag.recommend.FinalMean import FinalMean
from week5.code_rag.recommend.final_recommend import final_recommend

import torch
import json
import re


def parse_model_output(raw_output):
    try:
        # 第一步：直接尝试解析原始输出（兼容数组/对象）
        return json.loads(raw_output.strip())
    except json.JSONDecodeError:
        cleaned_output = raw_output.strip()

        # 1. 移除所有代码块标记（```json/```）及多余空白
        cleaned_output = re.sub(r'```(json)?', '', cleaned_output)
        cleaned_output = re.sub(r'\n+|\t+', ' ', cleaned_output)

        # 2. 智能识别格式并修复闭合符号（同时兼容数组和对象）
        bracket_count = cleaned_output.count('[')
        brace_count = cleaned_output.count('{')

        if bracket_count > 0 and brace_count > 0:
            # 优先处理数组（[{}]格式）
            first_bracket = cleaned_output.find('[')
            last_bracket = cleaned_output.rfind(']')
            if first_bracket != -1 and last_bracket != -1:
                cleaned_output = cleaned_output[first_bracket:last_bracket + 1]
        elif brace_count > 0:
            # 处理纯对象（{}格式）
            first_brace = cleaned_output.find('{')
            last_brace = cleaned_output.rfind('}')
            if first_brace != -1 and last_brace != -1:
                cleaned_output = cleaned_output[first_brace:last_brace + 1]
        elif bracket_count > 0:
            # 处理纯数组（[]格式）
            first_bracket = cleaned_output.find('[')
            last_bracket = cleaned_output.rfind(']')
            if first_bracket != -1 and last_bracket != -1:
                cleaned_output = cleaned_output[first_bracket:last_bracket + 1]

        # 3. 通用修复：多余逗号、空字段、引号转义问题
        cleaned_output = re.sub(r',\s*([}\]])', r'\1', cleaned_output)  # 末尾多余逗号
        cleaned_output = re.sub(r'"taste":\s*""', '"taste": "unknown"', cleaned_output)
        cleaned_output = re.sub(r'"Reason":\s*""', '"Reason": "No detailed reason provided"', cleaned_output)
        cleaned_output = re.sub(r'(\w+):\s*"([^"]*")([^"]*)"', r'\1: "\2\\""', cleaned_output)  # 修复内部引号

        # 4. 再次尝试解析（兼容数组/对象）
        try:
            return json.loads(cleaned_output.strip())
        except json.JSONDecodeError as e:
            print(f"解析失败，错误信息：{str(e)} | 修复后数据：{cleaned_output[:]}...")
            # 兜底返回（保持原格式兼容）
            return [
                {
                    "Name": "Data Parse Error",
                    "Calories": 0,
                    "Total Time": 0,
                    "Reason": "大模型格式输出出错，请重新输入问题吧。十分抱歉",
                    "taste": "unknown",
                }
            ] if bracket_count > 0 else {
                "Name": "Data Parse Error",
                "Calories": 0,
                "Total Time": 0,
                "Reason": "大模型格式输出出错，请重新输入问题吧。十分抱歉",
                "taste": "unknown",
                "step":"测试版的Qwen-7B大模型格式输出出错，请重新输入问题吧。十分抱歉 \n "
                       "The output of the large model format is incorrect. Please re-enter the problem. We are very sorry"
            }

"""
这是测试，相当于整个大模型的大脑:
 1. 第一层滤网，判定用户话题是否与美食相关
 2. 第二层滤网，判定用户话题是推荐具体食物还是推荐美食
 3. 第三层滤网，判定用户是需要根据食材来推荐，还是根据特点和特殊场景来推荐
 4. 根据判定，调用不同的函数
"""
#暴露出去的函数
def run_final(query, model, tokenizer):
    """
    暴露出去的函数，用于处理用户提问
    :param query: 用户提问
    :param model: 外部传的模型
    :param tokenizer: 外部传的分词器
    :return: 包含处理结果的字典
    """
    # 初始化返回对象（使用字典键名小写，符合Python命名规范）
    final_obj = {
        'data': None,  # 存储json或文本结果
        'rag_list': [],  # 存储RAG检索列表
        'code': 400,  # 状态码：400非食物，200具体菜，201食材推荐，202特定推荐
        'message': ""  # 新增：错误或提示信息
    }

# 第一层滤网：判定是否为食物相关话题
    no1 = is_food_query_final_solution(query, model, tokenizer)
    if no1 != 'YES':
        print("判定为非食物话题")
        final_obj['data'] = "Please enter a topic related to food"
        final_obj['message'] = "Query is not food-related"
        return final_obj

    # 第二层滤网：判定是询问具体做法还是推荐
    no2 = whatDoYouMean(query, model, tokenizer)
    # 修复：明确判断字符串"true"/"false"（避免之前的类型转换陷阱）
    is_specific_food = no2.strip().lower() == 'true'

    if is_specific_food:
        print("判定为询问具体食物做法")
        # 修复：使用传入的model和tokenizer，而非全局变量qwen_model
        result = final_about_food(query, model, tokenizer)
        final_answer = parse_model_output(result)
        final_obj['data'] = final_answer
        final_obj['code'] = 200
        final_obj['message'] = "Success: specific food recipe"
        return final_obj
    else:
        # 第三层滤网：判定推荐类型（食材/特点）
        no3 = FinalMean(query, model, tokenizer)
        if no3.strip().lower() == 'ingredient':
            print("判定为根据食材推荐")
            result = rag_recipe_qa_fixed(query, model, tokenizer)
            if len(result) != 2:
                raise ValueError(f"rag_recipe_qa_fixed返回值数量错误，预期2个，实际{len(result)}个")
            final_answer, rag_lists = result
            final_answer = parse_model_output(final_answer)
            final_obj['data'] = final_answer
            final_obj['rag_list'] = rag_lists
            final_obj['code'] = 201
            final_obj['message'] = "Success: ingredient-based recommendation"
            return final_obj
        else:
            print("判定为根据特点/场景推荐")
            # 同样检查返回值数量
            result = final_recommend(query, model, tokenizer)
            if len(result) != 2:
                raise ValueError(f"final_recommend返回值数量错误，预期2个，实际{len(result)}个")
            final_answer, rag_lists = result
            final_answer = parse_model_output(final_answer)
            final_obj['data'] = final_answer
            final_obj['rag_list'] = rag_lists
            final_obj['code'] = 202
            final_obj['message'] = "Success: feature/scene-based recommendation"
            return final_obj



#如果仅是进行测试来跑，则优先加载完一些数据后开始跑
if __name__ == '__main__':
    user_query = "how to make kung pao chicken?"
    qwen_model_path = '/home/wby/projects/model/Qwen-7B-Chat'
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    qwen_tokenizer = tokenizer_loader(qwen_model_path)
    base_model = model_loader(qwen_model_path)
    qwen_model = PeftModel.from_pretrained(base_model, "/home/wby/projects/week5/data/qwen_food_lora3/final_lora")

    final_obj=run_final(user_query,qwen_model,qwen_tokenizer)

    print(f"最终答案{final_obj}")


