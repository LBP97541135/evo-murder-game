/**
 * EvoMap Murder Game - Game Page (骨架)
 *
 * 主游戏页面——角色对话、线索展示、推理提交。
 * 当前为骨架占位，后续实现完整游戏交互。
 */

import React from "react";
import { Container, Title, Text, Stack } from "@mantine/core";

export function GamePage() {
  return (
    <Container size="md" py="xl">
      <Title order={1}>🎭 游戏进行中</Title>
      <Text c="dimmed" mt="md">
        游戏页面骨架——后续实现角色对话、线索面板、推理提交
      </Text>
      <Stack mt="xl">
        <Text>• 角色选择与对话界面</Text>
        <Text>• 线索收集与展示面板</Text>
        <Text>• 推理笔记</Text>
        <Text>• 向角色出示证据触发反应</Text>
        <Text>• 推理提交（选凶手→选动机→验证）</Text>
        <Text>• 游戏复盘</Text>
      </Stack>
    </Container>
  );
}
