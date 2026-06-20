"""
EvoMap Murder Game - Capsule Routes

胶囊系统 API：Gene 管理、DM 评审、胶囊生成/搜索/消费。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.capsules.capsule_service import (
    create_gene,
    get_gene,
    list_genes,
    dm_review_gene,
    generate_capsule_from_gene,
    search_capsules,
    get_capsule,
    list_capsules,
    delete_capsule,
    consume_capsule,
    get_capsules_for_agent,
    review_and_generate_capsules,
)

router = APIRouter()


# ============================
# 请求模型
# ============================

class GeneCreateRequest(BaseModel):
    agent_node_id: str
    session_id: str = ""
    script_id: str = ""
    signals: list = []
    category: str = ""
    status: str = "success"
    score: float = 0.7
    summary: str = ""
    detail: str = ""


class GeneReviewRequest(BaseModel):
    dm_node_id: str = ""


class CapsuleSearchRequest(BaseModel):
    signals: Optional[list] = None
    category: Optional[str] = None
    applicable_role: Optional[str] = None
    min_score: float = 0.0
    limit: int = 10


class CapsuleConsumeRequest(BaseModel):
    agent_role: str
    signals: Optional[list] = None
    limit: int = 5


class ReviewAndGenerateRequest(BaseModel):
    session_id: str
    script_id: str = ""


# ============================
# Gene 管理
# ============================

@router.post("/genes")
async def create_gene_record(req: GeneCreateRequest):
    """创建一条 Gene（原始经验记录）。"""
    result = create_gene(
        agent_node_id=req.agent_node_id,
        session_id=req.session_id,
        script_id=req.script_id,
        signals=req.signals,
        category=req.category,
        status=req.status,
        score=req.score,
        summary=req.summary,
        detail=req.detail,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


@router.get("/genes/{gene_id}")
async def get_gene_record(gene_id: str):
    """获取 Gene 详情。"""
    result = get_gene(gene_id)
    if not result:
        raise HTTPException(status_code=404, detail="Gene not found")
    return result


@router.get("/genes")
async def list_gene_records(
    agent_node_id: Optional[str] = None,
    session_id: Optional[str] = None,
    category: Optional[str] = None,
    dm_reviewed: Optional[bool] = None,
    limit: int = 50,
):
    """列出 Gene 记录。"""
    return list_genes(
        agent_node_id=agent_node_id,
        session_id=session_id,
        category=category,
        dm_reviewed=dm_reviewed,
        limit=limit,
    )


# ============================
# DM 评审
# ============================

@router.post("/genes/{gene_id}/review")
async def review_gene(gene_id: str, req: GeneReviewRequest):
    """DM 评审一条 Gene。"""
    result = dm_review_gene(gene_id, dm_node_id=req.dm_node_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


# ============================
# 胶囊生成
# ============================

@router.post("/genes/{gene_id}/generate-capsule")
async def generate_capsule(gene_id: str):
    """从已评审的 Gene 生成胶囊。"""
    result = generate_capsule_from_gene(gene_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


# ============================
# 胶囊搜索与消费
# ============================

@router.post("/search")
async def search_capsule_records(req: CapsuleSearchRequest):
    """搜索匹配的胶囊。"""
    return search_capsules(
        signals=req.signals,
        category=req.category,
        applicable_role=req.applicable_role,
        min_score=req.min_score,
        limit=req.limit,
    )


@router.get("/capsules/{capsule_id}")
async def get_capsule_record(capsule_id: str):
    """获取胶囊详情。"""
    result = get_capsule(capsule_id)
    if not result:
        raise HTTPException(status_code=404, detail="Capsule not found")
    return result


@router.get("/capsules")
async def list_capsule_records(
    category: Optional[str] = None,
    publisher_role: Optional[str] = None,
    review_status: Optional[str] = None,
    limit: int = 50,
):
    """列出胶囊记录。"""
    return list_capsules(
        category=category,
        publisher_role=publisher_role,
        review_status=review_status,
        limit=limit,
    )


@router.delete("/capsules/{capsule_id}")
async def delete_capsule_record(capsule_id: str):
    """删除胶囊。"""
    result = delete_capsule(capsule_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result)
    return result


@router.post("/consume")
async def consume_capsule_for_agent(req: CapsuleConsumeRequest):
    """获取指定角色适用的胶囊，返回融入 prompt 的文本。"""
    prompt_text = get_capsules_for_agent(
        agent_role=req.agent_role,
        signals=req.signals,
        limit=req.limit,
    )
    return {
        "success": True,
        "prompt_text": prompt_text,
        "has_capsules": bool(prompt_text),
    }


# ============================
# 一键流程
# ============================

@router.post("/review-and-generate")
async def review_and_generate(req: ReviewAndGenerateRequest):
    """局后复盘一键流程：生成 Gene → DM 评审 → 生成胶囊。"""
    result = review_and_generate_capsules(
        session_id=req.session_id,
        script_id=req.script_id,
    )
    return result
