#factory.py


from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
from utils.config_handler import rag_config
from utils.logger import logger
import os

load_dotenv()
_chat_model = None
_light_model = None

def get_chat_model():
    global _chat_model
    if _chat_model is None:
        _chat_model = ChatDeepSeek(model = rag_config.get("chat_model_name"),
                                   temperature = 0.7,
                                   api_key=os.environ.get("DEEPSEEK_API_KEY"),)
    logger.info("聊天模型已调用")
    return _chat_model

from langchain_community.chat_models import ChatTongyi

def get_light_model():
    """使用阿里云Qwen-Turbo，便宜且快"""
    global _light_model
    if _light_model is None:
        _light_model = ChatTongyi(
            model="qwen-turbo",  # 最轻量的版本
            temperature=0,
            max_tokens=200,
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),  # 复用你已有的
        )
        logger.info("轻量模型已初始化（用于判断任务）")
    return _light_model

