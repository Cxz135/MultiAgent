#course_clf.py


from agents.base_agent import BaseAgent
from pydantic import BaseModel

from core.state import OverallState


class CourseMatchResult(BaseModel):
    matched: bool
    confidence: int
    suggested_course: str
    reason: str

class CourseClassifierAgent(BaseAgent):
    def __init__(self, model):
        super().__init__(model)
        self.existing_courses = []

    def update_courses(self, courses):
        self.existing_courses = courses

    def process(self, state: OverallState):
        pass

    def detect_match(self, filename, content, target_course):
        prompt = f"""
                现有课程：{', '.join(self.existing_courses)}
                目标课程：{target_course}
                文件名：{filename}
                文件内容预览：{content[:1000]}

                请判断这个文件是否应该放在{target_course}下。
                """
        structured_llm = self.model.with_structured_output(CourseMatchResult)
        return structured_llm.invoke(prompt)

