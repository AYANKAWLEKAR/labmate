import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { SessionProvider } from "./components/SessionProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Labmate - Research Matchmaking Platform",
  description: "Connect with research opportunities at top institutions",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // #region agent log
  if (typeof window !== 'undefined') {
    const linkTags = Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(l => ({href: l.getAttribute('href'), id: l.id}));
    const styleTags = Array.from(document.querySelectorAll('style')).map(s => ({text: s.textContent?.substring(0, 200) || '', id: s.id}));
    fetch('http://127.0.0.1:7242/ingest/4602107a-e1df-493a-b467-d31eb221ce0f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'layout.tsx:18',message:'Layout render - CSS check',data:{linkTags,styleTagsCount:styleTags.length,hasGlobalsCss:linkTags.some(l=>l.href?.includes('globals')),hasTailwind:styleTags.some(s=>s.text.includes('tailwind')||s.text.includes('bg-background'))},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
  }
  // #endregion
  return (
    <html lang="en">
      <body className={inter.className}>
        <SessionProvider>{children}</SessionProvider>
      </body>
    </html>
  );
}

