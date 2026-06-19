"""
EvoMap Murder Game - Spoiler Story Routes

剧透故事管理：保存、列表、详情、删除、更新。
"""

from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, HTTPException

from api.db.models import (
    get_session,
    Script, SpoilerStory,
    spoiler_story_to_dict, dict_to_spoiler_story,
)

router = APIRouter()


# ============================
# API 端点
# ============================

@router.post("/save")
async def save_spoiler_story(data: dict):
    """保存剧透故事到数据库。"""
    session = get_session()
    try:
        script_id = data.get("scriptId")
        if not script_id:
            raise HTTPException(status_code=400, detail="剧本ID不能为空")

        script = session.query(Script).filter(Script.id == script_id).first()
        if not script:
            raise HTTPException(status_code=404, detail="剧本不存在")

        story = dict_to_spoiler_story(data, script_id)

        # 自动生成标题（如果为空）
        if not story.title or story.title == "剧透故事":
            count = session.query(SpoilerStory).filter(
                SpoilerStory.script_id == script_id
            ).count()
            story.title = f"《{script.title}》剧透故事 #{count + 1}"

        session.add(story)
        session.commit()
        session.refresh(story)

        return {
            "success": True,
            "message": "剧透故事保存成功",
            "story": spoiler_story_to_dict(story),
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"保存剧透故事失败: {str(e)}")
    finally:
        session.close()


@router.get("/{script_id}")
async def get_spoiler_stories(script_id: str):
    """获取指定剧本的所有剧透故事（按生成时间倒序）。"""
    session = get_session()
    try:
        script = session.query(Script).filter(Script.id == script_id).first()
        if not script:
            raise HTTPException(status_code=404, detail="剧本不存在")

        stories = session.query(SpoilerStory).filter(
            SpoilerStory.script_id == script_id
        ).order_by(SpoilerStory.generated_at.desc()).all()

        stories_data = [spoiler_story_to_dict(s) for s in stories]

        return {
            "success": True,
            "stories": stories_data,
            "script_title": script.title,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取剧透故事失败: {str(e)}")
    finally:
        session.close()


@router.get("/story/{story_id}")
async def get_spoiler_story(story_id: int):
    """获取指定的剧透故事详情。"""
    session = get_session()
    try:
        story = session.query(SpoilerStory).filter(SpoilerStory.id == story_id).first()
        if not story:
            raise HTTPException(status_code=404, detail="剧透故事不存在")

        return {
            "success": True,
            "story": spoiler_story_to_dict(story),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取剧透故事详情失败: {str(e)}")
    finally:
        session.close()


@router.put("/{story_id}")
async def update_spoiler_story(story_id: int, data: dict):
    """更新剧透故事。"""
    session = get_session()
    try:
        story = session.query(SpoilerStory).filter(SpoilerStory.id == story_id).first()
        if not story:
            raise HTTPException(status_code=404, detail="剧透故事不存在")

        if "title" in data:
            story.title = data["title"]
        if "content" in data:
            story.content = data["content"]
            story.word_count = len(data["content"])

        session.commit()
        session.refresh(story)

        return {
            "success": True,
            "message": "剧透故事更新成功",
            "story": spoiler_story_to_dict(story),
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"更新剧透故事失败: {str(e)}")
    finally:
        session.close()


@router.delete("/{story_id}")
async def delete_spoiler_story(story_id: int):
    """删除指定的剧透故事。"""
    session = get_session()
    try:
        story = session.query(SpoilerStory).filter(SpoilerStory.id == story_id).first()
        if not story:
            raise HTTPException(status_code=404, detail="剧透故事不存在")

        title = story.title
        session.delete(story)
        session.commit()

        return {"success": True, "message": f"剧透故事 '{title}' 删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"删除剧透故事失败: {str(e)}")
    finally:
        session.close()


@router.post("/batch-delete")
async def batch_delete_spoiler_stories(story_ids: List[int]):
    """批量删除剧透故事。"""
    session = get_session()
    try:
        deleted = 0
        failed = []

        for sid in story_ids:
            try:
                story = session.query(SpoilerStory).filter(SpoilerStory.id == sid).first()
                if story:
                    session.delete(story)
                    deleted += 1
                else:
                    failed.append(sid)
            except Exception as e:
                failed.append(sid)

        session.commit()

        return {
            "success": True,
            "message": f"批量删除完成: 成功 {deleted} 个, 失败 {len(failed)} 个",
            "deleted_count": deleted,
            "failed_ids": failed,
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"批量删除失败: {str(e)}")
    finally:
        session.close()