import React from "react";
import {
  ActionIcon,
  Badge,
  Box,
  Card,
  Grid,
  Group,
  Paper,
  SegmentedControl,
  Select,
  SimpleGrid,
  Stack,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import {
  IconChevronLeft,
  IconChevronRight,
  IconClock,
  IconCrown,
  IconHeart,
  IconPlayerPlay,
  IconSearch,
  IconSparkles,
  IconStarFilled,
  IconUsers,
} from "@tabler/icons-react";
import { useNavigate } from "react-router-dom";

import { useScripts } from "../api/hooks";
import { StudioShell } from "./StudioShell";

const genreOptions = ["全部", "情感本", "推理本", "机制本", "阵营本"];
const difficultyOptions = ["全部", "入门", "进阶", "硬核"];
const feedOptions = [
  { value: "featured", label: "精选" },
  { value: "hot", label: "热门" },
  { value: "new", label: "新上线" },
  { value: "recommended", label: "推荐" },
  { value: "friends", label: "好友玩过" },
];

function ScriptLibrary() {
  const navigate = useNavigate();
  const { scripts, loading, error } = useScripts();
  const hotScripts = scripts.filter((script) => script.hot);
  const [activeSlide, setActiveSlide] = React.useState(0);
  const [query, setQuery] = React.useState("");
  const [genre, setGenre] = React.useState("全部");
  const [difficulty, setDifficulty] = React.useState("全部");
  const [feed, setFeed] = React.useState("featured");

  React.useEffect(() => {
    const timer = window.setInterval(
      () => setActiveSlide((current) => hotScripts.length ? (current + 1) % hotScripts.length : 0),
      5000,
    );
    return () => window.clearInterval(timer);
  }, [hotScripts.length]);

  const featured = hotScripts[activeSlide] || scripts[0];
  const filtered = scripts.filter((script) => {
    const keyword = query.trim().toLowerCase();
    const hitQuery =
      !keyword ||
      script.title.toLowerCase().includes(keyword) ||
      script.subtitle.toLowerCase().includes(keyword) ||
      script.tags.some((tag) => tag.toLowerCase().includes(keyword));
    const hitGenre = genre === "全部" || script.genre === genre;
    const hitDifficulty = difficulty === "全部" || script.difficulty === difficulty;
    const hitFeed =
      feed === "featured" ||
      (feed === "hot" && script.hot) ||
      (feed === "new" && script.newArrival) ||
      (feed === "recommended" && script.recommended) ||
      (feed === "friends" && script.friendsPlayed);
    return hitQuery && hitGenre && hitDifficulty && hitFeed;
  });

  const showSlide = (index: number) => {
    if (!hotScripts.length) return;
    setActiveSlide((index + hotScripts.length) % hotScripts.length);
  };

  const hero = featured ? (
    <Grid gutter="xl" align="stretch">
      <Grid.Col span={{ base: 12, lg: 8 }}>
        <Paper
          radius="xl"
          className="script-carousel"
          onClick={() => navigate(`/library/${featured.id}`)}
          style={{
            backgroundImage: `linear-gradient(90deg, rgba(7,5,5,.96) 0%, rgba(11,7,7,.78) 48%, rgba(8,5,5,.2) 100%), url(${featured.cover})`,
          }}
        >
          <Stack justify="space-between" h="100%" className="script-carousel__content">
            <Group justify="space-between" align="flex-start">
              <Badge color="red" variant="filled" leftSection={<IconCrown size={13} />}>
                热门剧本 · {activeSlide + 1}/{hotScripts.length}
              </Badge>
              <Group gap="xs">
                <ActionIcon
                  variant="light"
                  color="gray"
                  radius="xl"
                  aria-label="上一个热门剧本"
                  onClick={(event) => {
                    event.stopPropagation();
                    showSlide(activeSlide - 1);
                  }}
                >
                  <IconChevronLeft size={18} />
                </ActionIcon>
                <ActionIcon
                  variant="light"
                  color="gray"
                  radius="xl"
                  aria-label="下一个热门剧本"
                  onClick={(event) => {
                    event.stopPropagation();
                    showSlide(activeSlide + 1);
                  }}
                >
                  <IconChevronRight size={18} />
                </ActionIcon>
              </Group>
            </Group>

            <Stack gap="sm" maw={610}>
              <Text className="monospace-label" size="xs" c="red.2">
                {featured.subtitle}
              </Text>
              <Title order={1} fz={{ base: 38, md: 62 }} lh={0.95}>
                {featured.title}
              </Title>
              <Text size="lg" c="gray.3" lh={1.7} lineClamp={2}>
                {featured.description}
              </Text>
              <Group gap="xs">
                <Badge variant="light" color="gray">{featured.genre}</Badge>
                <Badge variant="light" color="yellow">{featured.difficulty}</Badge>
                <Badge variant="light" color="red" leftSection={<IconStarFilled size={12} />}>
                  {featured.rating.toFixed(1)}
                </Badge>
              </Group>
              <Group gap="xl">
                <Group gap={6}><IconUsers size={17} /><Text fw={700}>{featured.players}</Text></Group>
                <Group gap={6}><IconClock size={17} /><Text fw={700}>{featured.duration}</Text></Group>
                <Text size="sm" c="red.2">点击查看剧本详情 →</Text>
              </Group>
            </Stack>

            <Group gap={7}>
              {hotScripts.map((script, index) => (
                <Box
                  key={script.id}
                  className={index === activeSlide ? "script-carousel__dot is-active" : "script-carousel__dot"}
                  onClick={(event) => {
                    event.stopPropagation();
                    showSlide(index);
                  }}
                />
              ))}
            </Group>
          </Stack>
        </Paper>
      </Grid.Col>

      <Grid.Col span={{ base: 12, lg: 4 }}>
        <Paper radius="xl" p="xl" className="tone-panel signal-board" h="100%">
          <Text className="monospace-label" size="xs" c="dimmed" mb="lg">
            signal board
          </Text>
          <Title order={3} mb="xl">剧本库实时信号</Title>
          <Stack gap="lg">
            {[
              { label: "剧本总数", value: scripts.length },
              { label: "热门剧本", value: scripts.filter((item) => item.hot).length },
              { label: "新上线", value: scripts.filter((item) => item.newArrival).length },
              { label: "平均评分", value: (scripts.reduce((sum, item) => sum + item.rating, 0) / scripts.length).toFixed(1) },
            ].map((stat) => (
              <Group key={stat.label} justify="space-between" className="signal-board__row">
                <Text c="dimmed">{stat.label}</Text>
                <Text fw={900} fz={24}>{stat.value}</Text>
              </Group>
            ))}
          </Stack>
        </Paper>
      </Grid.Col>
    </Grid>
  ) : null;

  return (
    <StudioShell title="剧本库" subtitle="" eyebrow="" stats={[]} hero={hero}>
      <Stack gap="xl">
        {(loading || error) && (
          <Paper radius="xl" p="sm" className="industrial-card">
            <Text size="sm" c={error ? "red" : "dimmed"}>
              {loading ? "正在从后端加载剧本…" : `后端剧本加载失败：${error}`}
            </Text>
          </Paper>
        )}

        {/* 继续上局游戏 — 红色细横条 */}
        {(() => {
          const activeIds = ["iron-avenue", "black-archive", "salt-ward", "mirror-parade"]
            .filter((id) => window.localStorage.getItem(`game-session:${id}`));
          if (activeIds.length === 0) return null;
          const lastId = activeIds[0];
          const titles: Record<string, string> = {
            "iron-avenue": "锈铁大道",
            "black-archive": "黑箱档案馆",
            "salt-ward": "盐雾病房",
            "mirror-parade": "镜面游行",
          };
          return (
            <Paper
              radius="xl"
              py="sm"
              px="lg"
              style={{
                background: "linear-gradient(90deg, rgba(201, 42, 42, 0.85), rgba(250, 82, 82, 0.55))",
                cursor: "pointer",
                border: "1px solid rgba(250, 82, 82, 0.4)",
              }}
              onClick={() => navigate(`/play/${lastId}`)}
            >
              <Group justify="center" gap="sm">
                <IconPlayerPlay size={18} />
                <Text fw={700} size="sm" style={{ letterSpacing: 1 }}>
                  继续上局游戏
                </Text>
                <Badge variant="filled" color="red" size="sm">{titles[lastId] || lastId}</Badge>
              </Group>
            </Paper>
          );
        })()}

        <Paper radius="xl" p="lg" className="industrial-card">
          <Grid gutter="md" align="end">
            <Grid.Col span={{ base: 12, md: 5 }}>
              <TextInput
                label="搜索剧本"
                placeholder="剧本名称 / 标签 / 英文标题"
                leftSection={<IconSearch size={16} />}
                value={query}
                onChange={(event) => setQuery(event.currentTarget.value)}
                radius="xl"
              />
            </Grid.Col>
            <Grid.Col span={{ base: 6, md: 2 }}>
              <Select label="题材" value={genre} onChange={(value) => setGenre(value || "全部")} data={genreOptions} />
            </Grid.Col>
            <Grid.Col span={{ base: 6, md: 2 }}>
              <Select label="难度" value={difficulty} onChange={(value) => setDifficulty(value || "全部")} data={difficultyOptions} />
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 3 }}>
              <SegmentedControl fullWidth value={feed} onChange={setFeed} data={feedOptions} />
            </Grid.Col>
          </Grid>
        </Paper>

        <Group justify="space-between" align="center">
          <Group gap="xs">
            <Badge color="red" variant="filled" leftSection={<IconCrown size={14} />}>剧本精选</Badge>
            <Badge color="gray" variant="light" leftSection={<IconSparkles size={14} />}>{filtered.length} 个结果</Badge>
          </Group>
          <Text size="sm" c="dimmed">点击剧本进入详情页</Text>
        </Group>

        {filtered.length > 0 ? (
          <SimpleGrid cols={{ base: 1, md: 2, xl: 3 }} spacing="lg">
            {filtered.map((script) => (
              <Card
                key={script.id}
                radius="xl"
                className="industrial-card script-library-card"
                p={0}
                onClick={() => navigate(`/library/${script.id}`)}
              >
                <Box
                  className="script-library-card__cover"
                  style={{ backgroundImage: `linear-gradient(180deg, transparent 35%, rgba(8,5,5,.95)), url(${script.cover})` }}
                >
                  <Group justify="space-between" p="md">
                    <Badge color="red" variant="filled">{script.genre}</Badge>
                    <Badge color="dark" variant="filled" leftSection={<IconStarFilled size={12} />}>
                      {script.rating.toFixed(1)}
                    </Badge>
                  </Group>
                </Box>
                <Stack p="lg" gap="sm">
                  <Text className="monospace-label" size="xs" c="dimmed">{script.subtitle}</Text>
                  <Title order={3}>{script.title}</Title>
                  <Text c="dimmed" lineClamp={2} lh={1.6}>{script.description}</Text>
                  <Group gap="xs">
                    {script.tags.slice(0, 3).map((tag) => <Badge key={tag} variant="light" color="gray">{tag}</Badge>)}
                  </Group>
                  <Group justify="space-between" mt="xs">
                    <Group gap={6}><IconUsers size={16} /><Text size="sm">{script.players}</Text></Group>
                    <Group gap={6}><IconClock size={16} /><Text size="sm">{script.duration}</Text></Group>
                  </Group>
                </Stack>
              </Card>
            ))}
          </SimpleGrid>
        ) : (
          <Paper radius="xl" p="xl" className="industrial-card">
            <Text ta="center" c="dimmed">没有符合当前条件的剧本。</Text>
          </Paper>
        )}

        <Paper radius="xl" p="lg" className="industrial-card">
          <Group justify="space-between" align="flex-start">
            <Stack gap={4}>
              <Text className="monospace-label" size="xs" c="dimmed">player feedback</Text>
              <Title order={3}>热门剧本与玩家反馈</Title>
            </Stack>
            <Badge variant="light" color="red" leftSection={<IconHeart size={14} />}>本周好评 96%</Badge>
          </Group>
          <SimpleGrid cols={{ base: 1, md: 3 }} mt="md" spacing="md">
            {[
              ["林晓青", "《锈铁大道》的线索链很扎实，最后一轮反转值得复盘。"],
              ["陈墨", "主持节奏稳定，信息给得克制，沉浸感保持到了结尾。"],
              ["苏颜", "第一次玩选了《盐雾病房》，规则清楚，没有入门压力。"],
            ].map(([name, text]) => (
              <Card key={name} radius="lg" className="tone-panel" p="md">
                <Text fw={800}>{name}</Text>
                <Text size="sm" c="dimmed" mt="sm" lh={1.7}>{text}</Text>
              </Card>
            ))}
          </SimpleGrid>
        </Paper>
      </Stack>
    </StudioShell>
  );
}

export { ScriptLibrary };
