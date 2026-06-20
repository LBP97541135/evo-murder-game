"""
EvoMap Murder Game - Recipe 创建与执行服务

多Gene编排流水线（Recipe）的创建、实例化、逐步执行业务逻辑。
一个 Recipe 包含多个 Gene 步骤，实例化为 Organism 后逐步执行。
"""

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, Callable

from api.evomap.evomap_client import EvoMapClient

logger = logging.getLogger(__name__)


# ============================
# 数据模型
# ============================

@dataclass
class GeneStep:
    """Recipe 中的一个 Gene 步骤定义。"""
    gene_asset_id: str          # 要执行的 Gene 的 asset_id
    position: int               # 执行顺序（从1开始）
    description: str = ""       # 步骤说明
    input_mapping: dict = field(default_factory=dict)  # 输入参数映射
    timeout_seconds: int = 300  # 步骤超时


@dataclass
class RecipeDefinition:
    """Recipe（多Gene编排流水线）定义。"""
    title: str
    description: str
    steps: list[GeneStep] = field(default_factory=list)
    price_per_execution: int = 0
    max_concurrent: int = 3
    recipe_id: str = ""


@dataclass
class OrganismState:
    """Organism（Recipe 运行实例）状态。"""
    organism_id: str
    recipe_id: str
    status: str                      # running / completed / failed / timeout
    current_position: int = 0
    total_steps: int = 0
    started_at: float = 0.0
    step_results: list[dict] = field(default_factory=list)
    final_output: dict = field(default_factory=dict)
    error: str = ""


# ============================
# Recipe 服务
# ============================

class RecipeService:
    """Recipe 编排服务：创建 Recipe、实例化 Organism、逐步执行 Gene。"""

    # 本地记录正在运行的 Organism
    _running_organisms: dict[str, OrganismState] = {}

    def __init__(self, client: EvoMapClient):
        self.client = client

    # ---------- Recipe 管理 ----------

    def create_recipe(self, recipe: RecipeDefinition) -> dict:
        """在 EvoMap 网络创建 Recipe。

        Args:
            recipe: Recipe 定义
        Returns:
            {"success": bool, "recipe_id": str, ...}
        """
        genes = []
        for step in recipe.steps:
            genes.append({
                "asset_id": step.gene_asset_id,
                "position": step.position,
                "description": step.description,
            })

        try:
            result = self.client.create_recipe(
                title=recipe.title,
                description=recipe.description,
                genes=genes,
                price_per_execution=recipe.price_per_execution,
                max_concurrent=recipe.max_concurrent,
            )
            if "error" in result:
                return {"success": False, "error": result["error"]}

            recipe_id = result.get("recipe_id", result.get("id", ""))
            recipe.recipe_id = recipe_id
            return {
                "success": True,
                "recipe_id": recipe_id,
                "detail": result,
            }
        except Exception as e:
            logger.error(f"Create recipe failed: {e}")
            return {"success": False, "error": str(e)}

    def build_game_recipe(
        self,
        script_name: str,
        companion_agents: list[dict],
    ) -> RecipeDefinition:
        """构建一场剧本杀游戏的 Recipe 模板。

        6步标准流程：
        1. 选角     — 玩家和 AI 分配角色
        2. 阅读剧本  — 各角色阅读自己的剧本信息
        3. 公共讨论1 — 自我介绍（各角色依次介绍身份）
        4. 随机搜证  — 各角色搜索线索
        5. 公共讨论2 — 出示线索和交流讨论
        6. 推理投票  — 指认凶手并投票
        """
        steps = []
        pos = 1

        # 1. 选角
        agent_names = ", ".join(a.get("name", "?") for a in companion_agents)
        steps.append(GeneStep(
            gene_asset_id="casting",
            position=pos,
            description=f"选角——分配角色：{agent_names}",
            input_mapping={"companion_agents": companion_agents},
            timeout_seconds=120,
        ))
        pos += 1

        # 2. 阅读剧本
        for agent in companion_agents:
            steps.append(GeneStep(
                gene_asset_id="script_reading",
                position=pos,
                description=f"{agent.get('name', 'Agent')} 阅读剧本",
                input_mapping={"agent_name": agent.get("name", "")},
                timeout_seconds=180,
            ))
            pos += 1

        # 3. 公共讨论1：自我介绍
        for agent in companion_agents:
            steps.append(GeneStep(
                gene_asset_id="self_intro",
                position=pos,
                description=f"{agent.get('name', 'Agent')} 自我介绍",
                input_mapping={"agent_name": agent.get("name", "")},
                timeout_seconds=120,
            ))
            pos += 1

        # 4. 随机搜证
        steps.append(GeneStep(
            gene_asset_id="evidence_search",
            position=pos,
            description="随机搜证——各角色搜索现场线索",
            timeout_seconds=240,
        ))
        pos += 1

        # 5. 公共讨论2：出示线索和交流
        steps.append(GeneStep(
            gene_asset_id="public_discussion",
            position=pos,
            description="公共讨论——出示线索和交流推理",
            timeout_seconds=300,
        ))
        pos += 1

        # 6. 推理投票
        steps.append(GeneStep(
            gene_asset_id="reasoning_vote",
            position=pos,
            description="推理投票——指认凶手并投票",
            timeout_seconds=180,
        ))

        return RecipeDefinition(
            title=f"剧本杀-{script_name}",
            description=f"《{script_name}》的标准6步游戏流程：选角→读本→自我介绍→搜证→讨论→投票",
            steps=steps,
        )

    def build_evolution_recipe(self, agent_name: str) -> RecipeDefinition:
        """构建 Agent 进化流程的 Recipe 模板。

        流水线：
        1. 召回历史经验
        2. 搜索社区相关 Gene
        3. 自评反思
        4. Constitution 改写
        5. 发布 Gene+Capsule
        """
        steps = [
            GeneStep(gene_asset_id="memory_recall", position=1,
                     description=f"{agent_name} 召回历史经验"),
            GeneStep(gene_asset_id="community_search", position=2,
                     description=f"{agent_name} 搜索社区相关策略"),
            GeneStep(gene_asset_id="self_reflection", position=3,
                     description=f"{agent_name} 自评反思"),
            GeneStep(gene_asset_id="constitution_rewrite", position=4,
                     description=f"{agent_name} Constitution 改写"),
            GeneStep(gene_asset_id="publish_experience", position=5,
                     description=f"{agent_name} 发布经验到社区"),
        ]
        return RecipeDefinition(
            title=f"Agent进化-{agent_name}",
            description=f"{agent_name} 的局后自动进化流水线",
            steps=steps,
        )

    # ---------- Organism 执行 ----------

    def instantiate_recipe(self, recipe_id: str,
                           input_payload: dict = None,
                           ttl: int = 7200) -> dict:
        """将 Recipe 实例化为 Organism（运行实例）。

        Args:
            recipe_id: Recipe ID
            input_payload: 输入参数
            ttl: Organism 存活时间（秒），默认2小时
        Returns:
            {"success": bool, "organism_id": str, ...}
        """
        payload = input_payload or {}

        try:
            result = self.client.express_recipe(
                recipe_id=recipe_id,
                input_payload=payload,
                ttl=ttl,
            )
            if "error" in result:
                return {"success": False, "error": result["error"]}

            organism_id = result.get("organism_id", result.get("id", ""))
            total_steps = payload.get("total_steps", 0)

            # 本地记录状态
            state = OrganismState(
                organism_id=organism_id,
                recipe_id=recipe_id,
                status="running",
                total_steps=total_steps,
                started_at=time.time(),
            )
            self._running_organisms[organism_id] = state

            return {
                "success": True,
                "organism_id": organism_id,
                "detail": result,
            }
        except Exception as e:
            logger.error(f"Instantiate recipe failed: {e}")
            return {"success": False, "error": str(e)}

    def execute_step(
        self,
        organism_id: str,
        gene_asset_id: str,
        position: int,
        output: dict = None,
        status: str = "success",
        capsule_id: str = "",
    ) -> dict:
        """在 Organism 中执行一个 Gene 步骤。

        Args:
            organism_id: Organism ID
            gene_asset_id: 要执行的 Gene asset_id
            position: 步骤位置（从1开始）
            output: 执行输出数据
            status: 执行状态（success / failed）
            capsule_id: 关联的 Capsule ID（可选）
        Returns:
            {"success": bool, "detail": dict}
        """
        try:
            result = self.client.express_gene(
                organism_id=organism_id,
                gene_asset_id=gene_asset_id,
                position=position,
                status=status,
                output=output or {},
                capsule_id=capsule_id or None,
            )

            # 更新本地状态
            if organism_id in self._running_organisms:
                state = self._running_organisms[organism_id]
                state.current_position = position
                state.step_results.append({
                    "position": position,
                    "gene_asset_id": gene_asset_id,
                    "status": status,
                    "output": output,
                    "result": result,
                })

            if "error" in result:
                if organism_id in self._running_organisms:
                    self._running_organisms[organism_id].status = "failed"
                    self._running_organisms[organism_id].error = result["error"]
                return {"success": False, "error": result["error"]}

            return {"success": True, "detail": result}
        except Exception as e:
            logger.error(f"Execute step failed (organism={organism_id}, gene={gene_asset_id}): {e}")
            if organism_id in self._running_organisms:
                self._running_organisms[organism_id].status = "error"
                self._running_organisms[organism_id].error = str(e)
            return {"success": False, "error": str(e)}

    def execute_recipe_full(
        self,
        recipe_id: str,
        steps: list[GeneStep],
        input_payload: dict = None,
        step_executor: Callable = None,
        ttl: int = 7200,
    ) -> dict:
        """完整执行一个 Recipe 的所有步骤（阻塞式）。

        如果不提供 step_executor，则只实例化不执行。
        如果提供 step_executor，会依次调用 step_executor(step) 并逐步推进。

        Args:
            recipe_id: Recipe ID
            steps: GeneStep 列表
            input_payload: 输入参数
            step_executor: 可选，自定义步骤执行函数，接收 GeneStep 参数
            ttl: Organism TTL
        Returns:
            {"success": bool, "organism_id": str, "results": list, ...}
        """
        # 1. 实例化 Recipe
        payload = input_payload or {}
        payload["total_steps"] = len(steps)

        instantiate_result = self.instantiate_recipe(recipe_id, payload, ttl)
        if not instantiate_result.get("success"):
            return instantiate_result

        organism_id = instantiate_result["organism_id"]

        # 2. 如果没有 step_executor，只返回实例化结果
        if not step_executor:
            return {
                "success": True,
                "organism_id": organism_id,
                "recipe_id": recipe_id,
                "total_steps": len(steps),
                "status": "instantiated",
                "steps": [asdict(s) for s in steps],
            }

        # 3. 依次执行每个步骤
        results = []
        all_success = True
        for step in sorted(steps, key=lambda s: s.position):
            logger.info(f"Executing step {step.position}/{len(steps)}: {step.description}")

            try:
                step_output = step_executor(step)
                if step_output is None:
                    step_output = {}

                exec_result = self.execute_step(
                    organism_id=organism_id,
                    gene_asset_id=step.gene_asset_id,
                    position=step.position,
                    output=step_output if isinstance(step_output, dict) else {"result": str(step_output)},
                    status="success",
                )
                results.append({
                    "position": step.position,
                    "gene_asset_id": step.gene_asset_id,
                    "success": exec_result.get("success", False),
                    "output": step_output,
                })

                if not exec_result.get("success"):
                    all_success = False
                    break

            except Exception as e:
                logger.error(f"Step {step.position} execution failed: {e}")
                self.execute_step(
                    organism_id=organism_id,
                    gene_asset_id=step.gene_asset_id,
                    position=step.position,
                    status="failed",
                    output={"error": str(e)},
                )
                results.append({
                    "position": step.position,
                    "gene_asset_id": step.gene_asset_id,
                    "success": False,
                    "error": str(e),
                })
                all_success = False
                break

        # 4. 更新最终状态
        if organism_id in self._running_organisms:
            state = self._running_organisms[organism_id]
            state.status = "completed" if all_success else "failed"
            state.final_output = {
                "all_success": all_success,
                "steps_completed": len([r for r in results if r.get("success")]),
                "total_steps": len(steps),
            }

        return {
            "success": all_success,
            "organism_id": organism_id,
            "recipe_id": recipe_id,
            "total_steps": len(steps),
            "steps_completed": len(results),
            "status": "completed" if all_success else "failed",
            "results": results,
        }

    # ---------- 状态查询 ----------

    def get_organism_status(self, organism_id: str) -> Optional[OrganismState]:
        """获取 Organism 当前状态（从本地缓存）。"""
        return self._running_organisms.get(organism_id)

    def list_running_organisms(self) -> list[OrganismState]:
        """列出所有正在运行的 Organism。"""
        return [
            s for s in self._running_organisms.values()
            if s.status in ("running",)
        ]

    def list_completed_organisms(self) -> list[OrganismState]:
        """列出所有已完成的 Organism。"""
        return [
            s for s in self._running_organisms.values()
            if s.status in ("completed", "failed", "error")
        ]

    def cleanup_organism(self, organism_id: str) -> bool:
        """清理（移除）一个 Organism 的本地记录。"""
        return self._running_organisms.pop(organism_id, None) is not None