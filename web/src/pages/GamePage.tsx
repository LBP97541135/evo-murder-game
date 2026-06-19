/**
 * EvoMap Murder Game - Game Page
 *
 * 游戏主界面：准备、进行、复盘的一体化舞台。
 */

import React from "react";
import {
  Badge,
  Box,
  Button,
  Card,
  Divider,
  Grid,
  Group,
  Paper,
  Progress,
  SegmentedControl,
  SimpleGrid,
  Slider,
  Stack,
  Tabs,
  Text,
  Textarea,
  TextInput,
  Timeline,
  Title,
} from "@mantine/core";
import {
  IconAlertTriangle,
  IconArrowBackUp,
  IconBellRinging2,
  IconClock,
  IconMessageCircle2,
  IconPlayerPause,
  IconPlayerPlay,
  IconScribble,
  IconShieldCheck,
  IconUsers,
} from "@tabler/icons-react";
import { useParams } from "react-router-dom";

import { StudioShell } from "./StudioShell";

const scriptMap: Record<string, string> = {
  "iron-avenue": "锈铁大道",
  "black-archive": "黑箱档案馆",
  "mirror-parade": "镜面游行",
  "salt-ward": "盐雾病房",
  "wolf-assembly": "狼群集会",
  "paper-cathedral": "纸穹教堂",
};

function GamePage() {
  const { id = "iron-avenue" } = useParams();
  const scriptTitle = scriptMap[id] || "未知剧本";
  const [mode, setMode] = React.useState("solo");
  const [phase, setPhase] = React.useState("prepare");
  const [activeTab, setActiveTab] = React.useState<string | null>("board");
  const [rage, setRage] = React.useState(42);

  const stageCards = {
    solo: [
      "真人用户 1 名，陪玩 Agent 补齐其他角色",
      "用户自由选择陪玩 Agent",
      "未选择的位置由系统推荐",
      "DM 由 DM-Agent 担任",
    ],
    group: [
      "创建公开或私密房间",
      "邀请好友或在大厅招募真人",
      "允许 Agent 补位并设置自动补齐时间",
      "房主可指定陪玩 Agent 并锁定阵容",
    ],
    quick: [
      "选择剧本后自动推荐角色",
      "自动推荐 DM-Agent 和陪玩 Agent 阵容",
      "自动完成席位分配",
      "直接进入准备阶段",
    ],
  } as const;

  const currentStage = stageCards[mode as keyof typeof stageCards];

  return (
    <StudioShell
      title="游戏主界面"
      subtitle={`当前剧本：${scriptTitle}。这里把单人模式、组队模式、快速开局、现场互动、节奏控制和对局复盘整合成一套沉浸式桌面。`}
      eyebrow="play / live room / replay"
      stats={[
        { label: "当前阶段", value: phase === "prepare" ? "准备" : phase === "live" ? "对局" : "复盘" },
        { label: "剩余时间", value: "02:38" },
        { label: "已上线 Agent", value: "4 / 6" },
        { label: "当前模式", value: mode === "solo" ? "单人" : mode === "group" ? "组队" : "快速开局" },
      ]}
    >
      <Stack gap="lg">
        <Paper radius="xl" p="lg" className="industrial-card">
          <Group justify="space-between" align="flex-start" wrap="wrap">
            <Stack gap={6} style={{ maxWidth: 780 }}>
              <Text className="monospace-label" size="xs" c="orange.3">
                live game room
              </Text>
              <Title order={2}>{scriptTitle}</Title>
              <Text c="dimmed" lh={1.75}>
                用工业质感的房间壳承载沉浸式对局：左侧查看角色和线索，中间进行发言与互动，右侧掌控节奏、DM 提示和房间状态。
              </Text>
            </Stack>
            <Group gap="sm">
              <Badge color="orange" variant="filled" leftSection={<IconUsers size={14} />}>
                4 人在线
              </Badge>
              <Badge color="gray" variant="light" leftSection={<IconClock size={14} />}>
                轮次 03
              </Badge>
              <Badge color="red" variant="light" leftSection={<IconAlertTriangle size={14} />}>
                谨防剧透
              </Badge>
            </Group>
          </Group>
        </Paper>

        <Grid gutter="lg">
          <Grid.Col span={{ base: 12, lg: 4 }}>
            <Paper radius="xl" p="lg" className="industrial-card">
              <Group justify="space-between" mb="md">
                <Title order={4}>游戏模式</Title>
                <SegmentedControl
                  value={mode}
                  onChange={setMode}
                  data={[
                    { label: "单人", value: "solo" },
                    { label: "组队", value: "group" },
                    { label: "快速开局", value: "quick" },
                  ]}
                />
              </Group>
              <Stack gap="sm">
                {currentStage.map((item) => (
                  <Card key={item} radius="lg" className="ambient-grid" p="md">
                    <Text fw={700}>{item}</Text>
                  </Card>
                ))}
              </Stack>

              <Divider my="md" color="rgba(255,255,255,0.08)" />

              <Stack gap="sm">
                <Text fw={700}>DM 主持偏好</Text>
                <Text size="sm" c="dimmed">
                  节奏、提示直接程度、新手教学、氛围描写、复盘详细程度、缩短非关键环节等参数可以在这里统一控制。
                </Text>
                <Slider
                  label={(value) => `${value}%`}
                  value={rage}
                  onChange={setRage}
                  min={0}
                  max={100}
                  color="orange"
                />
                <Group justify="space-between">
                  <Text size="sm" c="dimmed">
                    主动程度
                  </Text>
                  <Text fw={700}>{rage}%</Text>
                </Group>
              </Stack>
            </Paper>

            <Paper radius="xl" p="lg" className="industrial-card" mt="md">
              <Text className="monospace-label" size="xs" c="dimmed">
                role selection
              </Text>
              <Stack gap="sm" mt="sm">
                <Text fw={700}>用户选角</Text>
                <Text size="sm" c="dimmed" lh={1.7}>
                  可自主选择角色，也可以让个人助手推荐角色或随机分配。支持排除凶手位、情感位和高压角色。
                </Text>
                <Group gap="xs">
                  {["自主选择", "助手推荐", "随机分配", "排除凶手位"].map((item) => (
                    <Badge key={item} variant="light" color="gray">
                      {item}
                    </Badge>
                  ))}
                </Group>
              </Stack>
            </Paper>
          </Grid.Col>

          <Grid.Col span={{ base: 12, lg: 5 }}>
            <Paper radius="xl" p="lg" className="industrial-card">
              <Group justify="space-between" align="center">
                <Title order={4}>对局舞台</Title>
                <Tabs value={activeTab} onChange={setActiveTab}>
                  <Tabs.List>
                    <Tabs.Tab value="board">主界面</Tabs.Tab>
                    <Tabs.Tab value="notes">线索</Tabs.Tab>
                    <Tabs.Tab value="replay">复盘</Tabs.Tab>
                  </Tabs.List>
                </Tabs>
              </Group>

              <Tabs value={activeTab} onChange={setActiveTab} mt="md">
                <Tabs.Panel value="board">
                  <Stack gap="md">
                    <Paper radius="xl" p="md" className="ambient-grid">
                      <Group justify="space-between">
                        <Stack gap={4}>
                          <Text className="monospace-label" size="xs" c="dimmed">
                            current phase
                          </Text>
                          <Text fw={700} fz="lg">
                            当前阶段：{phase === "prepare" ? "准备" : phase === "live" ? "讨论" : "复盘"}
                          </Text>
                        </Stack>
                        <SegmentedControl
                          value={phase}
                          onChange={setPhase}
                          data={[
                            { label: "准备", value: "prepare" },
                            { label: "进行中", value: "live" },
                            { label: "复盘", value: "review" },
                          ]}
                        />
                      </Group>
                      <Progress mt="md" value={72} color="orange" radius="xl" />
                      <Group justify="space-between" mt="sm">
                        <Text size="sm" c="dimmed">
                          剩余发言：04
                        </Text>
                        <Text size="sm" c="dimmed">
                          当前任务：收束关键线索链并判断阵营倾向
                        </Text>
                      </Group>
                    </Paper>

                    <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
                      <Card radius="lg" className="ambient-grid" p="md">
                        <Text fw={700}>角色资料</Text>
                        <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                          查看自己与其他角色的公开信息、隐藏关系和身份提示，方便对照推理路径。
                        </Text>
                      </Card>
                      <Card radius="lg" className="ambient-grid" p="md">
                        <Text fw={700}>人物关系</Text>
                        <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                          以线段图方式查看人物之间的血缘、债务、对抗与合作关系。
                        </Text>
                      </Card>
                      <Card radius="lg" className="ambient-grid" p="md">
                        <Text fw={700}>公共线索</Text>
                        <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                          已获得线索、公共信息、私聊记录与系统提示可以在这里统一归档。
                        </Text>
                      </Card>
                      <Card radius="lg" className="ambient-grid" p="md">
                        <Text fw={700}>玩家状态</Text>
                        <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                          查看当前真人玩家和 Agent 状态、主动程度、静音状态与是否被提醒。
                        </Text>
                      </Card>
                    </SimpleGrid>
                  </Stack>
                </Tabs.Panel>

                <Tabs.Panel value="notes">
                  <Stack gap="md">
                    <Textarea
                      label="发言记录"
                      minRows={8}
                      defaultValue={`【01:12】白鸦：线索链里少了关键一环。\n【01:48】回声：先排掉不可能的人，再看门禁记录。\n【02:15】DM：你们可以申请一次提示，但会压缩讨论时间。`}
                    />
                    <Textarea
                      label="私聊记录"
                      minRows={5}
                      defaultValue={`你和纸鸮交换了关于“旧宅楼梯”的记忆碎片。\n燧石提醒你：如果继续追问，可能会触发阵营对立。`}
                    />
                  </Stack>
                </Tabs.Panel>

                <Tabs.Panel value="replay">
                  <Stack gap="md">
                    <Timeline active={3} bulletSize={18} lineWidth={2}>
                      <Timeline.Item title="真相揭示">
                        <Text c="dimmed" size="sm">
                          案件真相、时间线和关键线索链会在这里展开。
                        </Text>
                      </Timeline.Item>
                      <Timeline.Item title="我的推理">
                        <Text c="dimmed" size="sm">
                          记录自己如何从线索导向角色判断，是否有误判和跳步。
                        </Text>
                      </Timeline.Item>
                      <Timeline.Item title="角色任务">
                        <Text c="dimmed" size="sm">
                          查看角色任务完成情况、阵营胜负与投票结果。
                        </Text>
                      </Timeline.Item>
                      <Timeline.Item title="高光片段">
                        <Text c="dimmed" size="sm">
                          本局高光、Agent 表现、DM 表现和互动数据会在这里汇总。
                        </Text>
                      </Timeline.Item>
                    </Timeline>
                  </Stack>
                </Tabs.Panel>
              </Tabs>
            </Paper>

            <Paper radius="xl" p="lg" className="industrial-card" mt="md">
              <Group justify="space-between" wrap="wrap">
                <Title order={4}>与 Agent 互动</Title>
                <Badge variant="light" color="orange">
                  点名 / 提问 / 整理线索 / 私聊 / 缩短发言
                </Badge>
              </Group>
              <Stack gap="sm" mt="md">
                <TextInput placeholder="向某个 Agent 提问..." leftSection={<IconMessageCircle2 size={16} />} />
                <Textarea placeholder="输入角色内私聊内容..." minRows={4} />
                <Group gap="xs">
                  {[
                    "点名某个 Agent 发言",
                    "让 Agent 整理线索",
                    "让 Agent 表达怀疑对象",
                    "请求回顾讨论内容",
                  ].map((item) => (
                    <Button key={item} variant="light" radius="xl">
                      {item}
                    </Button>
                  ))}
                </Group>
              </Stack>
            </Paper>
          </Grid.Col>

          <Grid.Col span={{ base: 12, lg: 3 }}>
            <Stack gap="md">
              <Paper radius="xl" p="lg" className="industrial-card">
                <Group justify="space-between">
                  <Title order={4}>房间控制</Title>
                  <IconShieldCheck size={18} />
                </Group>
                <Stack gap="sm" mt="md">
                  <Button variant="light" leftSection={<IconPlayerPause size={16} />} radius="xl">
                    请求暂停
                  </Button>
                  <Button variant="light" leftSection={<IconPlayerPlay size={16} />} radius="xl">
                    请求继续
                  </Button>
                  <Button variant="light" leftSection={<IconBellRinging2 size={16} />} radius="xl">
                    请求 DM 提示
                  </Button>
                  <Button variant="light" leftSection={<IconArrowBackUp size={16} />} radius="xl">
                    请求 DM 总结
                  </Button>
                  <Button variant="light" color="red" leftSection={<IconAlertTriangle size={16} />} radius="xl">
                    举报剧透
                  </Button>
                </Stack>
              </Paper>

              <Paper radius="xl" p="lg" className="industrial-card">
                <Text className="monospace-label" size="xs" c="dimmed">
                  room state
                </Text>
                <Stack gap="sm" mt="sm">
                  <Group justify="space-between">
                    <Text size="sm" c="dimmed">
                      可用 DM-Agent
                    </Text>
                    <Text fw={700}>2</Text>
                  </Group>
                  <Group justify="space-between">
                    <Text size="sm" c="dimmed">
                      陪玩 Agent
                    </Text>
                    <Text fw={700}>3</Text>
                  </Group>
                  <Group justify="space-between">
                    <Text size="sm" c="dimmed">
                      真人玩家
                    </Text>
                    <Text fw={700}>4</Text>
                  </Group>
                </Stack>
              </Paper>

              <Paper radius="xl" p="lg" className="industrial-card">
                <Text className="monospace-label" size="xs" c="dimmed">
                  rhythm control
                </Text>
                <Text size="sm" c="dimmed" mt="sm" lh={1.7}>
                  支持压缩节奏、延长讨论、跳过非关键环节、设置 Agent 主动程度和静音某个 Agent。
                </Text>
              </Paper>
            </Stack>
          </Grid.Col>
        </Grid>

        <Paper radius="xl" p="lg" className="industrial-card">
          <Title order={3}>开局流程总览</Title>
          <SimpleGrid cols={{ base: 1, md: 3 }} mt="md" spacing="md">
            <Card radius="lg" className="ambient-grid" p="md">
              <Text fw={700}>单人模式</Text>
              <Text size="sm" c="dimmed" mt="sm" lh={1.7}>
                用户选择陪玩 Agent，其余席位由系统推荐，DM 由 DM-Agent 担任，并支持暂停、继续与节奏压缩。
              </Text>
            </Card>
            <Card radius="lg" className="ambient-grid" p="md">
              <Text fw={700}>组队模式</Text>
              <Text size="sm" c="dimmed" mt="sm" lh={1.7}>
                创建公开或私密房间，邀请好友或大厅招募真人，支持 Agent 补位与房主指定阵容。
              </Text>
            </Card>
            <Card radius="lg" className="ambient-grid" p="md">
              <Text fw={700}>快速开局</Text>
              <Text size="sm" c="dimmed" mt="sm" lh={1.7}>
                系统自动推荐角色、DM-Agent 与陪玩阵容，完成席位分配后直接进入准备阶段。
              </Text>
            </Card>
          </SimpleGrid>
        </Paper>
      </Stack>
    </StudioShell>
  );
}

export { GamePage };
