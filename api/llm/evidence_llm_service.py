"""
EvoMap Murder Game - Evidence LLM Service

证物出示时的AI角色反应生成。
从 ai-murder-mystery 的 evidence_llm_service.py 迁移核心逻辑。

⚠️ 此文件位于 api/llm/ 下，属于 llm 模块的职责范围。
这里只保留了核心的 prompt 构建和反应解析逻辑，
实际的 LLM 调用需要对接 api/llm/llm_service.py 的三层管道。

其他同学请在此文件中实现 LLM 调用部分的对接。
"""

from typing import Dict, Any, List, Tuple, Optional
import json
import re


async def invoke_ai_for_evidence_presentation(
    evidence: Dict[str, Any],
    presented_to: str,
    presented_by: str,
    text_content: Optional[str] = None,
    presentation_context: Optional[str] = None,
    target_actor: Optional[Dict] = None,
    current_actor: Optional[Dict] = None,
) -> Tuple[str, str, List[str], List[str]]:
    """
    向角色展示证物时的AI处理。

    Returns:
        Tuple[ai_response, reaction_type, new_evidences, updated_info]
    """
    try:
        # 构建AI提示词
        prompt = build_evidence_presentation_prompt(
            evidence, presented_to, presented_by, text_content, presentation_context, target_actor
        )

        # ⚠️ TODO: 其他同学请在这里对接 llm_service.py 的三层管道
        # 当前使用简化版调用作为占位
        from api.llm.llm_service import respond_initial
        ai_response = respond_initial(
            system_prompt="你是剧本杀中的角色扮演Agent，请对证物做出合理反应。",
            user_message=prompt,
            skip_critique=True,  # 证物反应场景下先跳过critique，减少token消耗
        )

        # 解析AI响应，确定反应类型和后续动作
        reaction_type, new_evidences, updated_info = parse_evidence_response(ai_response, evidence, presented_to)

        return ai_response, reaction_type, new_evidences, updated_info

    except Exception as e:
        print(f"❌ 证物展示AI调用失败: {str(e)}")
        return f"对于{evidence.get('name', '这个证物')}，我没有什么特别的想法。", "basic", [], []


def build_evidence_presentation_prompt(
    evidence: Dict[str, Any],
    presented_to: str,
    presented_by: str,
    text_content: Optional[str] = None,
    presentation_context: Optional[str] = None,
    target_actor: Optional[Dict] = None,
) -> str:
    """构建证物展示的AI提示词（从ai-murder-mystery原样迁移）。"""

    evidence_info = f"""
【展示的证物】
名称：{evidence.get('name', '未知证物')}
类别：{evidence.get('category', 'physical')}
基础描述：{evidence.get('basicDescription', '')}
"""

    if evidence.get('detailedDescription') and evidence.get('unlockLevel', 1) >= 2:
        evidence_info += f"专业分析：{evidence['detailedDescription']}\n"

    if evidence.get('deepDescription') and evidence.get('unlockLevel', 1) >= 3:
        evidence_info += f"深度发现：{evidence['deepDescription']}\n"

    importance_map = {'low': '一般', 'medium': '重要', 'high': '关键', 'critical': '决定性'}
    evidence_info += f"重要程度：{importance_map.get(evidence.get('importance', 'medium'), '重要')}\n"

    if evidence.get('relatedActors'):
        evidence_info += f"相关角色：{', '.join(evidence['relatedActors'])}\n"

    dialogue_context = f"""
【对话情境】
{presented_by}正在向{presented_to}展示证物。
"""
    if text_content:
        dialogue_context += f"展示时说：{text_content}\n"
    if presentation_context:
        dialogue_context += f"对话背景：{presentation_context}\n"

    role_guidance = ""
    if target_actor:
        role_guidance = f"""
【你的角色设定】
你是{target_actor.get('name', '')}。
背景：{target_actor.get('bio', '')}
性格：{target_actor.get('personality', '')}
当前状态：{target_actor.get('context', '')}
秘密信息：{target_actor.get('secret', '')}
行为限制：{target_actor.get('violation', '')}
"""

    reaction_guidance = """
【反应指导】
请根据你的角色设定和这个证物的相关性做出合理反应：

1. 如果这个证物与你无关或者你确实不了解：
   - 给出诚实的回应，如"我没见过这个"、"这跟我没关系"
   - 保持角色一致性

2. 如果这个证物与你有关但不构成威胁：
   - 可以提供一些你知道的信息
   - 保持合作态度，但不要透露敏感信息

3. 如果这个证物对你的秘密构成威胁：
   - 表现出紧张、回避或防御的情绪
   - 尝试转移话题或给出模糊的回答
   - 严格遵守你的违规限制，不能直接承认敏感信息

4. 如果这是决定性证据且你无法再隐瞒：
   - 表现出情绪崩溃或愤怒
   - 可能被迫透露一些重要信息
   - 仍然要符合角色性格特点

【回应要求】
- 保持角色的性格特征和说话方式
- 不要直接违反你的违规限制
- 根据证物的重要程度调整反应强度
- 如果证物确实相关，可以在合理范围内提供新信息
- 避免过于配合或过于防御，保持真实感
"""

    if target_actor:
        if target_actor.get('isKiller'):
            reaction_guidance += """
【凶手特殊指导】
- 绝对不能直接承认犯罪行为
- 对威胁性证物要表现出更强的防御性
- 可以表现出愤怒或试图反驳
- 在极端压力下可能泄露部分信息，但要保持最后的底线
"""
        elif target_actor.get('isPartner') or target_actor.get('isAssistant'):
            reaction_guidance += """
【搭档特殊指导】
- 以专业、客观的态度分析证物
- 可以提供技术性的见解和建议
- 建议下一步的调查方向
"""

    full_prompt = f"""
{evidence_info}

{dialogue_context}

{role_guidance}

{reaction_guidance}

请现在做出你的回应。记住要符合角色设定，不要泄露不应该知道的信息。
"""

    return full_prompt


def parse_evidence_response(
    ai_response: str,
    evidence: Dict[str, Any],
    presented_to: str,
) -> Tuple[str, List[str], List[str]]:
    """解析AI响应，确定反应类型和后续动作。"""

    reaction_type = "basic"
    new_evidences = []
    updated_info = []

    nervous_words = ["紧张", "不安", "心慌", "害怕", "担心", "焦虑"]
    angry_words = ["愤怒", "生气", "恼火", "气愤", "暴怒", "愤恨"]
    defensive_words = ["否认", "不是", "绝对没有", "怎么可能", "不关我事", "冤枉"]
    breakdown_words = ["崩溃", "受不了", "我承认", "好吧", "是的", "没错"]

    nervous_count = sum(1 for word in nervous_words if word in ai_response)
    angry_count = sum(1 for word in angry_words if word in ai_response)
    defensive_count = sum(1 for word in defensive_words if word in ai_response)
    breakdown_count = sum(1 for word in breakdown_words if word in ai_response)

    if breakdown_count >= 2 or ("承认" in ai_response and "是的" in ai_response):
        reaction_type = "breakthrough"
        if evidence.get('importance') in ['high', 'critical']:
            updated_info.append(f"{presented_to}的重要供词")
    elif (nervous_count + angry_count + defensive_count) >= 2 or len(ai_response) > 100:
        reaction_type = "contradiction"
        if evidence.get('unlockLevel', 1) < 2:
            updated_info.append(f"从{presented_to}的反应中获得新线索")
    else:
        reaction_type = "basic"

    potential_evidences = extract_potential_evidences(ai_response)
    new_evidences.extend(potential_evidences)

    return reaction_type, new_evidences, updated_info


def extract_potential_evidences(text: str) -> List[str]:
    """从AI响应中提取可能的新证物。"""
    potential_evidences = []

    item_patterns = [
        r"那个([^，。！？\s]+)",
        r"一个([^，。！？\s]+)",
        r"这个([^，。！？\s]+)",
        r"([^，。！？\s]*刀[^，。！？\s]*)",
        r"([^，。！？\s]*枪[^，。！？\s]*)",
        r"([^，。！？\s]*信[^，。！？\s]*)",
        r"([^，。！？\s]*照片[^，。！？\s]*)",
        r"([^，。！？\s]*文件[^，。！？\s]*)",
        r"([^，。！？\s]*钥匙[^，。！？\s]*)",
        r"([^，。！？\s]*手机[^，。！？\s]*)",
    ]

    for pattern in item_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) >= 2 and len(match) <= 10:
                potential_evidences.append(match)

    potential_evidences = list(set(potential_evidences))[:3]
    return potential_evidences
