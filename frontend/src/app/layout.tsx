import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";
import { Providers } from "@/providers";
import { AuthWrapper } from "@/components/AuthWrapper";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Persynix Bot | Enterprise WhatsApp AI Platform",
  description: "Enterprise-grade AI-powered WhatsApp Automation Dashboard — manage conversations, AI agents, workflows, and tickets at scale.",
  keywords: ["WhatsApp", "AI", "automation", "chatbot", "enterprise", "dashboard"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable} dark antialiased`}>
      <body className="flex h-screen bg-background text-foreground/80 overflow-hidden font-sans">
        <Providers>
          <AuthWrapper>
            {/* Ambient Background Grid & Glows for the entire app */}
            <div className="fixed inset-0 w-full h-full overflow-hidden pointer-events-none -z-20 bg-grid-pattern opacity-50" />
            <div className="fixed top-0 right-0 w-full h-full overflow-hidden pointer-events-none -z-10">
              <div className="ambient-light-1 absolute top-[-15%] right-[-5%] w-[600px] h-[600px] rounded-full bg-wa-green/[0.04] blur-[150px]" />
              <div className="ambient-light-2 absolute bottom-[-15%] left-[-5%] w-[500px] h-[500px] rounded-full bg-wa-purple/[0.04] blur-[150px]" />
              <div className="ambient-light-3 absolute top-[40%] left-[30%] w-[400px] h-[400px] rounded-full bg-wa-blue/[0.03] blur-[120px]" />
            </div>

            <Sidebar />
            <main className="flex-1 flex flex-col h-screen overflow-hidden relative p-4 pl-0 lg:pl-2">
              <div className="layout-pane flex-1 flex flex-col w-full h-full relative">
                {children}
              </div>
            </main>
          </AuthWrapper>
        </Providers>
      </body>
    </html>
  );
}
