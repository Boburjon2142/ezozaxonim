import "./globals.css";
import { ReactNode } from "react";
import { QueryProvider } from "@/components/layout/query-provider";
import { AppToaster } from "@/components/ui/toaster";

export const metadata = {
  title: "LifePause",
  description: "Anti-burnout personal rhythm system",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <QueryProvider>
          {children}
          <AppToaster />
        </QueryProvider>
      </body>
    </html>
  );
}
