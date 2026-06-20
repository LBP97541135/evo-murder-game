"""
从前端 scriptData.ts 导入剧本到数据库。

用法: python -m scripts.import_scripts
"""

import sys
import os

# 确保能找到 api 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.db.models import get_session, Script, Character, init_db


FRONTEND_SCRIPTS = [
    {
        "id": "iron-avenue",
        "title": "锈铁大道",
        "subtitle": "The Rusted Avenue",
        "genre": "推理本",
        "difficulty": "进阶",
        "playerCount": 6,
        "players": "4-6人",
        "duration": "4-5小时",
        "rating": 4.9,
        "description": "停摆工厂、老旧宿舍与失踪名单被压在同一座锈色街区里，真相沿着管道缓慢回流。",
        "details": "玩家将进入一座被废弃工业区包围的小镇。六名角色都与十二年前的事故有关，而一份重新出现的值班名单让彼此的证词开始崩塌。剧本强调线索还原、时间线拼接和多轮反转。",
        "cover": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1200&h=1500&fit=crop&auto=format",
        "tags": ["工业氛围", "线索链", "反转强", "高复盘"],
        "roles": ["林砾", "周岚", "顾沉", "秦野", "沈禾", "陆弦"],
    },
    {
        "id": "black-archive",
        "title": "黑箱档案馆",
        "subtitle": "Black Archive",
        "genre": "情感本",
        "difficulty": "入门",
        "playerCount": 7,
        "players": "6-7人",
        "duration": "5-6小时",
        "rating": 4.8,
        "description": "灰尘、烛火与被封存的家族信件，把每个人拽回一段难以解释的旧日往事。",
        "details": "一座即将关闭的私人档案馆收到匿名捐赠，七封信分别写给七位从未见过彼此的人。随着馆藏开放，他们发现自己的家庭记忆来自同一个被隐瞒的夜晚。",
        "cover": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=1200&h=1500&fit=crop&auto=format",
        "tags": ["高沉浸", "氛围感", "情绪拉扯", "新手友好"],
        "roles": ["许知白", "程见夏", "闻舟", "苏杳", "江临", "唐穗", "宋遥"],
    },
    {
        "id": "mirror-parade",
        "title": "镜面游行",
        "subtitle": "Mirror Parade",
        "genre": "阵营本",
        "difficulty": "硬核",
        "playerCount": 8,
        "players": "7-9人",
        "duration": "6小时",
        "rating": 4.7,
        "description": "面具、反光和舞台灯把每次发言切成碎片，所有阵营都在互相借力与拆台。",
        "details": "城市庆典前夜，八位游行委员会成员被困在镜厅。每个人拥有公开身份、秘密立场与一次改变规则的机会，胜负取决于信息交换和阵营判断。",
        "cover": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=1200&h=1500&fit=crop&auto=format",
        "tags": ["阵营博弈", "控场强", "表演位", "高对抗"],
        "roles": ["白面", "红隼", "司钟人", "玻璃匠", "礼官", "无名客", "领舞者", "守门人"],
    },
    {
        "id": "salt-ward",
        "title": "盐雾病房",
        "subtitle": "Salt Ward",
        "genre": "推理本",
        "difficulty": "入门",
        "playerCount": 6,
        "players": "5-6人",
        "duration": "3.5小时",
        "rating": 4.6,
        "description": "潮湿长廊与失效监控构成一场节奏温和、适合新手入门的推理练习。",
        "details": "临海疗养院在台风夜失去供电，一名患者离奇消失。玩家需要在有限场景中核对病历、监控和口供，完成清晰但不失悬念的真相还原。",
        "cover": "https://images.unsplash.com/photo-1516738901171-8eb4fc13bd20?w=1200&h=1500&fit=crop&auto=format",
        "tags": ["新手友好", "节奏清晰", "信息适中"],
        "roles": ["值夜医生", "护士长", "摄影师", "病人家属", "维修工", "档案员"],
    },
    {
        "id": "wolf-assembly",
        "title": "狼群集会",
        "subtitle": "Wolf Assembly",
        "genre": "机制本",
        "difficulty": "进阶",
        "playerCount": 8,
        "players": "6-8人",
        "duration": "4.5小时",
        "rating": 4.5,
        "description": "围绕营地资源与夜巡制度展开博弈，角色推进与资源调度都要算得很细。",
        "details": "极寒营地即将断粮，成员必须在夜巡、交易和公共建设之间分配行动点。隐藏目标会不断改变合作关系，适合喜欢资源机制与临场谈判的玩家。",
        "cover": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=1200&h=1500&fit=crop&auto=format",
        "tags": ["机制感", "资源调度", "夜谈博弈"],
        "roles": ["哨兵", "猎人", "医师", "书记员", "炊事长", "向导", "商人", "流亡者"],
    },
    {
        "id": "paper-cathedral",
        "title": "纸穹教堂",
        "subtitle": "Paper Cathedral",
        "genre": "情感本",
        "difficulty": "硬核",
        "playerCount": 7,
        "players": "6-8人",
        "duration": "5.5小时",
        "rating": 4.9,
        "description": "一座被封死的旧教堂正在吞没记忆，人物关系和信仰冲突同时发酵。",
        "details": "七名故人因一场纪念仪式重返纸穹教堂。被删改的唱诗册、空白照片和不同版本的告解，将把他们带向关于牺牲与记忆的最终选择。",
        "cover": "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1200&h=1500&fit=crop&auto=format",
        "tags": ["重氛围", "高情绪", "禁忌感"],
        "roles": ["司祭", "修复师", "唱诗人", "建筑师", "记者", "守墓人", "归乡者"],
    },
]


DIFFICULTY_MAP = {
    "入门": "easy",
    "进阶": "medium",
    "硬核": "hard",
}


def import_scripts():
    """将前端剧本数据导入数据库。"""
    session = get_session()
    imported = 0
    updated = 0

    for data in FRONTEND_SCRIPTS:
        script_id = data["id"]
        existing = session.query(Script).filter(Script.id == script_id).first()

        duration_minutes = 120
        if data["duration"]:
            try:
                parts = data["duration"].replace("小时", "").split("-")
                duration_minutes = int(float(parts[-1]) * 60)
            except (ValueError, IndexError):
                duration_minutes = 240

        difficulty = DIFFICULTY_MAP.get(data["difficulty"], "medium")

        if existing:
            existing.title = data["title"]
            existing.description = data["details"]
            existing.global_story = data["description"]
            existing.genre = data["genre"]
            existing.difficulty = difficulty
            existing.duration = duration_minutes
            existing.player_count = data["playerCount"]
            existing.cover_image = data["cover"]
            existing.source_type = "imported"
            updated += 1
        else:
            script = Script(
                id=script_id,
                title=data["title"],
                description=data["details"],
                global_story=data["description"],
                genre=data["genre"],
                difficulty=difficulty,
                duration=duration_minutes,
                player_count=data["playerCount"],
                cover_image=data["cover"],
                cover_source="ai",
                source_type="imported",
            )
            session.add(script)
            imported += 1

        # 导入角色
        for i, role_name in enumerate(data.get("roles", [])):
            char_id = f"{script_id}_char_{i}"
            char_existing = session.query(Character).filter(Character.id == char_id).first()
            if not char_existing:
                char = Character(
                    id=char_id,
                    script_id=script_id,
                    name=role_name,
                    bio=f"{data['title']}的角色之一",
                    role_type="suspect",
                    is_player=True,
                )
                session.add(char)

    session.commit()
    total = imported + updated
    print(f"导入完成：新增 {imported} 个，更新 {updated} 个，共 {total} 个剧本")
    session.close()
    return total


if __name__ == "__main__":
    init_db()
    import_scripts()