/**
 * EvoMap Murder Game - Personal Assistant Hub (指南针)
 */

import React, { useEffect, useState } from "react";
import {
  Badge,
  Button,
  Card,
  Divider,
  Grid,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Tabs,
  Text,
  TextInput,
  Title,
  Timeline,
  ScrollArea,
} from "@mantine/core";
import {
  IconBrain,
  IconMessageCircle2,
  IconSend,
  IconSparkles,
  IconTimeline,
  IconUserCircle,
} from "@tabler/icons-react";

import { StudioShell } from "./StudioShell";
import {
  getUserProfile,
  assistantChat,
  getAssistantHistory,
  type UserProfile,
} from "../api/invoke";
import { getAssistantGreeting } from "../api/assistantApi";

export function EvolutionTimeline() {
  const [tab, setTab] = React.useState<string | null>("profile");
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [assistantPersona, setAssistantPersona] = useState<{
    name: string;
    personaText: string;
    speechStyle: string;
  } | null>(null);
  const [greetingLoaded, setGreetingLoaded] = useState(false);

  useEffect(() => {
    getUserProfile()
      .then((data) => setProfile(data.profile))
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    getAssistantGreeting()
      .then((data) => {
        if (data.persona) {
          setAssistantPersona({
            name: data.persona.name,
            personaText: data.persona.personaText,
            speechStyle: data.persona.speechStyle,
          });
        }
        if (data.greeting) {
          setChatHistory([{ role: "assistant", content: data.greeting }]);
        }
        setGreetingLoaded(true);
      })
      .catch(() => setGreetingLoaded(true));
  }, []);

  useEffect(() => {
    if (!greetingLoaded) return;
    getAssistantHistory()
      .then((data) => {
        if (data.history?.length) setChatHistory(data.history);
      })
      .catch(() => undefined);
  }, [greetingLoaded]);

  const handleChat = async () => {
    const msg = chatInput.trim();
    if (!msg) return;
    setChatInput("");
    setChatHistory((prev) => [...prev, { role: "user", content: msg }]);
    setChatLoading(true);
    try {
      const res = await assistantChat(msg);
      setChatHistory((prev) => [...prev, { role: "assistant", content: res.reply }]);
    } catch {
      setChatHistory((prev) => [...prev, { role: "assistant", content: "抱歉，暂时无法回答。" }]);
    }
    setChatLoading(false);
  };

  const pd = profile?.profile_data || {};
  const assistantName = assistantPersona?.name || "指南针";

  return (
    <StudioShell
      title="个人助手中枢"
      subtitle={`${assistantName} · 偏好画像、推荐与开局助手`}
      eyebrow="assistant / evolution / profile"
      stats={[
        { label: "系统标签", value: `${profile?.tags?.length || 0}` },
        { label: "完成游戏", value: `${profile?.completed_games || 0}` },
        { label: "常用 Agent", value: `${profile?.favorite_agents?.length || 0}` },
        { label: "总局数", value: `${profile?.total_games || 0}` },
      ]}
    >
      <Stack gap="lg">
        <Paper radius="xl" p="lg" className="industrial-card">
          <Group justify="space-between" align="flex-start" wrap="wrap">
            <Stack gap={6} style={{ maxWidth: 760 }}>
              <Text className="monospace-label" size="xs" c="orange.3">personal intelligence center</Text>
              <Title order={2}>个人助手 · {assistantName}</Title>
              <Text c="dimmed" lh={1.75}>
                {assistantPersona?.personaText || "基于你的偏好画像，推荐剧本、角色和 Agent 阵容。"}
              </Text>
              {assistantPersona?.speechStyle && (
                <Text size="sm" c="dimmed">风格：{assistantPersona.speechStyle}</Text>
              )}
            </Stack>
            <Badge variant="light" color="orange" leftSection={<IconSparkles size={14} />}>
              {profile?.level || "Lv. 1"}
            </Badge>
          </Group>
        </Paper>

        <Paper radius="xl" p="lg" className="industrial-card">
          <Tabs value={tab} onChange={setTab}>
            <Tabs.List>
              <Tabs.Tab value="profile" leftSection={<IconBrain size={16} />}>用户画像</Tabs.Tab>
              <Tabs.Tab value="labels" leftSection={<IconUserCircle size={16} />}>偏好标签</Tabs.Tab>
              <Tabs.Tab value="recommend" leftSection={<IconSparkles size={16} />}>推荐</Tabs.Tab>
              <Tabs.Tab value="summary" leftSection={<IconTimeline size={16} />}>个人总结</Tabs.Tab>
              <Tabs.Tab value="prelude" leftSection={<IconMessageCircle2 size={16} />}>助手对话</Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="profile" pt="lg">
              <Grid gutter="lg">
                <Grid.Col span={{ base: 12, lg: 5 }}>
                  <Card radius="xl" className="ambient-grid" p="lg">
                    <Stack gap="sm" mt="sm">
                      {[
                        ["偏好剧本类型", (profile?.preferred_genres || []).join(" / ") || "未设置"],
                        ["偏好难度", profile?.preferred_difficulty || "未设置"],
                        ["偏好时长", profile?.preferred_duration || "未设置"],
                        ...Object.entries(pd).slice(0, 7),
                      ].map(([label, value]) => (
                        <Group key={label} justify="space-between" wrap="wrap">
                          <Text c="dimmed" size="sm">{label}</Text>
                          <Text fw={700}>{value as string}</Text>
                        </Group>
                      ))}
                    </Stack>
                  </Card>
                </Grid.Col>
                <Grid.Col span={{ base: 12, lg: 7 }}>
                  <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
                    {[
                      { label: "总游戏局数", value: profile?.total_games || 0 },
                      { label: "已完成游戏", value: profile?.completed_games || 0 },
                      { label: "累计时长", value: `${profile?.total_hours || 0} 小时` },
                      { label: "常用 Agent", value: (profile?.favorite_agents || []).length || 0 },
                    ].map((item) => (
                      <Card key={item.label} radius="xl" className="industrial-card" p="md">
                        <Text fw={700}>{item.label}</Text>
                        <Text size="xl" fw={900} mt="sm" c="orange.3">{item.value}</Text>
                      </Card>
                    ))}
                  </SimpleGrid>
                </Grid.Col>
              </Grid>
            </Tabs.Panel>

            <Tabs.Panel value="labels" pt="lg">
              <Card radius="xl" className="ambient-grid" p="lg">
                <Group gap="xs" mt="sm">
                  {(profile?.tags || []).length > 0
                    ? profile!.tags.map((item) => <Badge key={item} variant="light" color="gray">{item}</Badge>)
                    : <Text c="dimmed" size="sm">暂无标签，开始游戏后系统会自动生成</Text>}
                </Group>
              </Card>
            </Tabs.Panel>

            <Tabs.Panel value="recommend" pt="lg">
              <Text c="dimmed" mb="md">在「助手对话」中问{assistantName}，获取个性化推荐。</Text>
            </Tabs.Panel>

            <Tabs.Panel value="summary" pt="lg">
              <Timeline active={Math.min(profile?.completed_games || 0, 3)} bulletSize={18} lineWidth={2}>
                <Timeline.Item title="游戏局数"><Text size="sm" c="dimmed">已完成 {profile?.completed_games || 0} 局</Text></Timeline.Item>
                <Timeline.Item title="累计时长"><Text size="sm" c="dimmed">总时长 {profile?.total_hours || 0} 小时</Text></Timeline.Item>
              </Timeline>
            </Tabs.Panel>

            <Tabs.Panel value="prelude" pt="lg">
              <Grid gutter="lg">
                <Grid.Col span={{ base: 12, lg: 6 }}>
                  <Card radius="xl" className="industrial-card" p="lg" style={{ display: "flex", flexDirection: "column", minHeight: 420 }}>
                    <Text fw={700}>{assistantName} · 助手对话</Text>
                    <ScrollArea style={{ flex: 1, marginTop: 12 }} offsetScrollbars>
                      <Stack gap="sm">
                        {chatHistory.map((msg, idx) => (
                          <Paper
                            key={idx}
                            radius="lg"
                            p="sm"
                            className={msg.role === "user" ? "tone-panel" : "ambient-grid"}
                            style={{ alignSelf: msg.role === "user" ? "flex-end" : "flex-start", maxWidth: "85%" }}
                          >
                            <Text size="sm" lh={1.6} style={{ whiteSpace: "pre-wrap" }}>{msg.content}</Text>
                          </Paper>
                        ))}
                        {chatLoading && <Text c="dimmed" size="sm">思考中…</Text>}
                      </Stack>
                    </ScrollArea>
                    <Group gap="xs" mt="md">
                      <TextInput
                        style={{ flex: 1 }}
                        placeholder="输入问题…"
                        value={chatInput}
                        onChange={(e) => setChatInput(e.currentTarget.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleChat()}
                        disabled={chatLoading}
                      />
                      <Button radius="xl" onClick={handleChat} loading={chatLoading} disabled={!chatInput.trim()}>
                        <IconSend size={16} />
                      </Button>
                    </Group>
                  </Card>
                </Grid.Col>
                <Grid.Col span={{ base: 12, lg: 6 }}>
                  <Card radius="xl" className="industrial-card" p="lg">
                    <Text fw={700}>初始引导</Text>
                    <Text size="sm" c="dimmed" mt="sm" lh={1.7} style={{ whiteSpace: "pre-wrap" }}>
                      {chatHistory.find((m) => m.role === "assistant")?.content || "加载中…"}
                    </Text>
                  </Card>
                </Grid.Col>
              </Grid>
            </Tabs.Panel>
          </Tabs>
        </Paper>
      </Stack>
    </StudioShell>
  );
}
