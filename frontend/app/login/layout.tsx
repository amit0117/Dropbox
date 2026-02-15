import type { Metadata } from "next";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Login | Sample Dropbox",
  description: "Sign in to your account",
};

const LoginLayout = ({ children }: { children: React.ReactNode }) => {
  return <main className={`min-h-screen ${inter.className}`}>{children}</main>;
};

export default LoginLayout;
