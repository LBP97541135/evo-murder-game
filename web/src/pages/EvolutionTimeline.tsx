/**
 * EvoMap Murder Game - Personal Assistant Hub
 *
 * 个人助手中枢：画像、标签、推荐、总结、开局前助手。
 */

import React from "react";
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
} from "@mantine/core";
import {
  IconCalendarStats,
  IconBrain,
  IconMessageCircle2,
  IconSparkles,
  IconTimeline,
  IconUserCircle,
} from "@tabler/icons-react";

import { StudioShell } from "./StudioShell";

function EvolutionTimeline() {
  const [tab, setTab] = React.useState<string | null>("profile");

  return (
    <StudioShell
      title="个人助手中枢"
      subtitle="把用户画像、系统标签、剧本与 Agent 推荐、游玩总结以及开局前助手集中到一个暗色控制台里，作为每次开局前的决策入口。"
      eyebrow="assistant / evolution / profile"
      stats={[
        { label: "系统标签", value: "24" },
        { label: "推荐命中", value: "91%" },
        { label: "常用 Agent", value: "5" },
        { label: "近 30 日局数", value: "18" },
      ]}
    >
      <Stack gap="lg">
        <Paper radius="xl" p="lg" className="industrial-card">
          <Group justify="space-between" align="flex-start" wrap="wrap">
            <Stack gap={6} style={{ maxWidth: 760 }}>
              <Text className="monospace-label" size="xs" c="orange.3">
                personal intelligence center
              </Text>
              <Title order={2}>个人助手像一间资料室，也像一台偏好分析机</Title>
              <Text c="dimmed" lh={1.75}>
                它会读取你的偏好、常用 Agent、游戏时长和互动方式，给出下一局剧本、角色、陪玩阵容和 DM 配置建议。
              </Text>
            </Stack>
            <Badge variant="light" color="orange" leftSection={<IconSparkles size={14} />}>
              可解释推荐
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
                用户标签
              </Tabs.Tab>
              <Tabs.Tab value="recommend" leftSection={<IconSparkles size={16} />}>
                推荐
              </Tabs.Tab>
              <Tabs.Tab value="summary" leftSection={<IconTimeline size={16} />}>
                游玩总结
              </Tabs.Tab>
              <Tabs.Tab value="prelude" leftSection={<IconCalendarStats size={16} />}>
                游戏前助手
              </Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="profile" pt="lg">
              <Grid gutter="lg">
                <Grid.Col span={{ base: 12, lg: 5 }}>
                  <Card radius="xl" className="ambient-grid" p="lg">
                    <Text className="monospace-label" size="xs" c="dimmed">
                      user profile
                    </Text>
                    <Stack gap="sm" mt="sm">
                      {[
                        ["偏好剧本类型", "推理本 / 轻情绪 / 中时长"],
                        ["推理能力倾向", "中高"],
                        ["表演参与度", "中"],
                        ["主动发言程度", "中低"],
                        ["合作 / 对抗偏好", "偏合作"],
                        ["高压盘问敏感度", "较高"],
                        ["喜欢的 DM 风格", "节奏清晰 / 提示克制"],
                        ["喜欢的陪玩风格", "稳、会接话、不抢戏"],
                      ].map(([label, value]) => (
                        <Group key={label} justify="space-between" wrap="wrap">
                          <Text c="dimmed" size="sm">
                            {label}
                          </Text>
                          <Text fw={700}>{value}</Text>
                        </Group>
                      ))}
                    </Stack>
                  </Card>
                </Grid.Col>

                <Grid.Col span={{ base: 12, lg: 7 }}>
                  <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
                    {[
                      { label: "情绪表达偏好", value: 72 },
                      { label: "推理参与度", value: 84 },
                      { label: "表演接受度", value: 46 },
                      { label: "新元素尝试度", value: 61 },
                    ].map((item) => (
                      <Card key={item.label} radius="xl" className="industrial-card" p="md">
                        <Text fw={700}>{item.label}</Text>
                        <Progress value={item.value} mt="md" color="orange" radius="xl" />
                        <Text size="sm" c="dimmed" mt="sm">
                          {item.value}%
                        </Text>
                      </Card>
                    ))}
                  </SimpleGrid>
                </Grid.Col>
              </Grid>
            </Tabs.Panel>

            <Tabs.Panel value="labels" pt="lg">
              <Grid gutter="lg">
                <Grid.Col span={{ base: 12, lg: 5 }}>
                  <Card radius="xl" className="ambient-grid" p="lg">
                    <Text className="monospace-label" size="xs" c="dimmed">
                      generated labels
                    </Text>
                    <Group gap="xs" mt="sm">
                      {[
                        "推理优先",
                        "沉浸适中",
                        "新手局友好",
                        "偏合作",
                        "提示敏感",
                        "工业氛围偏好",
                        "中时长接受",
                      ].map((item) => (
                        <Badge key={item} variant="light" color="gray">
                          {item}
                        </Badge>
                      ))}
                    </Group>
                    <Divider my="md" color="rgba(255,255,255,0.08)" />
                    <Text fw={700}>标签形成依据</Text>
                    <Text size="sm" c="dimmed" mt="sm" lh={1.7}>
                      系统根据常玩剧本、常用 Agent、局数、停留时长、互动密度和复盘反馈生成标签。
                    </Text>
                  </Card>
                </Grid.Col>

                <Grid.Col span={{ base: 12, lg: 7 }}>
                  <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
                    <Card radius="xl" className="industrial-card" p="md">
                      <Text fw={700}>标签编辑</Text>
                      <Text size="sm" c="dimmed" mt="sm">
                        可修改、隐藏、删除或标记不准确的系统标签。
                      </Text>
                      <Button variant="light" radius="xl" mt="md">
                        调整标签
                      </Button>
                    </Card>
                    <Card radius="xl" className="industrial-card" p="md">
                      <Text fw={700}>可信度说明</Text>
                      <Text size="sm" c="dimmed" mt="sm">
                        每个标签都可以追溯到数据依据，方便判断是否需要人工修正。
                      </Text>
                      <Button variant="light" radius="xl" mt="md">
                        查看依据
                      </Button>
                    </Card>
                  </SimpleGrid>
                </Grid.Col>
              </Grid>
            </Tabs.Panel>

            <Tabs.Panel value="recommend" pt="lg">
              <SimpleGrid cols={{ base: 1, md: 2, lg: 3 }} spacing="md">
                {[
                  "推荐下一部适合的剧本",
                  "推荐适合的角色",
                  "推荐适合的陪玩 Agent",
                  "推荐适合的 DM-Agent",
                  "推荐适合的完整阵容",
                  "推荐与历史偏好不同但值得尝试的内容",
                ].map((item) => (
                  <Card key={item} radius="xl" className="industrial-card" p="md">
                    <Group justify="space-between">
                      <Text fw={700}>{item}</Text>
                      <IconSparkles size={16} />
                    </Group>
                    <Text size="sm" c="dimmed" mt="sm" lh={1.7}>
                      系统会展示推荐理由，告诉你为什么这个结果适合当前的情绪、时长和组队状态。
                    </Text>
                  </Card>
                ))}
              </SimpleGrid>
            </Tabs.Panel>

            <Tabs.Panel value="summary" pt="lg">
              <Grid gutter="lg">
                <Grid.Col span={{ base: 12, lg: 5 }}>
                  <Card radius="xl" className="industrial-card" p="lg">
                    <Text className="monospace-label" size="xs" c="dimmed">
                      play summary
                    </Text>
                    <Timeline active={3} bulletSize={18} lineWidth={2} mt="md">
                      <Timeline.Item title="单局总结">
                        <Text size="sm" c="dimmed">
                          记录本局的推理路径、互动片段和情绪波动。
                        </Text>
                      </Timeline.Item>
                      <Timeline.Item title="周报 / 月报">
                        <Text size="sm" c="dimmed">
                          汇总一段时间内的剧本探索、胜负和 Agent 互动。
                        </Text>
                      </Timeline.Item>
                      <Timeline.Item title="年度报告">
                        <Text size="sm" c="dimmed">
                          展示全年变化趋势、偏好迁移和最常用的搭档组合。
                        </Text>
                      </Timeline.Item>
                      <Timeline.Item title="探索地图">
                        <Text size="sm" c="dimmed">
                          将你尝试过的剧本类型和 DM 风格可视化成探索地图。
                        </Text>
                      </Timeline.Item>
                    </Timeline>
                  </Card>
                </Grid.Col>

                <Grid.Col span={{ base: 12, lg: 7 }}>
                  <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
                    {[
                      { title: "偏好变化趋势", value: "最近更偏向推理与中时长" },
                      { title: "推理能力变化", value: "正确率与线索归纳能力上升" },
                      { title: "常用 Agent 关系", value: "与白鸦、暮烛合作更稳定" },
                      { title: "探索地图", value: "情感本和废宅类剧本覆盖上升" },
                    ].map((item) => (
                      <Card key={item.title} radius="xl" className="ambient-grid" p="md">
                        <Text fw={700}>{item.title}</Text>
                        <Text size="sm" c="dimmed" mt="sm" lh={1.7}>
                          {item.value}
                        </Text>
                      </Card>
                    ))}
                  </SimpleGrid>
                </Grid.Col>
              </Grid>
            </Tabs.Panel>

            <Tabs.Panel value="prelude" pt="lg">
              <Grid gutter="lg">
                <Grid.Col span={{ base: 12, lg: 6 }}>
                  <Card radius="xl" className="industrial-card" p="lg">
                    <Text className="monospace-label" size="xs" c="dimmed">
                      pre-game checklist
                    </Text>
                    <Stack gap="sm" mt="sm">
                      {[
                        "询问用户今天想玩什么",
                        "根据时间和情绪推荐剧本",
                        "推荐陪玩阵容",
                        "提醒未完成的存档",
                        "提醒好友房间",
                        "帮助选择角色",
                        "调整本局 Agent 和 DM 参数",
                      ].map((item) => (
                        <Card key={item} radius="lg" className="ambient-grid" p="sm">
                          <Text fw={700}>{item}</Text>
                        </Card>
                      ))}
                    </Stack>
                  </Card>
                </Grid.Col>

                <Grid.Col span={{ base: 12, lg: 6 }}>
                  <Card radius="xl" className="industrial-card" p="lg">
                    <Text fw={700}>今天适合的开局建议</Text>
                    <Text size="sm" c="dimmed" mt="sm" lh={1.7}>
                      如果你今天想要低压沉浸，推荐先看推理本或轻情绪本；如果在线时长较短，优先选择 3 小时以内的局并让 DM 适度压缩节奏。
                    </Text>
                    <TextInput mt="md" placeholder="输入今天想要的氛围..." />
                    <Button variant="light" radius="xl" mt="md" leftSection={<IconMessageCircle2 size={14} />}>
                      让助手开始建议
                    </Button>
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

export { EvolutionTimeline };
