/**
 * EvoMap Murder Game - Personal Assistant Hub
 *
 * 个人助手中枢：画像、标签、推荐、总结、开局前助手。
 * 所有数据来自后端 /users/* 接口。
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
  Progress,
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
  IconArrowRight,
  IconBrain,
  IconCalendarStats,
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

export function EvolutionTimeline() {
  const [tab, setTab] = React.useState<string | null>("profile");
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [profileLoading, setProfileLoading] = useState(true);

  // 助手对话
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [chatLoading, setChatLoading] = useState(false);

  // 加载用户画像
  useEffect(() => {
    getUserProfile()
      .then((data) => {
        setProfile(data.profile);
        setProfileLoading(false);
      })
      .catch(() => setProfileLoading(false));
  }, []);

  // 加载助手历史对话
  useEffect(() => {
    getAssistantHistory()
      .then((data) => {
        if (data.history) setChatHistory(data.history);
      })
      .catch(() => {});
  }, []);

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

  return (
    <StudioShell
      title="个人助手中枢"
      subtitle="偏好画像、推荐与开局助手，数据来自后端用户系统。"
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
              <Text className="monospace-label" size="xs" c="orange.3">
                personal intelligence center
              </Text>
              <Title order={2}>个人助手</Title>
              <Text c="dimmed" lh={1.75}>
                基于你的偏好画像，推荐剧本、角色和 Agent 阵容。也可以在下方聊天框直接问我。
              </Text>
            </Stack>
            <Badge variant="light" color="orange" leftSection={<IconSparkles size={14} />}>
              {profile?.level || "Lv. 1"}
            </Badge>
          </Group>
        </Paper>

        <Paper radius="xl" p="lg" className="industrial-card">
          <Tabs value={tab} onChange={setTab}>
            <Tabs.List>
              <Tabs.Tab value="profile" leftSection={<IconBrain size={16} />}>
                用户画像
              </Tabs.Tab>
              <Tabs.Tab value="labels" leftSection={<IconUserCircle size={16} />}>
                偏好标签
              </Tabs.Tab>
              <Tabs.Tab value="recommend" leftSection={<IconSparkles size={16} />}>
                推荐
              </Tabs.Tab>
              <Tabs.Tab value="summary" leftSection={<IconTimeline size={16} />}>
                个人总结
              </Tabs.Tab>
              <Tabs.Tab value="prelude" leftSection={<IconMessageCircle2 size={16} />}>
                助手对话
              </Tabs.Tab>
            </Tabs.List>

            {/* Tab 1: 用户画像 */}
            <Tabs.Panel value="profile" pt="lg">
              <Grid gutter="lg">
                <Grid.Col span={{ base: 12, lg: 5 }}>
                  <Card radius="xl" className="ambient-grid" p="lg">
                    <Text className="monospace-label" size="xs" c="dimmed">user profile</Text>
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

            {/* Tab 2: 偏好标签 */}
            <Tabs.Panel value="labels" pt="lg">
              <Grid gutter="lg">
                <Grid.Col span={{ base: 12, lg: 5 }}>
                  <Card radius="xl" className="ambient-grid" p="lg">
                    <Text className="monospace-label" size="xs" c="dimmed">generated labels</Text>
                    <Group gap="xs" mt="sm">
                      {(profile?.tags || []).length > 0
                        ? profile!.tags.map((item) => (
                            <Badge key={item} variant="light" color="gray">{item}</Badge>
                          ))
                        : <Text c="dimmed" size="sm">暂无标签，开始游戏后系统会自动生成</Text>}
                    </Group>
                    <Divider my="md" color="rgba(255,255,255,0.08)" />
                    <Text fw={700}>标签形成依据</Text>
                    <Text size="sm" c="dimmed" mt="sm" lh={1.7}>
                      系统根据常玩剧本、常用 Agent、局数和互动数据生成标签。
                    </Text>
                  </Card>
                </Grid.Col>
                <Grid.Col span={{ base: 12, lg: 7 }}>
                  <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
                    <Card radius="xl" className="industrial-card" p="md">
                      <Text fw={700}>标签编辑</Text>
                      <Text size="sm" c="dimmed" mt="sm">可在设置中调整系统标签。</Text>
                      <Button variant="light" radius="xl" mt="md">调整标签</Button>
                    </Card>
                    <Card radius="xl" className="industrial-card" p="md">
                      <Text fw={700}>可信度说明</Text>
                      <Text size="sm" c="dimmed" mt="sm">每个标签都有数据依据。</Text>
                      <Button variant="light" radius="xl" mt="md">查看依据</Button>
                    </Card>
                  </SimpleGrid>
                </Grid.Col>
              </Grid>
            </Tabs.Panel>

            {/* Tab 3: 推荐 */}
            <Tabs.Panel value="recommend" pt="lg">
              <Text c="dimmed" mb="md">直接在下方「助手对话」Tab 中问我，我会基于你的偏好给出推荐。</Text>
              <SimpleGrid cols={{ base: 1, md: 2, lg: 3 }} spacing="md">
                {[
                  "推荐适合你的剧本",
                  "推荐适合的角色",
                  "推荐陪玩 Agent",
                  "推荐 DM Agent",
                  "推荐完整阵容搭配",
                  "推荐你没试过但可能喜欢的类型",
                ].map((item) => (
                  <Card key={item} radius="xl" className="industrial-card" p="md">
                    <Group justify="space-between">
                      <Text fw={700}>{item}</Text>
                      <IconSparkles size={16} />
                    </Group>
                    <Text size="sm" c="dimmed" mt="sm" lh={1.7}>
                      告诉我你的需求，我来推荐。
                    </Text>
                  </Card>
                ))}
              </SimpleGrid>
            </Tabs.Panel>

            {/* Tab 4: 个人总结 */}
            <Tabs.Panel value="summary" pt="lg">
              <Grid gutter="lg">
                <Grid.Col span={{ base: 12, lg: 5 }}>
                  <Card radius="xl" className="industrial-card" p="lg">
                    <Text className="monospace-label" size="xs" c="dimmed">play summary</Text>
                    <Timeline active={Math.min(profile?.completed_games || 0, 3)} bulletSize={18} lineWidth={2} mt="md">
                      <Timeline.Item title="游戏局数">
                        <Text size="sm" c="dimmed">已完成 {profile?.completed_games || 0} 局游戏</Text>
                      </Timeline.Item>
                      <Timeline.Item title="累计时长">
                        <Text size="sm" c="dimmed">总时长 {profile?.total_hours || 0} 小时</Text>
                      </Timeline.Item>
                      <Timeline.Item title="偏好题材">
                        <Text size="sm" c="dimmed">{(profile?.preferred_genres || []).join(" / ") || "未记录"}</Text>
                      </Timeline.Item>
                      <Timeline.Item title="常用 Agent">
                        <Text size="sm" c="dimmed">{(profile?.favorite_agents || []).join("、") || "暂无"}</Text>
                      </Timeline.Item>
                    </Timeline>
                  </Card>
                </Grid.Col>
                <Grid.Col span={{ base: 12, lg: 7 }}>
                  <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
                    {[
                      { title: "偏好变化趋势", value: "更多数据需要更多游戏来生成" },
                      { title: "推理能力变化", value: "持续游戏后系统会分析趋势" },
                      { title: "常用 Agent 关系", value: (profile?.favorite_agents || []).join("、") || "暂无数据" },
                      { title: "探索地图", value: "游戏数据积累后自动生成" },
                    ].map((item) => (
                      <Card key={item.title} radius="xl" className="ambient-grid" p="md">
                        <Text fw={700}>{item.title}</Text>
                        <Text size="sm" c="dimmed" mt="sm" lh={1.7}>{item.value}</Text>
                      </Card>
                    ))}
                  </SimpleGrid>
                </Grid.Col>
              </Grid>
            </Tabs.Panel>

            {/* Tab 5: 助手对话 */}
            <Tabs.Panel value="prelude" pt="lg">
              <Grid gutter="lg">
                <Grid.Col span={{ base: 12, lg: 6 }}>
                  <Card radius="xl" className="industrial-card" p="lg" style={{ height: "100%", display: "flex", flexDirection: "column" }}>
                    <Text className="monospace-label" size="xs" c="dimmed">assistant chat</Text>
                    <Text fw={700} mt="sm">直接问我，我来帮你推荐和解答</Text>
                    <ScrollArea style={{ flex: 1, marginTop: 12 }} offsetScrollbars>
                      <Stack gap="sm">
                        {chatHistory.length === 0 && (
                          <Text c="dimmed" size="sm">可以问：推荐一个推理本 / 我今天适合玩什么 / 介绍一下白鸦的能力</Text>
                        )}
                        {chatHistory.map((msg, idx) => (
                          <Paper
                            key={idx}
                            radius="lg"
                            p="sm"
                            className={msg.role === "user" ? "tone-panel" : "ambient-grid"}
                            style={{ alignSelf: msg.role === "user" ? "flex-end" : "flex-start", maxWidth: "85%" }}
                          >
                            <Text size="sm" lh={1.6}>{msg.content}</Text>
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
                    <Text fw={700}>今天适合的开局建议</Text>
                    <Text size="sm" c="dimmed" mt="sm" lh={1.7}>
                      你的偏好：{(profile?.preferred_genres || []).join("、") || "未设置"}。
                      可以试试在下方聊天框输入「推荐一个适合我的剧本」。
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