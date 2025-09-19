"""
辅助模块
@File       utils.py
@Author     小明
@Date       2025/9/18 09:16
@Version    V0.0.1
"""
import dotenv
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


# def get_model():
#     model = ChatOpenAI(
#         model='glm-4.5'
#     )
#     return model

# def get_model():
#     model = ChatOpenAI(
#         model='gpt-4.1'
#     )
#     return model

def get_model():
    model = ChatOpenAI(
        model='deepseek-reasoner'
    )
    return model
