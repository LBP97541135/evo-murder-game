"""
EvoMap Murder Game - Asset 获取与发布服务

社群资产（Gene + Capsule）的搜索、获取、校验、发布业务逻辑。
基于 EvoMapClient 的底层 HTTP 方法，提供面向 Agent 的高层 API。
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional

from api.evomap.evomap_client import EvoMapClient

logger = logging.getLogger(__name__)


# ============================
# 数据模型
# ============================

@dataclass
class Gene:
    """Gene（基因）——一个可复用的策略/技能单元。

    - 可被其他 Agent 搜索和获取
    - 表达时产出 Capsule（执行结果胶囊）
    """
    name: str
    description: str
    category: str = "general"          # general / role_playing / inference / hosting / hint
    tags: list = field(default_factory=list)
    version: str = "1.0.0"
    author_node_id: str = ""
    content: str = ""                   # 核心策略内容（prompt / 规则 / 算法描述）
    source: str = "local"               # local / community / imported


@dataclass
class Capsule:
    """Capsule（胶囊）——Gene 执行后产出的结果/经验包。

    包含执行上下文、结果数据、评分等信息。
    """
    gene_id: str = ""
    title: str = ""
    summary: str = ""
    signals: list = field(default_factory=list)
    score: float = 0.0
    execution_context: dict = field(default_factory=dict)
    output_data: dict = field(default_factory=dict)
    quality_tags: list = field(default_factory=list)


@dataclass
class AssetSearchResult:
    """社区资产搜索结果的单个条目。"""
    asset_id: str = ""
    name: str = ""
    description: str = ""
    category: str = ""
    tags: list = field(default_factory=list)
    author: str = ""
    version: str = ""
    score: float = 0.0
    match_reason: str = ""


# ============================
# Asset 服务
# ============================

class AssetService:
    """社群资产服务：搜索、获取、校验、发布 Gene + Capsule。"""

    def __init__(self, client: EvoMapClient):
        self.client = client
        # 本地缓存已获取/已发布的资产元数据
        self._fetched_cache: dict[str, Gene] = {}
        self._published_cache: dict[str, str] = {}  # asset_id -> name

    # ---------- 搜索与发现 ----------

    def search_by_signals(self, signals: list[str], category: str = "",
                          limit: int = 10) -> list[AssetSearchResult]:
        """按信号搜索社群资产（搜索模式，免费）。

        Args:
            signals: 搜索信号列表（如 ["role-playing", "inference"]）
            category: 可选的分类过滤
            limit: 最大返回数
        Returns:
            搜索结果列表
        """
        all_results = []
        try:
            # 先试 fetch（搜索模式）
            result = self.client.fetch(
                signals=signals,
                search_only=True,
                category=category or None,
            )
            if "error" not in result:
                all_results.extend(self._parse_search_result(result))

            # 再试 search_assets（GET 方式，关键词查询）
            query = " ".join(signals[:3])
            search_result = self.client.search_assets(query=query, category=category or None)
            if "error" not in search_result:
                all_results.extend(self._parse_search_result(search_result))

        except Exception as e:
            logger.warning(f"Asset search by signals failed: {e}")

        # 合并去重
        seen = set()
        unique = []
        for r in all_results:
            if r.asset_id not in seen:
                seen.add(r.asset_id)
                unique.append(r)

        return unique[:limit]

    def search_by_keyword(self, query: str, category: str = "") -> list[AssetSearchResult]:
        """按关键词搜索资产（免费 GET 方式）。"""
        try:
            result = self.client.search_assets(query=query, category=category or None)
            return self._parse_search_result(result)
        except Exception as e:
            logger.warning(f"Asset search by keyword failed: {e}")
            return []

    def discover_community(self) -> dict:
        """发现社区中的协作机会和热门资产。"""
        result = self.client.discover()
        return result if "error" not in result else {"items": []}

    # ---------- 获取（付费模式） ----------

    def fetch_asset(self, asset_id: str) -> Optional[Gene]:
        """获取单个资产的完整内容（付费，消耗积分）。"""
        try:
            result = self.client.fetch(
                asset_ids=[asset_id],
                search_only=False,
            )
            if "error" in result:
                logger.error(f"Failed to fetch asset {asset_id}: {result['error']}")
                return None
            gene = self._parse_gene_from_response(result)
            if gene:
                self._fetched_cache[asset_id] = gene
            return gene
        except Exception as e:
            logger.error(f"Fetch asset {asset_id} failed: {e}")
            return None

    def fetch_multiple(self, asset_ids: list[str]) -> list[Gene]:
        """批量获取资产内容。"""
        genes = []
        # 优先从缓存取
        for aid in asset_ids:
            if aid in self._fetched_cache:
                genes.append(self._fetched_cache[aid])
                asset_ids = [a for a in asset_ids if a != aid]

        if not asset_ids:
            return genes

        try:
            result = self.client.fetch(asset_ids=asset_ids, search_only=False)
            if "error" not in result:
                parsed = self._parse_genes_from_response(result)
                for g in parsed:
                    self._fetched_cache[g.author_node_id or "unknown"] = g
                genes.extend(parsed)
        except Exception as e:
            logger.warning(f"Batch fetch failed: {e}")

        return genes

    # ---------- 校验与发布 ----------

    def validate_assets(self, gene: Gene, capsule: Optional[Capsule] = None) -> dict:
        """发布前进行干跑校验，确保资产格式正确。"""
        assets = [asdict(gene)]
        if capsule:
            assets.append(asdict(capsule))

        try:
            result = self.client.validate(assets=assets)
            return result if "error" not in result else {"valid": False, "error": result["error"]}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def publish_gene(self, gene: Gene, chain_id: Optional[str] = None) -> dict:
        """发布一个 Gene 到社区。

        Args:
            gene: 要发布的 Gene
            chain_id: 可选，发行链 ID
        Returns:
            {"asset_id": str, "status": str} 或错误信息
        """
        gene_dict = asdict(gene)
        gene_dict["type"] = "gene"

        try:
            result = self.client.publish(assets=[gene_dict], chain_id=chain_id)
            if "error" in result:
                return {"success": False, "error": result["error"]}

            asset_id = result.get("asset_id", result.get("id", ""))
            self._published_cache[asset_id] = gene.name
            return {
                "success": True,
                "asset_id": asset_id,
                "status": "published",
                "name": gene.name,
                "detail": result,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def publish_gene_capsule_pair(
        self,
        gene: Gene,
        capsule: Capsule,
        chain_id: Optional[str] = None,
    ) -> dict:
        """发布 Gene + Capsule 资产包（先校验，通过后发布）。"""
        # 1. 校验
        validation = self.validate_assets(gene, capsule)
        if not validation.get("valid", True):
            return {"success": False, "error": f"Validation failed: {validation}"}

        # 2. 组装资产包
        gene_dict = asdict(gene)
        gene_dict["type"] = "gene"
        capsule_dict = asdict(capsule)
        capsule_dict["type"] = "capsule"

        try:
            result = self.client.publish(
                assets=[gene_dict, capsule_dict],
                chain_id=chain_id,
            )
            if "error" in result:
                return {"success": False, "error": result["error"]}

            asset_id = result.get("asset_id", result.get("id", ""))
            self._published_cache[asset_id] = f"{gene.name}+capsule"
            return {
                "success": True,
                "asset_id": asset_id,
                "status": "published",
                "gene_name": gene.name,
                "detail": result,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ---------- 本地缓存查询 ----------

    def get_cached_assets(self) -> list[dict]:
        """查看本地缓存的资产列表。"""
        return [
            {"asset_id": aid, "name": name}
            for aid, name in self._published_cache.items()
        ]

    def get_fetched_genes(self) -> list[Gene]:
        """获取已缓存的 Gene 列表。"""
        return list(self._fetched_cache.values())

    # ---------- 内部解析方法 ----------

    def _parse_search_result(self, raw: dict) -> list[AssetSearchResult]:
        """从 API 响应中解析搜索结果。"""
        items = raw.get("items", raw.get("results", raw.get("data", [])))
        if isinstance(items, dict):
            items = [items]

        results = []
        try:
            for item in items[:20]:
                results.append(AssetSearchResult(
                    asset_id=item.get("id", item.get("asset_id", "")),
                    name=item.get("name", item.get("title", "")),
                    description=item.get("description", ""),
                    category=item.get("category", ""),
                    tags=item.get("tags", []),
                    author=item.get("author", item.get("author_node_id", "")),
                    version=item.get("version", ""),
                    score=float(item.get("score", item.get("relevance", 0))),
                    match_reason=item.get("match_reason", ""),
                ))
        except Exception as e:
            logger.warning(f"Parse search result failed: {e}")
        return results

    def _parse_gene_from_response(self, raw: dict) -> Optional[Gene]:
        """从 API 响应中解析单个 Gene。"""
        try:
            # 尝试多种 API 响应格式
            data = raw.get("asset", raw.get("gene", raw.get("data", raw)))
            if isinstance(data, list) and data:
                data = data[0]
            return Gene(
                name=data.get("name", data.get("title", "unknown")),
                description=data.get("description", ""),
                category=data.get("category", "general"),
                tags=data.get("tags", []),
                version=data.get("version", "1.0.0"),
                author_node_id=data.get("author", data.get("author_node_id", "")),
                content=data.get("content", data.get("payload", "")),
                source="community",
            )
        except Exception as e:
            logger.warning(f"Parse gene from response failed: {e}")
            return None

    def _parse_genes_from_response(self, raw: dict) -> list[Gene]:
        """从 API 响应中解析多个 Gene。"""
        items = raw.get("items", raw.get("results", raw.get("assets", raw.get("data", []))))
        if isinstance(items, dict):
            items = [items]

        genes = []
        for item in items[:20]:
            gene = self._parse_gene_from_response({"asset": item})
            if gene:
                genes.append(gene)
        return genes