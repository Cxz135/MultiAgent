#web_search.py


from agents.base_agent import BaseAgent
import aiohttp
import asyncio
import json
from serpapi import GoogleSearch
import os

from core.state import OverallState
from utils.logger import logger
from dotenv import load_dotenv

load_dotenv()


class WebSearchAgent(BaseAgent):
    def __init__(self, model):
        super().__init__(model)
        self.api_key = os.getenv("SERPAPI_API_KEY")

    async def search_web(self, query: str, num_results: int = 5):
        params = {
            "q": query,
            "api_key": self.api_key,
            "num": num_results,
            "gl": "cn",
            "hl": "zh-cn",
            "engine": "google"
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        # 解析结果（SerpApi 返回格式和 Serper 不同）
        parsed = []
        if 'organic_results' in results:
            for item in results['organic_results'][:num_results]:
                parsed.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('link', ''),
                    'engine': 'serpapi'
                })
        return parsed

    def process(self, state: OverallState) -> dict:
        query = state["messages"][-1].content
        local_docs = state.get("retrieved_docs", [])
        course = state.get("current_course", "未分类")

        logger.info("🌐 正在联网搜索...")
        web_results = asyncio.run(self.search_web(query))

        # 格式化本地资料
        local_context = "\n".join([
            f"[课程资料] {d.page_content[:500]}..."  # 限制长度，避免 token 太长
            for d in local_docs[:3]
        ]) if local_docs else "无本地资料"

        # 格式化搜索结果
        if web_results:
            web_context = "\n".join([
                f"[网络] {r['title']}\n内容: {r['snippet']}\n来源: {r['url']}"
                for r in web_results
            ])
            logger.info(f"✅ 找到 {len(web_results)} 条网络结果")
        else:
            web_context = "无搜索结果"
            logger.warning("⚠️ 未找到网络结果")

        prompt = f"""
            你正在帮助学生学习【{course}】课程。
            
            【课程资料】（请优先使用）：
            {local_context}
            
            【网络搜索结果】（仅供参考）：
            {web_context}
            
            用户问题：{query}
            
            回答要求：
            1. 优先使用【课程资料】中的内容
            2. 如果【课程资料】不足，可以用【网络搜索结果】补充
            3. 如果使用网络信息，请标注来源
            4. 如果网络信息与课程资料冲突，以课程资料为准
            5. 如果网络信息超出课程范围，请说明这是扩展内容
            """

        response = self.model.invoke(prompt)

        return {
            "final_output": response.content,
            "web_results": web_results,
            "current_step": "web_done",
        }


