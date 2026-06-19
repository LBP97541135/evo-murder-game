/**
 * EvoMap Murder Game - Evolution Timeline (骨架)
 *
 * Agent 进化时间线——展示 constitution/identity_doc 变更历史、
 * Memory 记录、Gene/Capsule 发布记录。
 */

import React from "react";
import { Container, Title, Text, Stack, Timeline } from "@mantine/core";

export function EvolutionTimeline() {
  return (
    <Container size="md" py="xl">
      <Title order={1}>🧬 Agent 进化时间线</Title>
      <Text c="dimmed" mt="md" mb="xl">
        查看 Agent 的 constitution 改写历史、Memory 记录和 Gene/Capsule 发布
      </Text>

      <Timeline active={0} bulletSize={24}>
        <Timeline.Item title="初始注册" color="blue">
          <Text size="sm" c="dimmed">
            constitution: "你是剧本杀陪玩Agent，擅长角色扮演和推理互动"
          </Text>
        </Timeline.Item>
        <Timeline.Item title="第3局后 · constitution 改写" color="violet">
          <Text size="sm" c="dimmed">
            用户偏好：喜欢简洁回答、比喻说明、避免术语堆砌
          </Text>
        </Timeline.Item>
        <Timeline.Item title="第7局后 · 获得社区Gene" color="green">
          <Text size="sm" c="dimmed">
            从社区fetch到 "推理线索提取策略" Gene (GDI=52)
          </Text>
        </Timeline.Item>
        <Timeline.Item title="第10局后 · 发布Capsule" color="orange">
          <Text size="sm" c="dimmed">
            发布 "新手引导策略" Gene+Capsule 到社区
          </Text>
        </Timeline.Item>
      </Timeline>

      <Stack mt="xl" align="center">
        <Text c="dimmed">（进化时间线数据后续对接后端 API）</Text>
      </Stack>
    </Container>
  );
}
