/**
 * EvoMap Murder Game - Agent Panel (骨架)
 *
 * Agent 配置面板——注册 Agent、查看状态、配置进化参数。
 */

import React, { useState } from "react";
import {
  Container, Title, Text, Stack, Card, Badge,
  Button, TextInput, Select, Group,
} from "@mantine/core";
import { useAgent } from "../providers/contexts";
import { listAgents, registerAgent } from "../api/invoke";

export function AgentPanel() {
  const { agents, setAgents } = useAgent();
  const [role, setRole] = useState<string>("companion");
  const [name, setName] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if (!name) return;
    setLoading(true);
    try {
      await registerAgent(role, name, "evomap-gemini-3.1-pro-preview", "", "");
      const res = await listAgents();
      setAgents(res.agents);
    } catch (e) {
      console.error("Agent registration failed:", e);
    }
    setLoading(false);
  };

  const handleRefresh = async () => {
    try {
      const res = await listAgents();
      setAgents(res.agents);
    } catch (e) {
      console.error("Failed to refresh agents:", e);
    }
  };

  return (
    <Container size="md" py="xl">
      <Title order={1}>🤖 Agent 配置面板</Title>
      <Text c="dimmed" mt="md" mb="xl">
        注册 AI Agent 到 EvoMap 网络，配置角色和进化参数
      </Text>

      {/* 注册新 Agent */}
      <Card withBorder padding="lg" mb="xl">
        <Title order={3} mb="md">注册新 Agent</Title>
        <Group>
          <Select
            label="角色类型"
            data={[
              { value: "dm", label: "DM（主持人）" },
              { value: "companion", label: "陪玩（角色扮演）" },
              { value: "assistant", label: "个人助手" },
            ]}
            value={role}
            onChange={(v) => setRole(v || "companion")}
          />
          <TextInput
            label="Agent 名称"
            placeholder="例如：小七、陈默、酒馆老板"
            value={name}
            onChange={(e) => setName(e.currentTarget.value)}
            style={{ flex: 1 }}
          />
          <Button onClick={handleRegister} loading={loading}>
            注册到 EvoMap
          </Button>
        </Group>
      </Card>

      {/* 已注册 Agent 列表 */}
      <Title order={3} mb="md">已注册 Agent</Title>
      <Button variant="light" mb="md" onClick={handleRefresh}>刷新列表</Button>
      {agents.length === 0 ? (
        <Text c="dimmed">尚未注册任何 Agent</Text>
      ) : (
        <Stack>
          {agents.map((a) => (
            <Card key={a.key} withBorder padding="sm">
              <Group>
                <Badge color={a.role === "dm" ? "red" : a.role === "companion" ? "blue" : "green"}>
                  {a.role}
                </Badge>
                <Text fw={500}>{a.name}</Text>
                <Badge variant="light">{a.model}</Badge>
                <Badge variant="light" color={a.registered ? "teal" : "gray"}>
                  {a.registered ? "已注册" : "待注册"}
                </Badge>
              </Group>
            </Card>
          ))}
        </Stack>
      )}
    </Container>
  );
}
