import {
  Avatar,
  Badge,
  Button,
  Card,
  Grid,
  Group,
  Paper,
  Progress,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import {
  IconArchive,
  IconCalendarStats,
  IconChevronRight,
  IconClock,
  IconDeviceGamepad2,
  IconEdit,
  IconMail,
  IconUserCircle,
} from "@tabler/icons-react";
import { useNavigate } from "react-router-dom";

import { StudioShell } from "./StudioShell";

function ProfilePage() {
  const navigate = useNavigate();

  return (
    <StudioShell
      title="个人主页"
      subtitle="管理个人资料、查看游玩偏好，并从这里进入“我的游戏”查看正在进行和已经完成的历史对局。"
      eyebrow="profile / identity / games"
      stats={[
        { label: "玩家等级", value: "Lv. 18" },
        { label: "完成游戏", value: "27" },
        { label: "累计时长", value: "126 h" },
        { label: "常用 Agent", value: "5" },
      ]}
    >
      <Stack gap="lg">
        <Paper radius="xl" p={{ base: "lg", md: "xl" }} className="industrial-card">
          <Group justify="space-between" align="center" wrap="wrap" gap="xl">
            <Group gap="lg" wrap="wrap">
              <Avatar
                size={112}
                radius="xl"
                color="red"
                src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300&h=300&fit=crop&auto=format"
              >
                林
              </Avatar>
              <Stack gap="xs">
                <Group gap="sm">
                  <Title order={2}>林晓青</Title>
                  <Badge color="red" variant="light">资深玩家</Badge>
                </Group>
                <Text c="dimmed">玩家 ID：NOIR_0716</Text>
                <Text c="dimmed" maw={620}>
                  偏爱推理本与工业废墟氛围，习惯先整理时间线，再通过角色关系寻找矛盾点。
                </Text>
                <Group gap="xs">
                  {["推理优先", "偏合作", "中时长", "沉浸适中"].map((tag) => (
                    <Badge key={tag} variant="light" color="gray">{tag}</Badge>
                  ))}
                </Group>
              </Stack>
            </Group>
            <Button variant="light" radius="xl" leftSection={<IconEdit size={16} />}>
              编辑资料
            </Button>
          </Group>
        </Paper>

        <Grid gutter="lg">
          <Grid.Col span={{ base: 12, lg: 7 }}>
            <Paper radius="xl" p="lg" className="industrial-card">
              <Group justify="space-between" mb="lg">
                <Stack gap={3}>
                  <Text className="monospace-label" size="xs" c="orange.3">
                    personal record
                  </Text>
                  <Title order={3}>我的档案</Title>
                </Stack>
                <IconUserCircle size={24} />
              </Group>

              <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
                {[
                  { icon: IconMail, label: "绑定邮箱", value: "linxiaoqing@example.com" },
                  { icon: IconCalendarStats, label: "加入时间", value: "2025 年 9 月 16 日" },
                  { icon: IconClock, label: "偏好时长", value: "3-5 小时" },
                  { icon: IconArchive, label: "偏好类型", value: "推理本 / 情感本" },
                ].map((item) => {
                  const Icon = item.icon;
                  return (
                    <Card key={item.label} radius="lg" p="md" className="ambient-grid">
                      <Group gap="sm" wrap="nowrap">
                        <Icon size={19} />
                        <Stack gap={2}>
                          <Text size="sm" c="dimmed">{item.label}</Text>
                          <Text fw={700}>{item.value}</Text>
                        </Stack>
                      </Group>
                    </Card>
                  );
                })}
              </SimpleGrid>

              <Stack gap="md" mt="lg">
                {[
                  { label: "推理参与度", value: 86 },
                  { label: "沉浸体验偏好", value: 74 },
                  { label: "团队协作倾向", value: 81 },
                ].map((item) => (
                  <Stack key={item.label} gap={6}>
                    <Group justify="space-between">
                      <Text size="sm">{item.label}</Text>
                      <Text size="sm" fw={700}>{item.value}%</Text>
                    </Group>
                    <Progress value={item.value} color="orange" radius="xl" />
                  </Stack>
                ))}
              </Stack>
            </Paper>
          </Grid.Col>

          <Grid.Col span={{ base: 12, lg: 5 }}>
            <Card
              radius="xl"
              p="xl"
              className="tone-hero"
              onClick={() => navigate("/games")}
              style={{ cursor: "pointer", height: "100%" }}
            >
              <Stack h="100%" justify="space-between" gap="xl">
                <Stack gap="md">
                  <Group justify="space-between">
                    <Paper radius="xl" p="md" className="industrial-card">
                      <IconDeviceGamepad2 size={28} />
                    </Paper>
                    <Badge color="orange" variant="filled">1 局进行中</Badge>
                  </Group>
                  <Stack gap="xs">
                    <Text className="monospace-label" size="xs" c="orange.3">
                      my games
                    </Text>
                    <Title order={2}>我的游戏</Title>
                    <Text c="dimmed" lh={1.75}>
                      查看历史游戏列表，继续未完成的对局，或进入已完成游戏查看主界面与复盘内容。
                    </Text>
                  </Stack>
                </Stack>

                <Stack gap="md">
                  <SimpleGrid cols={3}>
                    {[
                      ["历史游戏", "28"],
                      ["已完成", "27"],
                      ["进行中", "1"],
                    ].map(([label, value]) => (
                      <Card key={label} radius="lg" p="sm" className="ambient-grid">
                        <Text fw={800} fz="xl">{value}</Text>
                        <Text size="xs" c="dimmed">{label}</Text>
                      </Card>
                    ))}
                  </SimpleGrid>
                  <Button
                    fullWidth
                    radius="xl"
                    rightSection={<IconChevronRight size={16} />}
                    onClick={(event) => {
                      event.stopPropagation();
                      navigate("/games");
                    }}
                  >
                    进入我的游戏
                  </Button>
                </Stack>
              </Stack>
            </Card>
          </Grid.Col>
        </Grid>
      </Stack>
    </StudioShell>
  );
}

export { ProfilePage };
