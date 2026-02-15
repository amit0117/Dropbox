import Link from "next/link";
import { Button, Center, Stack, Text, Title } from "@mantine/core";

export default function AuthCodeErrorPage() {
  return (
    <Center h="100vh" px="md">
      <Stack align="center" gap="sm">
        <Title order={2}>Authentication failed</Title>
        <Text c="dimmed">We could not complete sign-in. Please try again.</Text>
        <Button component="a" href="/login">
          Back to login
        </Button>
        <Link href="/">Go to home</Link>
      </Stack>
    </Center>
  );
}
