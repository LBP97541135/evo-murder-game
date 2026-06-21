import React from "react";
import {
  ActionIcon,
  AppShell,
  Avatar,
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
  IconBrain,
  IconDeviceGamepad2,
  IconLayoutDashboard,
  IconRobot,
  IconVolume,
  IconVolumeOff,
} from "@tabler/icons-react";
import { useBgm } from "../hooks/useBgm";

const NAV_ITEMS = [
  { key: "library", label: "剧本库", to: "/library", icon: IconArchive },
  { key: "games", label: "我的游戏", to: "/games", icon: IconDeviceGamepad2 },
  { key: "agents", label: "Agent 广场", to: "/agents", icon: IconRobot },
  { key: "evolution", label: "个人助手", to: "/evolution", icon: IconBrain },
];

type StudioShellProps = {
  title: string;
  subtitle: string;
  eyebrow: string;
  stats: Array<{ label: string; value: string }>;
  hero?: React.ReactNode;
  children: React.ReactNode;
};

export function StudioShell({
  title,
  subtitle,
  eyebrow,
  stats,
  hero,
  children,
}: StudioShellProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const bgm = useBgm();
  const isItemActive = (item: (typeof NAV_ITEMS)[number]) =>
    location.pathname === item.to ||
    location.pathname.startsWith(`${item.to}/`) ||
    (item.key === "games" && location.pathname.startsWith("/play/"));

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
                const active = isItemActive(item);
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
              {/* 背景音乐控制按钮 */}
              <ActionIcon
                variant="subtle"
                color="gray"
                radius="xl"
                size="lg"
                onClick={() => bgm.toggle()}
                aria-label={bgm.isPlaying ? "暂停背景音乐" : "播放背景音乐"}
              >
                {bgm.isPlaying ? <IconVolume size={20} /> : <IconVolumeOff size={20} />}
              </ActionIcon>
              {/* <Button
                variant="light"
                leftSection={<IconDeviceGamepad2 size={16} />}
                onClick={() => navigate("/games")}
                radius="xl"
                visibleFrom="lg"
              >
                我的游戏
              </Button> */}
              <Group
                gap="sm"
                wrap="nowrap"
                onClick={() => navigate("/profile")}
                role="link"
                aria-label="进入林晓青的个人主页"
                tabIndex={0}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    navigate("/profile");
                  }
                }}
                style={{ cursor: "pointer" }}
              >
                <Avatar
                  size={42}
                  radius="xl"
                  color="red"
                  src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=160&h=160&fit=crop&auto=format"
                >
                  林
                </Avatar>
                <Stack gap={0} visibleFrom="sm">
                  <Text size="sm" fw={800}>林晓青</Text>
                  <Text size="xs" c="dimmed">个人主页</Text>
                </Stack>
              </Group>
            </Group>
          </Group>
        </Container>
      </AppShell.Header>

      <AppShell.Main className="studio-main">
        <Container size="7xl" py={{ base: "lg", md: "xl" }}>
          <Stack gap="xl">
            {hero ?? (
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
            )}

            <Box>{children}</Box>
          </Stack>
        </Container>
      </AppShell.Main>
    </AppShell>
  );
}
