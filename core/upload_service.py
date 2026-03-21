# core/upload_service.py

import os
from datetime import datetime
from rag.vector_store import VectorStoreService
from utils.logger import logger


class UploadService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.upload_base = "data/uploads"
        os.makedirs(self.upload_base, exist_ok=True)

    async def save_file(self, file, course: str, user_id: str):
        course_dir = os.path.join(self.upload_base, course)
        os.makedirs(course_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(course_dir, filename)

        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        return file_path

    async def process_upload(self, file, course: str, user_id: str):
        """
        处理上传：保存原始文件 + 向量化
        """
        try:
            # 1. 保存原始文件
            file_path = await self.save_file(file, course, user_id)

            # 2. 添加到向量库
            doc_ids = self.vector_store.add_document(
                file_path=file_path,
                course=course,
                user_id='default',
            )

            return {
                "status": "success",
                "course": course,
                "file_path": file_path,
                "doc_count": len(doc_ids) if doc_ids else 0,
                "message": f"文件已上传到课程【{course}】",
                "confidence": 100
            }

        except Exception as e:
            logger.error(f"上传失败: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def delete_document(self, file_path: str, course: str, user_id: str = 'default'):
        """
        删除单个文档
        """
        try:
            # 从向量库删除
            success = self.vector_store.delete_document(file_path, course, user_id)

            # 从文件系统删除
            if os.path.exists(file_path):
                os.remove(file_path)

            return {
                "status": "success" if success else "error",
                "file_path": file_path,
                "message": "文档已删除" if success else "删除失败"
            }

        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def delete_course_documents(self, course: str, user_id: str):
        """
        删除课程的所有文档
        """
        try:
            # 从向量库删除
            success = self.vector_store.delete_course_documents(course, user_id)

            # 删除课程文件夹
            course_dir = os.path.join(self.upload_base, course)
            if os.path.exists(course_dir):
                import shutil
                shutil.rmtree(course_dir)
            from core.course_service import course_service
            course_service.remove_course(user_id, course)

            return {
                "status": "success" if success else "error",
                "message": f"课程【{course}】已删除"
            }

        except Exception as e:
            logger.error(f"删除课程失败: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


upload_service = UploadService()

