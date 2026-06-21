import React from "react";
import {
  Badge,
  Button,
  Card,
  Grid,
  Group,
  Paper,
  Progress,
  SegmentedControl,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import {
  IconCalendar,
  IconClock,
  IconPlayerPlay,
  IconRefresh,
  IconUsers,
} from "@tabler/icons-react";
import { useNavigate } from "react-router-dom";

import { StudioShell } from "./StudioShell";

type GameStatus = "进行中" | "已完成";

type GameRecord = {
  id: string;
  title: string;
  subtitle: string;
  status: GameStatus;
  playedAt: string;
  duration: string;
  role: string;
  team: string;
  progress: number;
  summary: string;
  cover: string;
};

const gameRecords: GameRecord[] = [
  {
    id: "iron-avenue",
    title: "锈铁大道",
    subtitle: "The Rusted Avenue",
    status: "进行中",
    playedAt: "2026-06-18 20:30",
    duration: "已进行 2 小时 18 分",
    role: "维修员 · 周野",
    team: "2 位好友 · 3 位 Agent",
    progress: 64,
    summary: "调查推进至废弃宿舍区，门禁记录与失踪名单之间仍有一处时间矛盾。",
    cover:
      "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=900&h=1200&fit=crop&auto=format",
  },
  {
    id: "black-archive",
    title: "黑箱档案馆",
    subtitle: "Black Archive",
    status: "已完成",
    playedAt: "2026-06-12 19:45",
    duration: "5 小时 06 分",
    role: "档案管理员 · 林默",
    team: "单人模式 · 5 位 Agent",
    progress: 100,
    summary: "最终还原家族信件的寄送顺序，完成个人支线并解锁隐藏结局。",
    cover:
      "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=900&h=1200&fit=crop&auto=format",
  },
  {
    id: "salt-ward",
    title: "盐雾病房",
    subtitle: "Salt Ward",
    status: "已完成",
    playedAt: "2026-06-03 21:10",
    duration: "3 小时 34 分",
    role: "实习医生 · 许言",
    team: "3 位好友 · 2 位 Agent",
    progress: 100,
    summary: "通过失效监控和药品记录锁定关键时间段，团队推理评价为 A。",
    cover:
      "https://images.unsplash.com/photo-1516738901171-8eb4fc13bd20?w=900&h=1200&fit=crop&auto=format",
  },
  {
    id: "mirror-parade",
    title: "镜面游行",
    subtitle: "Mirror Parade",
    status: "已完成",
    playedAt: "2026-05-25 14:00",
    duration: "6 小时 12 分",
    role: "游行指挥 · 莱恩",
    team: "5 位好友 · 2 位 Agent",
    progress: 100,
    summary: "所属阵营获胜，完成两次关键结盟，但个人隐藏任务未全部达成。",
    cover:
      "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=900&h=1200&fit=crop&auto=format",
  },
];

function MyGamesPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = React.useState("all");

  const filteredRecords = gameRecords.filter(
    (game) =>
      filter === "all" ||
      (filter === "active" && game.status === "进行中") ||
      (filter === "completed" && game.status === "已完成"),
  );

  return (
    <StudioShell
      title="我的游戏"
      subtitle="查看正在进行和已经完成的历史对局。选择具体剧本后，进入对应的游戏主界面继续游玩或查看复盘。"
      eyebrow="my games / history / replay"
      stats={[
        { label: "历史游戏", value: `${gameRecords.length}` },
        { label: "进行中", value: `${gameRecords.filter((game) => game.status === "进行中").length}` },
        { label: "已完成", value: `${gameRecords.filter((game) => game.status === "已完成").length}` },
        { label: "累计时长", value: "37.5 h" },
      ]}
    >
      <Stack gap="lg">
        <Paper radius="xl" p="lg" className="industrial-card">
          <Group justify="space-between" align="center" wrap="wrap">
            <Stack gap={4}>
              <Text className="monospace-label" size="xs" c="orange.3">
                game archive
              </Text>
              <Title order={2}>历史游戏列表</Title>
              <Text c="dimmed">点击任意游戏卡片或操作按钮进入该游戏的主界面。</Text>
            </Stack>
            <SegmentedControl
              value={filter}
              onChange={setFilter}
              data={[
                { label: "全部", value: "all" },
                { label: "进行中", value: "active" },
                { label: "已完成", value: "completed" },
              ]}
            />
          </Group>
        </Paper>

        <SimpleGrid cols={{ base: 1, lg: 2 }} spacing="lg">
          {filteredRecords.map((game) => (
            <Card
              key={game.id}
              radius="xl"
              p="lg"
              className="industrial-card"
              onClick={() => navigate(`/play/${game.id}`)}
              style={{ cursor: "pointer" }}
            >
              <Grid gutter="lg">
                <Grid.Col span={{ base: 12, sm: 4 }}>
                  <Paper
                    radius="lg"
                    h={220}
                    style={{
                      backgroundImage: `linear-gradient(180deg, rgba(0,0,0,0.02), rgba(0,0,0,0.78)), url(${game.cover})`,
                      backgroundPosition: "center",
                      backgroundSize: "cover",
                    }}
                  />
                </Grid.Col>
                <Grid.Col span={{ base: 12, sm: 8 }}>
                  <Stack h="100%" gap="sm">
                    <Group justify="space-between" align="flex-start">
                      <Stack gap={2}>
                        <Text className="monospace-label" size="xs" c="dimmed">
                          {game.subtitle}
                        </Text>
                        <Title order={3}>{game.title}</Title>
                      </Stack>
                      <Badge color={game.status === "进行中" ? "orange" : "teal"} variant="light">
                        {game.status}
                      </Badge>
                    </Group>

                    <Text size="sm" c="dimmed" lh={1.65}>
                      {game.summary}
                    </Text>

                    <Stack gap={6}>
                      <Group gap="xs">
                        <IconCalendar size={15} />
                        <Text size="sm" c="dimmed">{game.playedAt}</Text>
                      </Group>
                      <Group gap="xs">
                        <IconClock size={15} />
                        <Text size="sm" c="dimmed">{game.duration}</Text>
                      </Group>
                      <Group gap="xs">
                        <IconUsers size={15} />
                        <Text size="sm" c="dimmed">{game.team}</Text>
                      </Group>
                    </Stack>

                    <Stack gap={5} mt="auto">
                      <Group justify="space-between">
                        <Text size="sm" fw={700}>{game.role}</Text>
                        <Text size="sm" c="dimmed">{game.progress}%</Text>
                      </Group>
                      <Progress
                        value={game.progress}
                        color={game.status === "进行中" ? "orange" : "teal"}
                        radius="xl"
                      />
                    </Stack>

                    <Button
                      mt="xs"
                      radius="xl"
                      variant={game.status === "进行中" ? "filled" : "light"}
                      color={game.status === "进行中" ? "red" : "gray"}
                      leftSection={
                        game.status === "进行中"
                          ? <IconPlayerPlay size={16} />
                          : <IconRefresh size={16} />
                      }
                      onClick={(event) => {
                        event.stopPropagation();
                        if (game.status === "进行中") {
                          navigate(`/play/${game.id}`);
                        } else {
                          navigate(`/review/${game.id}`);
                        }
                      }}
                    >
                      {game.status === "进行中" ? "继续游戏" : "查看游戏与复盘"}
                    </Button>
                  </Stack>
                </Grid.Col>
              </Grid>
            </Card>
          ))}
        </SimpleGrid>
      </Stack>
    </StudioShell>
  );
}

export { MyGamesPage };
