"""
EvoMap Murder Game - Capsule Service

本地胶囊系统：Gene（原始经验）→ DM评审 → Capsule（普适经验资产）

核心流程：
  1. 局后复盘：Agent 自评生成 Gene
  2. DM 评审：DM-Agent 用 LLM 对 Gene 打分+点评
  3. 胶囊生成：高质量 Gene（score > 阈值）提炼为 Capsule
  4. 胶囊消费：新局开始前搜索匹配 Capsule，融入 Agent prompt
"""

import uuid
import json
import logging
from typing import Optional
from datetime import datetime, timezone

from api.db.models import get_session, GeneRecord, CapsuleRecord, AgentNode as AgentNodeModel
from api.llm.llm_service import respond_initial

logger = logging.getLogger(__name__)

# 胶囊生成阈值：综合评分（自评*0.3 + DM评分*0.7）超过此值才生成胶囊
CAPSULE_SCORE_THRESHOLD = 0.6


# ============================
# Gene 管理
# ============================

def create_gene(
    agent_node_id: str,
    session_id: str,
    script_id: str,
    signals: list,
    category: str,
    status: str,
    score: float,
    summary: str,
    detail: str = "",
) -> dict:
    """创建一条 Gene（原始经验记录）。"""
    gene_id = f"gene_{uuid.uuid4().hex[:8]}"

    db_session = get_session()
    try:
        gene = GeneRecord(
            id=gene_id,
            agent_node_id=agent_node_id,
            session_id=session_id,
            script_id=script_id,
            signals=signals,
            category=category,
            status=status,
            score=score,
            summary=summary,
            detail=detail,
        )
        db_session.add(gene)
        db_session.commit()

        return {
            "success": True,
            "gene_id": gene_id,
            "message": "Gene 创建成功",
        }
    except Exception as e:
        db_session.rollback()
        logger.error(f"创建 Gene 失败: {e}")
        return {"error": str(e)}
    finally:
        db_session.close()


def get_gene(gene_id: str) -> Optional[dict]:
    """获取 Gene 详情。"""
    db_session = get_session()
    try:
        gene = db_session.query(GeneRecord).filter(GeneRecord.id == gene_id).first()
        if not gene:
            return None
        return _gene_to_dict(gene)
    finally:
        db_session.close()


def list_genes(
    agent_node_id: Optional[str] = None,
    session_id: Optional[str] = None,
    category: Optional[str] = None,
    dm_reviewed: Optional[bool] = None,
    limit: int = 50,
) -> list:
    """列出 Gene 记录。"""
    db_session = get_session()
    try:
        query = db_session.query(GeneRecord)
        if agent_node_id:
            query = query.filter(GeneRecord.agent_node_id == agent_node_id)
        if session_id:
            query = query.filter(GeneRecord.session_id == session_id)
        if category:
            query = query.filter(GeneRecord.category == category)
        if dm_reviewed is not None:
            query = query.filter(GeneRecord.dm_reviewed == dm_reviewed)

        genes = query.order_by(GeneRecord.created_at.desc()).limit(limit).all()
        return [_gene_to_dict(g) for g in genes]
    finally:
        db_session.close()


# ============================
# DM 评审
# ============================

def dm_review_gene(gene_id: str, dm_node_id: str = "") -> dict:
    """DM 评审一条 Gene：用 LLM 打分+点评，返回评审结果。

    DM 掌握完整真相和所有角色秘密，评审最权威。
    评审维度：
      1. 经验是否准确（是否基于事实）
      2. 策略是否普适（是否可复用）
      3. 是否有改进空间
    """
    db_session = get_session()
    try:
        gene = db_session.query(GeneRecord).filter(GeneRecord.id == gene_id).first()
        if not gene:
            return {"error": "gene_not_found"}

        # 获取 Agent 信息
        agent = db_session.query(AgentNodeModel).filter(
            AgentNodeModel.node_id == gene.agent_node_id
        ).first()
        agent_role = agent.role if agent else "companion"
        agent_name = agent.name if agent else "Unknown"

        # 构建 DM 评审 prompt
        review_prompt = f"""你是剧本杀主持人（DM），正在评审一个{agent_role} Agent 的局后经验总结。

## Agent 信息
- 角色：{agent_role}
- 名称：{agent_name}
- 自评分数：{gene.score:.2f}
- 经验状态：{gene.status}

## 经验摘要
{gene.summary}

## 经验详情
{gene.detail or '（无详情）'}

## 评审要求
请从以下维度评审这条经验，输出 JSON 格式：

1. **准确性**（0-1）：经验是否基于事实，有无错误认知
2. **普适性**（0-1）：经验是否可复用到其他剧本/场景
3. **深度**（0-1）：经验是否有足够深度，还是表面观察
4. **改进空间**（0-1）：0=已完善，1=有很大改进空间
5. **综合评分**（0-1）：加权综合分
6. **评审意见**：简要点评（2-3句话）
7. **改进建议**：具体可操作的改进方向

请严格输出以下 JSON 格式，不要输出其他内容：
{{"accuracy": 0.8, "universality": 0.7, "depth": 0.6, "improvement_space": 0.3, "dm_score": 0.75, "comment": "评审意见", "suggestions": "改进建议"}}"""

        # 调用 LLM 进行评审
        review_text = respond_initial(
            system_prompt="你是剧本杀DM评审专家，负责评审Agent的局后经验。请严格按JSON格式输出。",
            user_message=review_prompt,
            temperature=0.3,
            max_tokens=1024,
        )

        # 解析 LLM 返回的 JSON
        try:
            # 尝试提取 JSON
            json_str = review_text.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()

            review_result = json.loads(json_str)
        except (json.JSONDecodeError, IndexError):
            # JSON 解析失败，使用默认评分
            logger.warning(f"DM 评审 JSON 解析失败，使用默认评分: {review_text[:200]}")
            review_result = {
                "accuracy": 0.5,
                "universality": 0.5,
                "depth": 0.5,
                "improvement_space": 0.5,
                "dm_score": 0.5,
                "comment": "评审结果解析失败，使用默认评分",
                "suggestions": "请确保经验总结格式规范",
            }

        # 更新 Gene 记录
        gene.dm_reviewed = True
        gene.dm_score = review_result.get("dm_score", 0.5)
        gene.dm_comment = review_result.get("comment", "")
        gene.dm_suggestions = review_result.get("suggestions", "")

        db_session.commit()

        return {
            "success": True,
            "gene_id": gene_id,
            "dm_score": gene.dm_score,
            "dm_comment": gene.dm_comment,
            "dm_suggestions": gene.dm_suggestions,
            "review_detail": review_result,
        }

    except Exception as e:
        db_session.rollback()
        logger.error(f"DM 评审失败: {e}")
        return {"error": str(e)}
    finally:
        db_session.close()


# ============================
# 胶囊生成
# ============================

def generate_capsule_from_gene(gene_id: str) -> dict:
    """从已评审的 Gene 生成胶囊。

    条件：综合评分 = 自评*0.3 + DM评分*0.7 > CAPSULE_SCORE_THRESHOLD
    """
    db_session = get_session()
    try:
        gene = db_session.query(GeneRecord).filter(GeneRecord.id == gene_id).first()
        if not gene:
            return {"error": "gene_not_found"}

        if not gene.dm_reviewed:
            return {"error": "gene_not_reviewed", "message": "Gene 尚未经过 DM 评审"}

        # 计算综合评分
        composite_score = gene.score * 0.3 + gene.dm_score * 0.7

        if composite_score < CAPSULE_SCORE_THRESHOLD:
            return {
                "error": "score_too_low",
                "composite_score": composite_score,
                "threshold": CAPSULE_SCORE_THRESHOLD,
                "message": f"综合评分 {composite_score:.2f} 低于阈值 {CAPSULE_SCORE_THRESHOLD}，不生成胶囊",
            }

        # 获取 Agent 信息
        agent = db_session.query(AgentNodeModel).filter(
            AgentNodeModel.node_id == gene.agent_node_id
        ).first()
        agent_role = agent.role if agent else "companion"

        # 用 LLM 从 Gene 提炼普适经验
        capsule_content = _extract_capsule_content(gene, agent_role)

        # 确定适用角色
        role_map = {
            "dm": ["dm"],
            "companion": ["companion"],
            "assistant": ["assistant"],
        }
        applicable_roles = role_map.get(agent_role, ["companion"])

        # 创建胶囊
        capsule_id = f"capsule_{uuid.uuid4().hex[:8]}"
        capsule = CapsuleRecord(
            id=capsule_id,
            gene_id=gene_id,
            publisher_id=gene.agent_node_id,
            publisher_role=agent_role,
            title=capsule_content.get("title", f"{agent_role}经验胶囊"),
            category=gene.category,
            signals=gene.signals,
            applicable_roles=applicable_roles,
            content=capsule_content.get("content", gene.summary),
            strategy=capsule_content.get("strategy", ""),
            examples=capsule_content.get("examples", ""),
            anti_patterns=capsule_content.get("anti_patterns", ""),
            score=composite_score,
            review_status="approved",
            reviewed_by="dm",
        )
        db_session.add(capsule)

        # 关联 Gene 到 Capsule
        gene.capsule_id = capsule_id

        db_session.commit()

        return {
            "success": True,
            "capsule_id": capsule_id,
            "composite_score": composite_score,
            "title": capsule.title,
            "message": "胶囊生成成功",
        }

    except Exception as e:
        db_session.rollback()
        logger.error(f"生成胶囊失败: {e}")
        return {"error": str(e)}
    finally:
        db_session.close()


def _extract_capsule_content(gene: GeneRecord, agent_role: str) -> dict:
    """用 LLM 从 Gene 提炼普适经验内容。"""
    prompt = f"""你是一个经验提炼专家，需要从一个{agent_role} Agent 的剧本杀局后经验中，提炼出普适可复用的经验胶囊。

## 原始经验
- 类别：{gene.category}
- 状态：{gene.status}
- 自评：{gene.score:.2f}
- 摘要：{gene.summary}
- 详情：{gene.detail or '无'}
- DM评审：{gene.dm_comment}
- DM建议：{gene.dm_suggestions}

## 提炼要求
请将这条具体经验提炼为普适经验，输出 JSON 格式：
1. **title**：胶囊标题（简洁，5-15字）
2. **content**：普适经验正文（200-400字，去掉剧本特定信息，保留可复用策略）
3. **strategy**：具体策略/方法（可操作步骤）
4. **examples**：使用示例（什么场景下应用这条经验）
5. **anti_patterns**：反面模式（什么情况下不应该用这条经验）

请严格输出 JSON 格式，不要输出其他内容：
{{"title": "...", "content": "...", "strategy": "...", "examples": "...", "anti_patterns": "..."}}"""

    result = respond_initial(
        system_prompt="你是经验提炼专家，负责将具体经验抽象为普适策略。请严格按JSON格式输出。",
        user_message=prompt,
        temperature=0.4,
        max_tokens=2048,
    )

    try:
        json_str = result.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
        return json.loads(json_str)
    except (json.JSONDecodeError, IndexError):
        logger.warning(f"胶囊内容 JSON 解析失败: {result[:200]}")
        return {
            "title": f"{agent_role}经验胶囊",
            "content": gene.summary,
            "strategy": gene.dm_suggestions or "",
            "examples": "",
            "anti_patterns": "",
        }


# ============================
# 胶囊搜索与消费
# ============================

def search_capsules(
    signals: Optional[list] = None,
    category: Optional[str] = None,
    applicable_role: Optional[str] = None,
    min_score: float = 0.0,
    limit: int = 10,
) -> list:
    """搜索匹配的胶囊。"""
    db_session = get_session()
    try:
        query = db_session.query(CapsuleRecord).filter(
            CapsuleRecord.review_status == "approved"
        )

        if category:
            query = query.filter(CapsuleRecord.category == category)
        if min_score > 0:
            query = query.filter(CapsuleRecord.score >= min_score)

        capsules = query.order_by(CapsuleRecord.score.desc()).limit(limit * 3).all()

        # 在内存中过滤 signals 和 applicable_roles（JSON 字段不方便 SQL 过滤）
        results = []
        for c in capsules:
            c_dict = _capsule_to_dict(c)

            # 过滤适用角色
            if applicable_role and applicable_role not in (c.applicable_roles or []):
                continue

            # 过滤信号匹配
            if signals:
                capsule_signals = set(c.signals or [])
                query_signals = set(signals)
                if not capsule_signals.intersection(query_signals):
                    continue

            results.append(c_dict)
            if len(results) >= limit:
                break

        return results
    finally:
        db_session.close()


def consume_capsule(capsule_id: str) -> Optional[str]:
    """消费一个胶囊，返回融入 prompt 的文本，并更新使用计数。"""
    db_session = get_session()
    try:
        capsule = db_session.query(CapsuleRecord).filter(CapsuleRecord.id == capsule_id).first()
        if not capsule:
            return None

        # 更新使用计数
        capsule.usage_count += 1
        db_session.commit()

        # 返回融入 prompt 的文本
        prompt_text = f"""## 经验胶囊：{capsule.title}
{capsule.content}"""
        if capsule.strategy:
            prompt_text += f"\n\n### 策略方法\n{capsule.strategy}"
        if capsule.examples:
            prompt_text += f"\n\n### 使用示例\n{capsule.examples}"
        if capsule.anti_patterns:
            prompt_text += f"\n\n### 避免事项\n{capsule.anti_patterns}"

        return prompt_text
    except Exception as e:
        db_session.rollback()
        logger.error(f"消费胶囊失败: {e}")
        return None
    finally:
        db_session.close()


def get_capsules_for_agent(agent_role: str, signals: list = None, limit: int = 5) -> str:
    """获取指定角色适用的所有胶囊，合并为一段 prompt 文本。

    在新局开始前调用，将胶囊经验融入 Agent 的 system prompt。
    """
    capsules = search_capsules(
        signals=signals,
        applicable_role=agent_role,
        min_score=CAPSULE_SCORE_THRESHOLD,
        limit=limit,
    )

    if not capsules:
        return ""

    parts = ["\n\n## 你从历史经验中积累的智慧："]
    for c in capsules:
        parts.append(f"\n### {c['title']}（评分:{c['score']:.2f}，使用{c['usageCount']}次）")
        parts.append(c["content"])
        if c.get("strategy"):
            parts.append(f"策略：{c['strategy']}")
        if c.get("antiPatterns"):
            parts.append(f"避免：{c['antiPatterns']}")

        # 记录消费
        consume_capsule(c["id"])

    return "\n".join(parts)


# ============================
# 胶囊管理
# ============================

def get_capsule(capsule_id: str) -> Optional[dict]:
    """获取胶囊详情。"""
    db_session = get_session()
    try:
        capsule = db_session.query(CapsuleRecord).filter(CapsuleRecord.id == capsule_id).first()
        if not capsule:
            return None
        return _capsule_to_dict(capsule)
    finally:
        db_session.close()


def list_capsules(
    category: Optional[str] = None,
    publisher_role: Optional[str] = None,
    review_status: Optional[str] = None,
    limit: int = 50,
) -> list:
    """列出胶囊记录。"""
    db_session = get_session()
    try:
        query = db_session.query(CapsuleRecord)
        if category:
            query = query.filter(CapsuleRecord.category == category)
        if publisher_role:
            query = query.filter(CapsuleRecord.publisher_role == publisher_role)
        if review_status:
            query = query.filter(CapsuleRecord.review_status == review_status)

        capsules = query.order_by(CapsuleRecord.score.desc()).limit(limit).all()
        return [_capsule_to_dict(c) for c in capsules]
    finally:
        db_session.close()


def delete_capsule(capsule_id: str) -> dict:
    """删除胶囊。"""
    db_session = get_session()
    try:
        capsule = db_session.query(CapsuleRecord).filter(CapsuleRecord.id == capsule_id).first()
        if not capsule:
            return {"error": "capsule_not_found"}

        # 解除 Gene 关联
        if capsule.gene_id:
            gene = db_session.query(GeneRecord).filter(GeneRecord.id == capsule.gene_id).first()
            if gene:
                gene.capsule_id = ""

        db_session.delete(capsule)
        db_session.commit()
        return {"success": True, "message": "胶囊已删除"}
    except Exception as e:
        db_session.rollback()
        return {"error": str(e)}
    finally:
        db_session.close()


# ============================
# 一键流程：复盘 → 评审 → 生成胶囊
# ============================

def review_and_generate_capsules(session_id: str, script_id: str = "") -> dict:
    """局后复盘一键流程：为所有 Agent 生成 Gene → DM 评审 → 生成胶囊。

    在 review 阶段自动调用。
    """
    from api.orchestrator import orchestrator

    results = {
        "session_id": session_id,
        "genes": [],
        "capsules": [],
        "errors": [],
    }

    # 1. 为每个 Agent 生成 Gene
    for key, agent in orchestrator.agents.items():
        if agent.role.value == "assistant":
            continue  # 助手不参与游戏复盘

        # 构建经验信号
        signals = agent.domains.copy()
        if script_id:
            signals.append(f"script:{script_id}")

        # 构建经验摘要
        if agent.role.value == "dm":
            summary = f"DM主持复盘 - 会话{session_id}"
            category = "hosting"
        else:
            summary = f"角色扮演复盘 - 会话{session_id}"
            category = "role-playing"

        # 创建 Gene
        gene_result = create_gene(
            agent_node_id=agent.node_id,
            session_id=session_id,
            script_id=script_id,
            signals=signals,
            category=category,
            status="completed",
            score=0.7,  # 默认自评分，后续可由 Agent 自评覆盖
            summary=summary,
            detail="",  # 可由 Agent 自评填充
        )

        if "error" in gene_result:
            results["errors"].append(f"Agent {agent.name} Gene 创建失败: {gene_result['error']}")
            continue

        results["genes"].append(gene_result)

    # 2. DM 评审所有 Gene
    for gene_info in results["genes"]:
        gene_id = gene_info["gene_id"]
        review_result = dm_review_gene(gene_id)

        if "error" in review_result:
            results["errors"].append(f"Gene {gene_id} DM评审失败: {review_result['error']}")
            continue

        gene_info["dm_review"] = review_result

        # 3. 尝试生成胶囊
        capsule_result = generate_capsule_from_gene(gene_id)

        if capsule_result.get("success"):
            results["capsules"].append(capsule_result)
        elif capsule_result.get("error") == "score_too_low":
            gene_info["capsule_skip_reason"] = f"评分不足: {capsule_result.get('composite_score', 0):.2f}"
        else:
            results["errors"].append(f"Gene {gene_id} 胶囊生成失败: {capsule_result.get('error', 'unknown')}")

    return results


# ============================
# 数据转换
# ============================

def _gene_to_dict(gene: GeneRecord) -> dict:
    return {
        "id": gene.id,
        "agentNodeId": gene.agent_node_id,
        "sessionId": gene.session_id,
        "scriptId": gene.script_id,
        "signals": gene.signals or [],
        "category": gene.category,
        "status": gene.status,
        "score": gene.score,
        "summary": gene.summary,
        "detail": gene.detail,
        "dmReviewed": gene.dm_reviewed,
        "dmScore": gene.dm_score,
        "dmComment": gene.dm_comment,
        "dmSuggestions": gene.dm_suggestions,
        "capsuleId": gene.capsule_id,
        "createdAt": gene.created_at.isoformat() if gene.created_at else "",
    }


def _capsule_to_dict(capsule: CapsuleRecord) -> dict:
    return {
        "id": capsule.id,
        "geneId": capsule.gene_id,
        "publisherId": capsule.publisher_id,
        "publisherRole": capsule.publisher_role,
        "title": capsule.title,
        "category": capsule.category,
        "signals": capsule.signals or [],
        "applicableRoles": capsule.applicable_roles or [],
        "content": capsule.content,
        "strategy": capsule.strategy,
        "examples": capsule.examples,
        "antiPatterns": capsule.anti_patterns,
        "score": capsule.score,
        "usageCount": capsule.usage_count,
        "effectiveness": capsule.effectiveness,
        "source": capsule.source,
        "reviewStatus": capsule.review_status,
        "reviewedBy": capsule.reviewed_by,
        "createdAt": capsule.created_at.isoformat() if capsule.created_at else "",
        "updatedAt": capsule.updated_at.isoformat() if capsule.updated_at else "",
    }
