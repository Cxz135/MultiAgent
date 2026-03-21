#course_service.py


from agents.course_manager import CourseManager
from model.factory import get_chat_model
from utils.logger import logger
import json
import os

class CourseService:

    def __init__(self):
        self.course_manager = CourseManager(get_chat_model())
        self.courses_file = "data/courses.json"
        self._load_courses()

    def _load_courses(self):
        if os.path.exists(self.courses_file):
            with open(self.courses_file, "r") as f:
                self.courses = json.load(f)
        else:
            self.courses = {
                "default": {
                    "courses": ["机器学习", "深度学习"],  # 默认课程
                    "user_custom": {}
                }
            }
            self._save_courses()

    def get_user_courses(self, user_id: str) -> list:
        """获取用户的课程列表"""
        # 先检查用户自定义课程
        user_custom = self.courses["default"]["user_custom"].get(user_id, [])
        # 合并默认课程
        default_courses = self.courses["default"]["courses"]
        return list(set(default_courses + user_custom))

    def add_course(self, user_id: str, course_name: str):
        """添加新课"""
        if user_id not in self.courses["default"]["user_custom"]:
            self.courses["default"]["user_custom"][user_id] = []

        if course_name not in self.courses["default"]["user_custom"][user_id]:
            self.courses["default"]["user_custom"][user_id].append(course_name)
            self._save_courses()

    def remove_course(self, user_id: str, course_name: str):
        """删除课程（从用户列表中移除）"""
        # 从用户自定义课程中删除
        if user_id in self.courses["default"]["user_custom"]:
            if course_name in self.courses["default"]["user_custom"][user_id]:
                self.courses["default"]["user_custom"][user_id].remove(course_name)
                self._save_courses()
                logger.info(f"已从用户 {user_id} 的课程列表中删除: {course_name}")
                return True

        # 如果是默认课程，不能删除（可以提示或特殊处理）
        if course_name in self.courses["default"]["courses"]:
            logger.warning(f"不能删除默认课程: {course_name}")
            # 如果你想允许删除默认课程，也可以移除
            # self.courses["default"]["courses"].remove(course_name)
            # self._save_courses()
            return False

        return False

    def _save_courses(self):
        os.makedirs(os.path.dirname(self.courses_file), exist_ok=True)
        with open(self.courses_file, 'w') as f:
            json.dump(self.courses, f, indent=2)

course_service = CourseService()