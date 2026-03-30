#app/main.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.api import chat, documents
import uvicorn
import os
import redis
from contextlib import asynccontextmanager
from fastapi.templating import Jinja2Templates
from app.cache import cache
from core.course_service import course_service
from utils.logger import logger
from dotenv import load_dotenv
load_dotenv()

redis_client = None

# 自定义缓存函数
'''def cached_llm_call(llm, prompt):
    key = cache.generate_key(prompt)
    cached = cache.get(key)
    if cached:
        print(f"缓存命中: {prompt[:30]}...")
        return cached

    print(f"缓存未命中: {prompt[:30]}...")
    result = llm.invoke(prompt)
    cache.set(key, result)
    return result'''

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    os.makedirs("data/uploads", exist_ok=True)
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "learning-assistant")

    try:
        redis_client = redis.Redis.from_url(
            "redis://localhost:6379",
            decode_responses=False,
            socket_timeout=5,
            socket_connect_timeout=2,
        )
        redis_client.ping()
        logger.info("✅ Redis 连接成功")

        # 设置缓存客户端
        cache.set_client(redis_client)  # 现在有这个方法了

        # 测试缓存
        test_key = cache.generate_key("test")
        cache.set(test_key, {"test": "value"})  # 精确缓存测试
        test_value = cache.get(test_key)
        if test_value:
            logger.info("✅ 精确缓存测试成功")
        else:
            logger.warning("⚠️ 精确缓存测试失败")

        # 测试语义缓存
        cache.set("这是一个测试问题", {"answer": "测试答案"}, "test_course", "qa")
        semantic_result = cache.get("这是一个测试问题", "test_course", "qa")
        if semantic_result:
            logger.info("✅ 语义缓存测试成功")
        else:
            logger.warning("⚠️ 语义缓存测试失败")

    except Exception as e:
        print(f"⚠️ Redis 连接失败，将不使用缓存: {e}")
        cache.set_client(None)

    logger.info("🚀 应用启动完成")
    yield

    logger.info("🛑 应用关闭中...")
    if redis_client:
        redis_client.close()
        logger.info("✅ Redis 连接已关闭")


app = FastAPI(title="智能学习助手", lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),  # 生产环境要改
    max_age=120,  # session 过期时间（秒）
    same_site="lax",
)

templates = Jinja2Templates(directory="app/static")
app.include_router(chat.router, prefix="/api")
app.include_router(documents.router, prefix="/api")


@app.get("/")
async def home(request: Request):
    # 获取用户ID（可以从 session 或 cookie 获取，这里先用 default）
    if "user_id" not in request.session:
        import secrets
        request.session["user_id"] = f"user_{secrets.token_hex(4)}"

    user_id = 'default'

    # 获取用户的课程列表
    courses = course_service.get_user_courses(user_id)
    current_course = request.session.get("current_course", courses[0] if courses else "未分类")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "courses": courses,
            "current_course": current_course,
        }
    )

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

def get_redis():
    """获取 Redis 客户端（如果可用）"""
    if hasattr(app.state, "redis"):
        return app.state.redis
    return None

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )