from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

from utils.path_tool import get_project_path

PROJECT_PATH = get_project_path()

load_dotenv(os.path.join(PROJECT_PATH, ".env"))


def create_deepseek_model():
    """创建一个deepseek模型"""
    return init_chat_model(
        model="deepseek:deepseek-flash",
        temperature=0.2,
    )


if __name__ == '__main__':
    model = create_deepseek_model()
    response = model.invoke("你好")
    print(response)
