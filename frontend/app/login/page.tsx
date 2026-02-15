import { Card, Center, Stack, Text, Title } from "@mantine/core";
import GoogleLoginButton from "@/components/auth/google-login-button";

export default function LoginPage() {
  return (
    <Center h="100vh" px="md">
      <Card maw={420} p="xl" radius="md" shadow="md" w="100%">
        <Stack gap="md">
          <Title order={2}>Sample Dropbox</Title>
          <Text c="dimmed" size="sm">
            Sign in to view, upload, and download your files.
          </Text>
          <GoogleLoginButton />
        </Stack>
      </Card>
    </Center>
  );
}
