import React from "react";
import {
  AppShell,
  Badge,
  Box,
  Button,
  Container,
  Group,
  Paper,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import { useLocation, useNavigate } from "react-router-dom";
import {
  IconArchive,
  IconBolt,
  IconBrain,
  IconLayoutDashboard,
  IconPlayerPlay,
  IconRobot,
  IconTimelineEventExclamation,
} from "@tabler/icons-react";

const NAV_ITEMS = [
  { key: "library", label: "剧本库", to: "/library", icon: IconArchive },
  { key: "play", label: "游戏主界面", to: "/play/iron-avenue", icon: IconPlayerPlay },
  { key: "agents", label: "Agent 广场", to: "/agents", icon: IconRobot },
  { key: "evolution", label: "个人助手", to: "/evolution", icon: IconBrain },
];

type StudioShellProps = {
  title: string;
  subtitle: string;
  eyebrow: string;
  stats: Array<{ label: string; value: string }>;
  children: React.ReactNode;
};

export function StudioShell({
  title,
  subtitle,
  eyebrow,
  stats,
  children,
}: StudioShellProps) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <AppShell className="studio-shell" header={{ height: 88 }} padding={0}>
      <AppShell.Header className="studio-header">
        <Container size="7xl" h="100%">
          <Group h="100%" justify="space-between" align="center" wrap="nowrap">
            <Group gap="md" wrap="nowrap">
              <Paper radius="xl" p="sm" className="industrial-card">
                <IconLayoutDashboard size={22} stroke={1.8} />
              </Paper>
              <Stack gap={2}>
                <Group gap={8} align="center" wrap="nowrap">
                  <Text
                    fw={900}
                    fz={{ base: "md", md: "lg" }}
                    style={{ fontFamily: "'Cinzel Decorative', serif", letterSpacing: "0.15em" }}
                  >
                    暗夜剧场
                  </Text>
                  <Badge variant="light" color="red">
                    Noir Theatre
                  </Badge>
                </Group>
                <Text size="sm" c="dimmed">
                  剧本杀、陪玩 Agent、DM 和个人助手的暗黑工业舞台
                </Text>
              </Stack>
            </Group>

            <Group gap="xs" wrap="nowrap" visibleFrom="md">
              {NAV_ITEMS.map((item) => {
                const active =
                  location.pathname === item.to ||
                  location.pathname.startsWith(`${item.to}/`);
                const Icon = item.icon;
                return (
                  <Button
                    key={item.key}
                    variant={active ? "filled" : "subtle"}
                    color={active ? "red" : "gray"}
                    leftSection={<Icon size={16} />}
                    onClick={() => navigate(item.to)}
                    radius="xl"
                  >
                    {item.label}
                  </Button>
                );
              })}
            </Group>

            <Group gap="xs" wrap="nowrap">
              <Button
                variant="light"
                leftSection={<IconBolt size={16} />}
                onClick={() => navigate("/library")}
                radius="xl"
              >
                快速开局
              </Button>
              <Button
                variant="default"
                leftSection={<IconTimelineEventExclamation size={16} />}
                onClick={() => navigate("/evolution")}
                radius="xl"
              >
                个人助手
              </Button>
            </Group>
          </Group>
        </Container>
      </AppShell.Header>

      <AppShell.Main className="studio-main">
        <Container size="7xl" py={{ base: "lg", md: "xl" }}>
          <Stack gap="xl">
            <Paper radius="xl" p={{ base: "lg", md: "xl" }} className="studio-hero">
              <Group justify="space-between" align="flex-start" wrap="wrap" gap="xl">
                <Stack gap="sm" style={{ maxWidth: 760 }}>
                  <Text className="monospace-label" size="xs" c="red.3">
                    {eyebrow}
                  </Text>
                  <Title order={1} fz={{ base: 30, md: 48 }} lh={1.05}>
                    {title}
                  </Title>
                  <Text size="lg" c="dimmed" lh={1.8} maw={700}>
                    {subtitle}
                  </Text>
                </Stack>

                <Paper radius="xl" p="lg" className="tone-panel" style={{ minWidth: 300 }}>
                  <Text className="monospace-label" size="xs" c="dimmed" mb={8}>
                    signal board
                  </Text>
                  <Stack gap="sm">
                    {stats.map((stat) => (
                      <Group key={stat.label} justify="space-between" wrap="nowrap">
                        <Text size="sm" c="dimmed">
                          {stat.label}
                        </Text>
                        <Text fw={800}>{stat.value}</Text>
                      </Group>
                    ))}
                  </Stack>
                </Paper>
              </Group>
            </Paper>

            <Group gap="sm" wrap="wrap">
              {NAV_ITEMS.map((item) => {
                const active =
                  location.pathname === item.to ||
                  location.pathname.startsWith(`${item.to}/`);
                return (
                  <Button
                    key={item.key}
                    variant={active ? "filled" : "subtle"}
                    color={active ? "red" : "gray"}
                    radius="xl"
                    onClick={() => navigate(item.to)}
                  >
                    {item.label}
                  </Button>
                );
              })}
            </Group>

            <Box>{children}</Box>
          </Stack>
        </Container>
      </AppShell.Main>
    </AppShell>
  );
}
