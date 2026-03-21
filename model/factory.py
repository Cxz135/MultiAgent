#factory.py


from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
from utils.config_handler import rag_config
from utils.logger import logger
import os

load_dotenv()
_chat_model = None

def get_chat_model():
    global _chat_model
    if _chat_model is None:
        _chat_model = ChatDeepSeek(model = rag_config.get("chat_model_name"),
                                   temperature = 0.7,
                                   api_key=os.environ.get("DEEPSEEK_API_KEY"),)
    logger.info("聊天模型已调用")
    return _chat_model

