"""
EvoMap Murder Game - A2A Protocol Client

封装所有 EvoMap GEP-A2A 协议的 API 调用，供 Agent 使用。
包括：节点注册、心跳、Session通信、Memory记忆、资产发布/获取、Council治理、Task悬赏。
"""

import time
import uuid
import json
import httpx
from typing import Optional

from api.config.settings import EVOMAP_HUB_URL, EVOMAP_NODE_ID, EVOMAP_NODE_SECRET


class EvoMapClient:
    """EvoMap A2A Protocol 客户端，统一封装所有端点调用。"""

    def __init__(
        self,
        node_id: str = EVOMAP_NODE_ID,
        node_secret: str = EVOMAP_NODE_SECRET,
        hub_url: str = EVOMAP_HUB_URL,
    ):
        self.node_id = node_id
        self.node_secret = node_secret
        self.hub_url = hub_url.rstrip("/")
        self._client = httpx.Client(timeout=30.0)

    # ============================
    # 通用工具
    # ============================

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.node_secret}",
            "Content-Type": "application/json",
        }

    def _envelope(self, message_type: str, payload: Optional[dict] = None) -> dict:
        """构建 GEP-A2A 协议信封。"""
        envelope = {
            "protocol": "gep-a2a",
            "protocol_version": "1.0.0",
            "message_type": message_type,
            "message_id": f"msg_{int(time.time() * 1000)}_{uuid.uuid4().hex[:4]}",
            "sender_id": self.node_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
        }
        if payload:
            envelope["payload"] = payload
        return envelope

    def _post(self, endpoint: str, body: dict) -> dict:
        """发送 POST 请求到 EvoMap Hub。"""
        url = f"{self.hub_url}{endpoint}"
        try:
            r = self._client.post(url, headers=self._headers(), json=body)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}", "detail": e.response.text}
        except httpx.RequestError as e:
            return {"error": "request_error", "detail": str(e)}

    def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """发送 GET 请求到 EvoMap Hub。"""
        url = f"{self.hub_url}{endpoint}"
        try:
            r = self._client.get(url, headers=self._headers(), params=params)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}", "detail": e.response.text}
        except httpx.RequestError as e:
            return {"error": "request_error", "detail": str(e)}

    # ============================
    # 1. 节点生命周期
    # ============================

    def hello(self, name: str, capabilities: dict, model: str,
              identity_doc: str = "", constitution: str = "") -> dict:
        """注册新节点到 EvoMap 网络。"""
        payload = {
            "name": name,
            "capabilities": capabilities,
            "model": model,
            "identity_doc": identity_doc,
            "constitution": constitution,
        }
        return self._post("/a2a/hello", self._envelope("hello", payload))

    def heartbeat(self) -> dict:
        """发送心跳保活。"""
        return self._post("/a2a/heartbeat", self._envelope("heartbeat"))

    # ============================
    # 2. Session 多Agent协作
    # ============================

    def create_session(self, topic: str, participants: list) -> dict:
        """创建多Agent协作会话。"""
        body = {
            "sender_id": self.node_id,
            "topic": topic,
            "participants": participants,
        }
        return self._post("/a2a/session/create", body)

    def join_session(self, session_id: str) -> dict:
        """加入已有会话。"""
        body = {
            "sender_id": self.node_id,
            "session_id": session_id,
        }
        return self._post("/a2a/session/join", body)

    def send_message(
        self,
        session_id: str,
        msg_type: str,
        payload: dict,
        to_node_id: Optional[str] = None,
    ) -> dict:
        """在会话中发送消息。to_node_id=None 时广播。"""
        body = {
            "session_id": session_id,
            "sender_id": self.node_id,
            "msg_type": msg_type,
            "payload": payload,
        }
        if to_node_id:
            body["to_node_id"] = to_node_id
        return self._post("/a2a/session/message", body)

    def submit_task_result(
        self, session_id: str, task_id: str, result_asset_id: str
    ) -> dict:
        """提交子任务完成结果。"""
        body = {
            "session_id": session_id,
            "sender_id": self.node_id,
            "task_id": task_id,
            "result_asset_id": result_asset_id,
        }
        return self._post("/a2a/session/submit", body)

    # ============================
    # 3. 资产发布与获取
    # ============================

    def publish(self, assets: list, chain_id: Optional[str] = None) -> dict:
        """发布 Gene+Capsule 资产包。"""
        payload = {"assets": assets}
        if chain_id:
            payload["chain_id"] = chain_id
        return self._post("/a2a/publish", self._envelope("publish", payload))

    def validate(self, assets: list) -> dict:
        """发布前干跑校验。"""
        payload = {"assets": assets}
        return self._post("/a2a/validate", self._envelope("validate", payload))

    def fetch(
        self,
        signals: Optional[list] = None,
        search_only: bool = True,
        asset_ids: Optional[list] = None,
        category: Optional[str] = None,
    ) -> dict:
        """搜索或获取社区资产。search_only=True 免费，获取完整内容付费。"""
        payload = {
            "sender_id": self.node_id,
            "search_only": search_only,
        }
        if signals:
            payload["signals"] = signals
        if asset_ids:
            payload["asset_ids"] = asset_ids
            payload["search_only"] = False
        if category:
            payload["category"] = category
        return self._post("/a2a/fetch", payload)

    def search_assets(self, query: str, category: Optional[str] = None) -> dict:
        """GET 方式搜索资产元数据（免费）。"""
        params = {"q": query}
        if category:
            params["category"] = category
        return self._get("/a2a/assets/search", params)

    # ============================
    # 4. 进化记忆
    # ============================

    def memory_record(
        self, signals: list, gene_id: str, status: str, score: float, summary: str
    ) -> dict:
        """记录一次策略执行经验到私有记忆库。"""
        body = {
            "sender_id": self.node_id,
            "signals": signals,
            "gene_id": gene_id,
            "status": status,
            "score": score,
            "summary": summary,
        }
        return self._post("/a2a/memory/record", body)

    def memory_recall(self, signals: list, limit: int = 5) -> dict:
        """按信号相似度召回历史经验。"""
        body = {
            "sender_id": self.node_id,
            "signals": signals,
            "limit": limit,
        }
        return self._post("/a2a/memory/recall", body)

    def memory_status(self) -> dict:
        """查看当前节点记忆概况。"""
        return self._get("/a2a/memory/status")

    # ============================
    # 5. Council 治理与决策
    # ============================

    def council_propose(
        self, title: str, description: str, proposal_type: str = "general",
        payload: Optional[dict] = None
    ) -> dict:
        """发起 AI Council 提案。"""
        body = {
            "sender_id": self.node_id,
            "type": proposal_type,
            "title": title,
            "description": description,
        }
        if payload:
            body["payload"] = payload
        return self._post("/a2a/council/propose", body)

    def dialog(
        self, deliberation_id: str, dialog_type: str, content: dict
    ) -> dict:
        """参与 Council 审议对话。

        dialog_type: second / diverge / challenge / agree / disagree / build_on / amend / vote
        """
        body = {
            "sender_id": self.node_id,
            "deliberation_id": deliberation_id,
            "dialog_type": dialog_type,
            "content": content,
        }
        return self._post("/a2a/dialog", body)

    # ============================
    # 6. 任务与悬赏
    # ============================

    def propose_decomposition(
        self, task_id: str, subtasks: list
    ) -> dict:
        """蜂群分解：将复杂任务拆为多个子任务。"""
        body = {
            "sender_id": self.node_id,
            "task_id": task_id,
            "subtasks": subtasks,
        }
        return self._post("/a2a/task/propose-decomposition", body)

    def claim_task(self, task_id: str) -> dict:
        """认领悬赏任务。"""
        body = {
            "sender_id": self.node_id,
            "task_id": task_id,
        }
        return self._post("/a2a/task/claim", body)

    def complete_task(self, task_id: str, result: dict) -> dict:
        """标记任务完成。"""
        body = {
            "sender_id": self.node_id,
            "task_id": task_id,
            "result": result,
        }
        return self._post("/a2a/task/complete", body)

    def ask(self, question: str, domain: str = "", bounty: int = 5) -> dict:
        """Agent主动发布问题/悬赏，向网络求助。"""
        body = {
            "sender_id": self.node_id,
            "question": question,
            "domain": domain,
            "bounty": bounty,
        }
        return self._post("/a2a/ask", body)

    # ============================
    # 7. Recipe & Organism 流程编排
    # ============================

    def create_recipe(
        self, title: str, description: str, genes: list,
        price_per_execution: int = 0, max_concurrent: int = 3
    ) -> dict:
        """创建 Recipe（多Gene编排流水线）。"""
        body = {
            "sender_id": self.node_id,
            "title": title,
            "description": description,
            "genes": genes,
            "price_per_execution": price_per_execution,
            "max_concurrent": max_concurrent,
        }
        return self._post("/a2a/recipe", body)

    def express_recipe(self, recipe_id: str, input_payload: dict, ttl: int = 3600) -> dict:
        """将 Recipe 实例化为 Organism（运行实例）。"""
        body = {
            "sender_id": self.node_id,
            "input_payload": input_payload,
            "ttl": ttl,
        }
        return self._post(f"/a2a/recipe/{recipe_id}/express", body)

    def express_gene(
        self, organism_id: str, gene_asset_id: str, position: int,
        status: str = "success", output: Optional[dict] = None,
        capsule_id: Optional[str] = None
    ) -> dict:
        """在 Organism 中逐步执行 Gene。"""
        body = {
            "sender_id": self.node_id,
            "gene_asset_id": gene_asset_id,
            "position": position,
            "status": status,
        }
        if output:
            body["output"] = output
        if capsule_id:
            body["capsule_id"] = capsule_id
        return self._post(f"/a2a/organism/{organism_id}/express-gene", body)

    # ============================
    # 8. 积分与经济
    # ============================

    def credit_estimate(self) -> dict:
        """估算积分对应的 token 数和请求数。"""
        return self._get("/a2a/credit/estimate")

    def earnings(self) -> dict:
        """查看收益历史。"""
        return self._get("/a2a/earnings")

    # ============================
    # 9. 发现与帮助
    # ============================

    def discover(self) -> dict:
        """发现网络中的协作机会。"""
        return self._get("/a2a/discover")

    def help(self, endpoint: str = "") -> dict:
        """即时文档查询。"""
        params = {"endpoint": endpoint} if endpoint else {}
        return self._get("/a2a/help", params)


# ============================
# 全局单例（用于非特定 Agent 的通用调用）
# ============================
evomap_client = EvoMapClient()
