/**
 * EvoMap Murder Game - Script Library Page
 *
 * 剧本库页面——浏览、搜索、筛选剧本。
 * 当前为骨架，后续对接后端 API。
 */

import React from "react";
import {
  Container, Title, Text, SimpleGrid, Card, Badge, Group,
  Button, TextInput, Select, Stack,
} from "@mantine/core";
import { useNavigate } from "react-router-dom";
import { useScript } from "../providers/contexts";

export function ScriptLibrary() {
  const navigate = useNavigate();
  const { scripts } = useScript();

  return (
    <Container size="lg" py="xl">
      <Title order={1} ta="center" mb="lg">
        🎭 进化酒馆 · 剧本库
      </Title>
      <Text ta="center" c="dimmed" mb="xl">
        选择一个剧本，与自进化的 AI Agent 共同推理真相
      </Text>

      {/* 筛选栏 */}
      <Group mb="lg">
        <TextInput placeholder="搜索剧本..." style={{ flex: 1 }} />
        <Select
          placeholder="难度"
          data={[
            { value: "easy", label: "新手" },
            { value: "medium", label: "中等" },
            { value: "hard", label: "硬核" },
          ]}
          clearable
        />
        <Select
          placeholder="题材"
          data={[
            { value: "modern", label: "现代" },
            { value: "ancient", label: "古风" },
            { value: "horror", label: "恐怖" },
            { value: "campus", label: "校园" },
          ]}
          clearable
        />
      </Group>

      {/* 剧本网格 */}
      {scripts.length === 0 ? (
        <Stack align="center" mt="xl">
          <Text c="dimmed">暂无剧本，请先从后端导入或通过 AI 生成</Text>
          <Button onClick={() => navigate("/agents")}>
            配置 Agent 开始游戏
          </Button>
        </Stack>
      ) : (
        <SimpleGrid cols={3}>
          {scripts.map((s) => (
            <Card key={s.id} shadow="sm" padding="lg" radius="md"
              withBorder style={{ cursor: "pointer" }}
              onClick={() => navigate(`/play/${s.id}`)}
            >
              <Group mb="xs">
                <Title order={3}>{s.title}</Title>
                <Badge color="blue">{s.difficulty}</Badge>
                <Badge color="violet">{s.theme}</Badge>
              </Group>
              <Text size="sm" c="dimmed">{s.description}</Text>
              <Group mt="md">
                <Badge variant="light">{s.playerCount}人</Badge>
                <Badge variant="light">{s.duration}分钟</Badge>
              </Group>
            </Card>
          ))}
        </SimpleGrid>
      )}
    </Container>
  );
}
