#course_manager.py


from agents.base_agent import BaseAgent
from core.state import OverallState

class CourseManager(BaseAgent):
    def __init__(self, model):
        super().__init__(model)
        self.courses = set()

    def process(self, state: OverallState):
        pass

    def add_course(self, filename, content):
        prompt = f"""
                文件名：{filename}
                内容预览：{content[:500]}

                如果这个文件属于一门新课，请给出课程名称。如果属于现有课程，返回现有课程名。
                现有课程：{', '.join(self.courses)}
                """

        suggested = self.model.invoke(prompt).content.strip()

        if suggested not in self.courses:
            # 询问用户是否创建新课
            return {"action": "ask", "suggested": suggested}

        return {"action": "use_existing", "course": suggested}