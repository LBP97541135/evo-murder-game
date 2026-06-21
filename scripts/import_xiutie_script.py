"""
锈铁大道 · 消失的3分钟 — 剧本数据库导入脚本
覆盖现存的 xiutie-avenue-missing-three-minutes 记录。
"""
import json
import sys
from pathlib import Path

# 确保能找到 api 模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from api.db.models import get_session, Script, Character, dict_to_script, dict_to_character

SCRIPT_ID = "xiutie-avenue-missing-three-minutes"

# ============================
# 剧本元数据
# ============================
script_data = {
    "id": SCRIPT_ID,
    "title": "锈铁大道 · 消失的3分钟",
    "description": "十二年前，锈铁大道厂区发生了一起爆炸事故。事故造成3人死亡、12人受伤，官方结论是「设备老化导致气体泄漏」。但事故当晚22:41至22:44的三分钟监控记录被人为删除。今晚，当年的当事人被匿名召集回废弃厂区，真相即将浮出水面……",
    "author": "EvoMap",
    "version": "2.0.0",
    "sourceType": "manual",
    "globalStory": (
        "十二年前，锈铁大道厂区在一场爆炸事故中化为废墟。\n\n"
        "官方结论：设备老化导致气体泄漏，引发爆炸。\n"
        "但事故当晚22:41至22:44的三分钟监控记录被人为删除。\n"
        "这消失的三分钟里，究竟发生了什么？\n\n"
        "今晚，七个人被匿名信召集回锈铁大道废弃厂区——\n"
        "当年负责门禁的维修员、追踪旧案的调查记者、\n"
        "值夜班的护士、执行安全协议的前工头、\n"
        "改了证词的保安，以及自称「吹哨人」的顾沉。\n\n"
        "顾沉被发现死在了厂区控制室——后脑遭到钝器击打。\n"
        "他的U盘和笔记本里的关键文件被删除殆尽。\n"
        "消失的三分钟监控记录、被篡改的伤情报告、\n"
        "伪造的安全检测报告——这些线索在今晚交织成一张网。\n\n"
        "凶手就在你们中间。"
    ),
    "theme": "modern",
    "genre": "推理本",
    "difficulty": "hard",
    "duration": 120,
    "emotionLevel": 0.7,
    "inferenceLevel": 0.9,
    "horrorLevel": 0.3,
    "playerCount": 6,
    "fixedKiller": "周岚",
}

# ============================
# 角色数据（来自人物设定.json）
# ============================
characters_data = [
    {
        "id": "char_zhouye",
        "name": "周野",
        "bio": "32岁，门禁维修员。沉默寡言，技术精湛，12年前负责锈铁大道厂区的门禁系统维护。爆炸事故后离开厂区，在城区开了一家锁匠铺。今晚被匿名信召集回来，信中承诺「找到谁下令删除了那3分钟监控记录」。",
        "personality": "沉默、警觉、技术宅。说话简短直接，不喜欢绕弯子。对锁和门禁系统有近乎偏执的专业兴趣。面对质问时会下意识摸口袋里的工具，紧张时语速加快。",
        "context": "你是周野，12年前负责锈铁大道厂区门禁系统的维修员。爆炸事故后，有人付钱让你删除了22:41到22:44这3分钟的监控记录。你一直以为那只是普通的设备故障记录，直到最近发现——那3分钟记录的是有人进入厂区放置爆炸物的画面。\n\n你父亲周建国是当年的厂区安全主管，他命令你删除记录后不久就「意外」去世了。你一直怀疑父亲的死与掩盖真相有关。今晚来锈铁大道，是想找到谁下令删除记录，为父亲正名。\n\n但你也有秘密：23:00你潜入控制室，用扳手撬开了文件柜，想偷回当年自己删除记录的操作日志。你撬柜时顾沉就在房间里，他被安眠药弄得昏昏沉沉，被你的动静惊醒但没看清你的脸。你慌忙从窗户离开，留下了一把带指纹的扳手。",
        "secret": "你23:00潜入控制室用扳手撬开了文件柜，顾沉被惊醒但没看清你。你从窗户逃离，扳手留在了现场。你删除监控记录是受父亲命令，而父亲在事故后「意外」死亡。",
        "violation": "不能承认你今晚潜入过控制室；不能承认你撬了文件柜；不能说出你父亲命令你删除记录的事；不能透露你怀疑姐姐周岚隐瞒了什么。",
        "isVictim": False, "isKiller": False, "isAssistant": False,
        "isPlayer": False, "isPartner": False, "isDetective": False,
        "roleType": "嫌疑人",
        "image": "",
    },
    {
        "id": "char_shenhe",
        "name": "沈禾",
        "bio": "35岁，调查记者。三年前开始追踪锈铁大道旧案，发表了多篇深度报道，被誉为「真相猎手」。但她的调查似乎总是差一步——每次接近核心证据时就会遇到「巧合」的阻碍。",
        "personality": "犀利、自信、善于追问。说话时喜欢直视对方眼睛，擅长用沉默制造压力。但被问到自己的资金来源时会变得闪烁其词，偶尔流露出不自然的笑容。",
        "context": "你是沈禾，调查记者。三年前你开始追踪锈铁大道旧案，外界以为你是正义的化身，但真相是：你第一年就收到了一笔巨额封口费，条件是「调查可以继续，但永远不要找到关键证据」。\n\n你接受了。三年来，你的「调查」实际上在帮掩盖——你故意引导公众关注错误的方向，每次接近真相就巧妙地转向。但顾沉发现了你的资金来源，今晚他威胁要公开你收封口费的事。\n\n23:10你闯入控制室与顾沉对峙。你恳求他不要公开，但他态度强硬。争吵升级为推搡，顾沉被你推倒撞到桌角，后脑左侧磕出了血。你吓坏了，慌忙离开。你不知道他后来怎样了——你离开时他还活着，虽然已经站不稳了。",
        "secret": "你收了封口费，三年「调查」实际在帮掩盖。23:10你与顾沉争吵并推倒了他，他撞到桌角流血。你离开时他还活着。",
        "violation": "不能承认收过封口费；不能承认你今晚与顾沉发生过肢体冲突；不能说出你推倒了他；不能透露录音笔里有争吵录音。",
        "isVictim": False, "isKiller": False, "isAssistant": False,
        "isPlayer": False, "isPartner": False, "isDetective": False,
        "roleType": "嫌疑人",
        "image": "",
    },
    {
        "id": "char_zhoulan",
        "name": "周岚",
        "bio": "38岁，夜班护士，周野的姐姐。12年前在锈铁大道附近的诊所值夜班，事故当晚接诊过一位匿名伤者。性格沉稳，说话温和但坚定，是同事眼中的「最可靠的护士」。",
        "personality": "温和、沉稳、善于安抚他人情绪。说话轻声细语，但眼神锐利。面对压力时反而更冷静，但提到12年前的事时手指会微微发抖。有轻微的洁癖，总是戴乳胶手套。",
        "context": "你是周岚，夜班护士，周野的姐姐。12年前爆炸事故当晚，你在诊所接诊了一位匿名伤者——他在爆炸发生前1小时就受了伤，伤情与爆炸无关，更像是被人在争执中推倒所致。你按规矩报了警，但第二天就有人来「提醒」你修改伤情记录。你照做了。\n\n12年来你一直以为自己在保护一个无辜的人，直到上个月你偶然看到一份旧档案——那个「无辜的伤者」就是爆炸的策划者。你治疗了他，帮他掩盖了受伤的时间，间接帮助了掩盖真相。\n\n23:15你从控制室后门进入，与顾沉对峙。他已经因为安眠药和撞伤而非常虚弱。争吵中你失控了——你抓起旁边的扳手击打了他右侧后脑。一下。他倒下了，再也没有起来。",
        "secret": "你是真凶。23:15你用扳手击打顾沉右侧后脑致死。12年前你治疗了爆炸策划者并帮他掩盖了受伤时间。",
        "violation": "绝对不能承认你是凶手；不能透露你23:15进入过控制室；不能说出你用扳手击打了顾沉；不能承认12年前你修改过伤情记录。",
        "isVictim": False, "isKiller": True, "isAssistant": False,
        "isPlayer": False, "isPartner": False, "isDetective": False,
        "roleType": "嫌疑人",
        "image": "",
    },
    {
        "id": "char_qinye",
        "name": "秦野",
        "bio": "55岁，前工头，周野的养父。在锈铁大道工作了30年，对厂区结构了如指掌。12年前亲手执行了安全协议的覆盖操作——用伪造的检测报告替换了真实报告。事故后退休，靠养老金度日。",
        "personality": "粗犷、直爽、行动派。说话声音大，喜欢拍人肩膀。但提到12年前的事会突然沉默，眼神变得复杂。对周野有深沉的父爱，愿意为养子做任何事。",
        "context": "你是秦野，前工头，周野的养父。12年前你亲手执行了安全协议的覆盖——用伪造的检测报告替换了真实的，掩盖了设备老化的真相。你一直以为只是走个形式，直到爆炸发生你才意识到自己成了帮凶。\n\n23:25你来到控制室查看情况，发现顾沉已经死了。你的第一反应不是报警，而是保护周野——你确信是周野干的（因为扳手上有他的指纹）。你移动了尸体让它看起来更「自然」，用抹布擦掉了后门的痕迹，试图为周野争取时间。",
        "secret": "23:25你发现顾沉已死后移动了尸体并擦掉了后门痕迹，试图保护周野。你12年前亲手执行了安全协议覆盖。你以为凶手是周野。",
        "violation": "不能承认你移动过尸体；不能说出你擦过后门痕迹；不能透露你12年前执行了安全协议覆盖。",
        "isVictim": False, "isKiller": False, "isAssistant": False,
        "isPlayer": False, "isPartner": False, "isDetective": False,
        "roleType": "嫌疑人",
        "image": "",
    },
    {
        "id": "char_linyuan",
        "name": "林远",
        "bio": "45岁，旧保安，12年前在锈铁大道值夜班。事故当晚声称「什么都没看到」，但他的证词在事故前后有两个不同版本。事故后转行做了小区保安，一直过着低调的生活。",
        "personality": "谨慎、胆小、善于观察。说话时总是避开别人的目光，习惯性地搓手。对「正义」和「真相」这类词有本能的抵触。喝酒后会变得话多，容易说漏嘴。",
        "context": "你是林远，12年前锈铁大道的夜班保安。事故当晚你亲眼看到有人从控制室后门离开，但第二天有人付钱让你改了证词——你说「什么都没看到」。\n\n22:30你比所有人都早到了控制室。你在顾沉的咖啡里下了安眠药——你只是想迷晕他，偷走那段录音。你从自己常备的安眠药瓶里取了两片，磨成粉放进咖啡。顾沉喝下后开始犯困，但安眠药的剂量不足以让他完全昏迷，更不足以致死。\n\n你22:50离开控制室时顾沉还醒着，只是昏昏沉沉。",
        "secret": "你22:30在顾沉的咖啡里下了安眠药，想迷晕他偷录音。剂量不足以致死，但让他变得虚弱。你12年前改过证词，顾沉录下了你改证词的对话。",
        "violation": "不能承认你下过安眠药；不能说出你来控制室是为了偷录音；不能透露你12年前改过证词。",
        "isVictim": False, "isKiller": False, "isAssistant": False,
        "isPlayer": False, "isPartner": False, "isDetective": False,
        "roleType": "嫌疑人",
        "image": "",
    },
    {
        "id": "char_guchen",
        "name": "顾沉",
        "bio": "50岁，前安全主管，12年前负责锈铁大道的安全管理。表面上是「吹哨人」，实际上他才是最大的掩盖者。",
        "personality": "精明、城府深、善于操控。说话滴水不漏，总是微笑着让人放松警惕。但内心极度焦虑，经常失眠，有严重的胃病。",
        "context": "你是顾沉，12年前锈铁大道的安全主管。你不是什么吹哨人——你一直是最大的掩盖者。你22:00到达控制室开始工作，22:30喝了咖啡（里面被下了安眠药），22:41设置了一条定时消息。23:00被周野的撬柜声惊醒，23:10沈禾闯入与你争吵，23:15周岚从后门进来……你已经死了。",
        "secret": "你今晚来是为了销毁证据，不是公开真相。你设置了定时消息制造烟雾弹。你在死前完成了大部分文件删除。",
        "violation": "（受害者角色，由DM控制）",
        "isVictim": True, "isKiller": False, "isAssistant": False,
        "isPlayer": False, "isPartner": False, "isDetective": False,
        "roleType": "受害者",
        "image": "",
    },
]

# ============================
# 证物数据
# ============================
evidences_data = [
    {
        "id": "ev_wrench",
        "name": "沾血的扳手",
        "description": "一把重型活动扳手，把手上沾有干涸的血迹，把柄处似乎有清晰的指纹。这是导致顾沉死亡的致命伤来源。",
        "category": "physical",
        "importance": "high",
        "initial_state": "hidden",
        "location": "控制室地板，尸体右侧",
        "time": "23:20 发现",
        "related_characters": ["周野", "周岚", "秦野"]
    },
    {
        "id": "ev_coffee_cup",
        "name": "残留的咖啡杯",
        "description": "顾沉办公桌上的咖啡杯，底部残留有微量白色粉末。经化验含有高效安眠药成分。",
        "category": "physical",
        "importance": "medium",
        "initial_state": "hidden",
        "location": "办公桌",
        "time": "22:45 使用",
        "related_characters": ["顾沉", "林远"]
    },
    {
        "id": "ev_journal",
        "name": "被撕毁的航海日志",
        "description": "12年前事故当晚的操作日志，关键的22:41至22:44页码被暴力撕除，边缘有焦黑痕迹。",
        "category": "document",
        "importance": "high",
        "initial_state": "hidden",
        "location": "被撬开的文件柜",
        "time": "12年前",
        "related_characters": ["周野", "顾沉"]
    },
    {
        "id": "ev_recording_pen",
        "name": "微型录音笔",
        "description": "藏在沙发缝隙里的录音笔。里面记录了一段激烈的争吵声，背景中有撞击重物的沉闷声响。",
        "category": "digital",
        "importance": "high",
        "initial_state": "hidden",
        "location": "休息区沙发",
        "time": "23:10 录制",
        "related_characters": ["沈禾", "顾沉"]
    },
    {
        "id": "ev_safety_report",
        "name": "伪造的安全检测报告",
        "description": "一份盖有厂区公章的检测报告，日期被涂改过，内容显示设备一切正常，但纸张厚度不一，明显有覆盖痕迹。",
        "category": "document",
        "importance": "medium",
        "initial_state": "surface",
        "location": "公共公告板",
        "time": "12年前",
        "related_characters": ["秦野", "顾沉"]
    },
    {
        "id": "ev_anonymous_letter",
        "name": "带血的匿名信",
        "description": "召唤众人回来的匿名信，信封背面印有一个奇怪的铁锈纹章，信纸一角有周岚诊所的特有标记。",
        "category": "document",
        "importance": "medium",
        "initial_state": "surface",
        "location": "各人手中",
        "time": "今日",
        "related_characters": ["周岚", "顾沉"]
    }
]

# ============================
# 导入
# ============================
def main():
    from api.db.models import ScriptEvidence
    session = get_session()
    try:
        # 1. 删除旧数据
        old = session.query(Script).filter(Script.id == SCRIPT_ID).first()
        if old:
            print(f"删除旧剧本: {old.title}")
            session.delete(old)
            session.flush()

        # 2. 创建剧本
        script = dict_to_script(script_data)
        session.add(script)
        session.flush()
        print(f"已创建剧本: {script.title} (id={script.id})")

        # 3. 添加角色
        for cd in characters_data:
            char = dict_to_character(cd, SCRIPT_ID)
            session.add(char)
        session.flush()
        print(f"已添加 {len(characters_data)} 个角色")

        # 4. 添加证物
        for ed in evidences_data:
            evidence = ScriptEvidence(
                id=ed["id"],
                script_id=SCRIPT_ID,
                name=ed["name"],
                description=ed["description"],
                category=ed["category"],
                importance=ed["importance"],
                initial_state=ed["initial_state"],
                related_characters=json.dumps(ed["related_characters"], ensure_ascii=False)
            )
            session.add(evidence)
        session.flush()
        print(f"已添加 {len(evidences_data)} 个证物线索")

        # 5. 验证
        created = session.query(Script).filter(Script.id == SCRIPT_ID).first()
        chars = list(created.characters)
        evs = list(created.script_evidences)
        print(f"\n验证: {created.title}")
        print(f"  角色数: {len(chars)}")
        for c in chars:
            print(f"  - {c.name} ({c.role_type}) victim={c.is_victim} killer={c.is_killer}")
        
        print(f"  证物数: {len(evs)}")
        for e in evs:
            print(f"  - {e.name} [{e.initial_state}]")

        session.commit()
        print("\n✅ 导入成功！")

    except Exception as e:
        session.rollback()
        print(f"\n❌ 导入失败: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()