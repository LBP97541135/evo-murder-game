import React from "react";
import {
  Badge,
  Box,
  Button,
  Grid,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import {
  IconArrowLeft,
  IconClock,
  IconRobot,
  IconStarFilled,
  IconUsers,
} from "@tabler/icons-react";
import { Navigate, useNavigate, useParams } from "react-router-dom";

import { useScript } from "../api/hooks";
import { StudioShell } from "./StudioShell";

function ScriptDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { script, loading, error } = useScript(id);

  if (!script && !loading) {
    return <Navigate to="/library" replace />;
  }
  if (!script) return null;

  return (
    <StudioShell
      title={script.title}
      subtitle={script.description}
      eyebrow={`script archive / ${script.subtitle}`}
      stats={[
        { label: "评分", value: script.rating.toFixed(1) },
        { label: "角色人数", value: `${script.playerCount} 人` },
        { label: "预计时长", value: script.duration },
        { label: "难度", value: script.difficulty },
      ]}
    >
      <Stack gap="xl">
        {(loading || error) && (
          <Paper radius="xl" p="sm" className="industrial-card">
            <Text size="sm" c={error ? "yellow" : "dimmed"}>
              {loading ? "正在从后端加载剧本详情…" : `后端详情加载失败，当前展示本地数据：${error}`}
            </Text>
          </Paper>
        )}
        <Button
          variant="subtle"
          color="gray"
          leftSection={<IconArrowLeft size={17} />}
          onClick={() => navigate("/library")}
          style={{ alignSelf: "flex-start" }}
        >
          返回剧本库
        </Button>

        <Grid gutter="xl" align="stretch">
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Box
              className="script-detail-cover"
              style={{
                backgroundImage: `linear-gradient(180deg, rgba(0,0,0,.04), rgba(0,0,0,.72)), url(${script.cover})`,
              }}
            >
              <Stack justify="flex-end" h="100%" p="xl">
                <Text className="monospace-label" size="xs" c="red.2">{script.subtitle}</Text>
                <Title order={2}>{script.title}</Title>
                <Group gap="xs">
                  <Badge color="red">{script.genre}</Badge>
                  <Badge color="yellow" variant="light">{script.difficulty}</Badge>
                  <Badge color="gray" variant="light" leftSection={<IconStarFilled size={12} />}>
                    {script.rating.toFixed(1)}
                  </Badge>
                </Group>
              </Stack>
            </Box>
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 8 }}>
            <Stack gap="lg" h="100%">
              <Paper radius="xl" p="xl" className="industrial-card">
                <Text className="monospace-label" size="xs" c="red.3">script details</Text>
                <Title order={2} mt="sm">剧本详情</Title>
                <Text c="dimmed" mt="md" lh={1.9} fz="lg">{script.details}</Text>
                <SimpleGrid cols={{ base: 1, sm: 3 }} mt="xl">
                  <Paper className="tone-panel" radius="lg" p="md">
                    <IconUsers size={20} />
                    <Text size="sm" c="dimmed" mt="sm">角色人数</Text>
                    <Text fw={900} fz="xl">{script.playerCount} 人</Text>
                  </Paper>
                  <Paper className="tone-panel" radius="lg" p="md">
                    <IconClock size={20} />
                    <Text size="sm" c="dimmed" mt="sm">预计时长</Text>
                    <Text fw={900} fz="xl">{script.duration}</Text>
                  </Paper>
                  <Paper className="tone-panel" radius="lg" p="md">
                    <IconStarFilled size={20} />
                    <Text size="sm" c="dimmed" mt="sm">玩家评分</Text>
                    <Text fw={900} fz="xl">{script.rating.toFixed(1)}</Text>
                  </Paper>
                </SimpleGrid>
              </Paper>

              <Paper radius="xl" p="xl" className="industrial-card" style={{ flex: 1 }}>
                <Group gap="sm">
                  <IconRobot size={20} />
                  <Title order={3}>Agent Fit</Title>
                </Group>
                <Text c="dimmed" mt="sm">适合主持或陪玩本剧本的 Agent 阵容。</Text>
                <Group gap="sm" mt="lg">
                  {script.agentFit.map((agent) => (
                    <Badge key={agent} size="lg" color="red" variant="light">{agent}</Badge>
                  ))}
                </Group>
              </Paper>
            </Stack>
          </Grid.Col>
        </Grid>

        <Grid gutter="xl">
          <Grid.Col span={{ base: 12, md: 7 }}>
            <Paper radius="xl" p="xl" className="industrial-card" h="100%">
              <Text className="monospace-label" size="xs" c="dimmed">cast list</Text>
              <Title order={3} mt="sm">剧本角色</Title>
              <SimpleGrid cols={{ base: 2, sm: 3 }} mt="lg">
                {script.roles.map((role, index) => (
                  <Paper key={role} radius="lg" p="md" className="tone-panel">
                    <Text size="xs" c="red.3" className="monospace-label">
                      role {String(index + 1).padStart(2, "0")}
                    </Text>
                    <Text fw={800} mt={6}>{role}</Text>
                  </Paper>
                ))}
              </SimpleGrid>
            </Paper>
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 5 }}>
            <Paper radius="xl" p="xl" className="industrial-card" h="100%">
              <Text className="monospace-label" size="xs" c="dimmed">recommended audience</Text>
              <Title order={3} mt="sm">适合人群</Title>
              <Text c="dimmed" mt="sm" lh={1.7}>根据剧本难度、节奏和主要体验整理。</Text>
              <Group gap="sm" mt="lg">
                {script.audienceTags.map((tag) => (
                  <Badge key={tag} size="lg" color="gray" variant="light">{tag}</Badge>
                ))}
              </Group>
            </Paper>
          </Grid.Col>
        </Grid>
      </Stack>
    </StudioShell>
  );
}

export { ScriptDetailPage };
