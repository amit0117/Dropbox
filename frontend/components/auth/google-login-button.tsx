"use client";

import { Button } from "@mantine/core";
import { createClient } from "@/utils/supabase/client";
import { useState } from "react";

const GoogleLoginButton = () => {
  const [isLoading, setIsLoading] = useState(false);

  const handleGoogleLogin = async () => {
    try {
      setIsLoading(true);
      const supabase = createClient();
      const params = new URLSearchParams(window.location.search);
      const finalRedirect = params.get("finalRedirect") || "/";
      await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: `${window.location.origin}/auth/callback?finalRedirect=${encodeURIComponent(finalRedirect)}`,
          queryParams: {
            access_type: "offline",
            prompt: "select_account",
          },
        },
      });
    } catch {
      console.error("Error signing in with Google");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      fullWidth
      loading={isLoading}
      onClick={handleGoogleLogin}
      radius="xl"
      size="md"
    >
      {isLoading ? "Connecting..." : "Sign in with Google"}
    </Button>
  );
};

export default GoogleLoginButton;
