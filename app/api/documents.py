#app/api/documents.py


from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from core import upload_service
from core.upload_service import upload_service
from core.course_service import course_service
from utils.logger import logger
import os

router = APIRouter(prefix = "/documents", tags = ["documents"])


@router.post("/courses/add")
async def add_course(request: Request, data: dict):
    """添加新课程"""
    user_id = "default"   #request.session.get("user_id", "default")
    course_name = data.get("course_name")

    # 创建课程文件夹
    course_dir = os.path.join("data/uploads", course_name)
    os.makedirs(course_dir, exist_ok=True)

    # 添加到课程服务
    course_service.add_course(user_id, course_name)

    return {"status": "success"}


@router.post("/courses/delete")
async def delete_course(request: Request, data: dict):
    """删除课程（包括所有文件）"""
    data = await request.json()
    course_name = data.get("course_name")
    user_id = "default"   #request.session.get("user_id", "default")

    # 调用 upload_service 的方法
    result = await upload_service.delete_course_documents(course_name, user_id)

    return result

@router.post("/upload")
async def upload(
        request: Request,
        file: UploadFile = File(...),
        target_course: str = Form(...),
):
    user_id = "default"   #request.session.get("user_id", "default")
    result = await upload_service.process_upload(file, target_course, user_id)

    if result.get("status") == "need_confirmation":
        return {
            "status": "confirm",
            "message": f"这个文件可能属于【{result.get('suggested_course')}】，要创建新课吗？",
            "data": {
                "suggested_course": result.get("suggested_course"),
                "original_course": target_course
            }
        }

        # 处理成功的情况
    if result.get("status") == "success":
        course_name = result.get("course")

        # 如果是新课，添加到用户课程列表
        if course_name not in course_service.get_user_courses(user_id):
            course_service.add_course(user_id, course_name)
        request.session["current_course"] = course_name

        return {
            "status": "success",
            "message": f"文件已上传到【{course_name}】课程",
            "course": course_name,
            "confidence": result.get("confidence", 100)
        }

        # 处理错误的情况
    return {
        "status": "error",
        "message": result.get("message", "上传失败")
    }


@router.get("/list")
async def list_documents(course: str = None):
    """列出指定课程的文件"""
    upload_dir = "data/uploads"
    if not os.path.exists(upload_dir):
        return {"files": []}

    if course:
        # 只返回指定课程的文件
        course_dir = os.path.join(upload_dir, course)
        if os.path.exists(course_dir):
            files = os.listdir(course_dir)
            return {
                "files": [
                    {"name": f, "course": course, "path": os.path.join(course_dir, f)}
                    for f in files
                ]
            }
        return {"files": []}

    # 返回所有课程的文件
    all_files = []
    for course_name in os.listdir(upload_dir):
        course_path = os.path.join(upload_dir, course_name)
        if os.path.isdir(course_path):
            for f in os.listdir(course_path):
                all_files.append({"name": f, "course": course_name})

    return {"files": all_files}

@router.get("/courses")
async def get_courses(request: Request):
    user_id = "default"   #request.session.get("user_id", "default")
    courses = course_service.get_user_courses(user_id)
    return {"courses": courses}


@router.delete("/delete/{course}/{filename}")
async def delete_document(course: str, filename: str, request: Request):
    """删除指定文档（从向量库和文件系统）"""
    user_id = "default"   #request.session.get("user_id", "default")
    file_path = os.path.join("data/uploads", course, filename)
    result = await upload_service.delete_document(file_path, course, user_id)
    return result


@router.get("/view")
async def view_file(course: str, file: str):
    """预览文件"""
    file_path = os.path.join("data/uploads", course, file)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    # 根据文件类型返回不同内容
    if file.endswith('.pdf'):
        # 返回 PDF 文件
        return FileResponse(file_path, media_type='application/pdf')
    elif file.endswith('.txt'):
        # 返回文本内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(f"<pre>{content}</pre>")

    return FileResponse(file_path)


@router.get("/download")
async def download_file(course: str, file: str):
    """下载文件"""
    # 安全检查：防止路径遍历攻击
    if ".." in course or ".." in file:
        raise HTTPException(status_code=400, detail="无效的文件名")

    file_path = os.path.join("data/uploads", course, file)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    # 获取原始文件名（去掉时间戳前缀）
    # 文件名格式：20260319_170107_4. Data Preprocessing.pdf
    # 提取原始文件名：4. Data Preprocessing.pdf
    parts = file.split("_", 2)
    original_filename = parts[2] if len(parts) > 2 else file

    return FileResponse(
        file_path,
        filename=original_filename,
        media_type='application/octet-stream'
    )



