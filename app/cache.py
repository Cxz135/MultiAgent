# app/cache.py


import redis
import pickle
import hashlib
import json
from typing import Any, Optional


class SimpleRedisCache:

    def __init__(self, ttl=3600):
        self.client = None
        self.ttl = ttl

    def set_client(self, redis_client):
        self.client = redis_client

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.client:
            return None
        try:
            data = self.client.get(f"cache:{key}")
            if data:
                return pickle.loads(data)
            return None

        except Exception as e:
            print(f"缓存读取失败: {e}")
            return None

    def set(self, key: str, value: Any):
        """设置缓存"""
        if not self.client:
            return
        try:
            data = pickle.dumps(value)
            self.client.setex(f"cache:{key}", self.ttl, data)
        except Exception as e:
            print(f"缓存写入失败: {e}")

    def generate_key(self, *args, **kwargs) -> str:
        content = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(content.encode()).hexdigest()

    def clear(self):
        if not self.client:
            return
        try:
            keys = self.client.keys("cache:*")
            if keys:
                self.client.delete(*keys)
            print(f"✅ 已清空 {len(keys)} 个缓存")
        except Exception as e:
            print(f"清空缓存失败: {e}")

# 全局缓存实例
cache = SimpleRedisCache(ttl=3600)