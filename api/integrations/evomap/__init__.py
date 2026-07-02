# -*- coding: utf-8 -*-
"""EvoMap Murder Game - EvoMap 集成模块

提供 EvoMap 平台的可选集成。
"""

from api.integrations.evomap.adapter import EvoMapAdapter
from api.integrations.evomap.client import EvoMapClient, evomap_client

__all__ = ["EvoMapAdapter", "EvoMapClient", "evomap_client"]
