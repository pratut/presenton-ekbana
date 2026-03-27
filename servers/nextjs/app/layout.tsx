import type { Metadata } from "next";
import localFont from "next/font/local";
import { Syne, Unbounded } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import MixpanelInitializer from "./MixpanelInitializer";
import { Toaster } from "@/components/ui/sonner";
import { RouteGuard } from "@/components/auth/RouteGuard";
const inter = localFont({
  src: [
    {
      path: "./fonts/Inter.ttf",
      weight: "400",
      style: "normal",
    },
  ],
  variable: "--font-inter",
});

const syne = Syne({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-syne",
});

const unbounded = Unbounded({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-unbounded",
});


export const metadata: Metadata = {
  metadataBase: new URL("https://ekbana.com"),
  title: "EKbana-AI presentation",
  description:
    "AI-powered presentation generator with custom layouts, multi-model support, and professional design. Create stunning presentations in minutes.",
  keywords: [
    "AI presentation generator",
    "data storytelling",
    "data visualization tool",
    "AI data presentation",
    "presentation generator",
    "data to presentation",
    "interactive presentations",
    "professional slides",
  ],
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-icon.png',
  },
  openGraph: {
    title: "EKbana-AI presentation",
    description:
      "AI-powered presentation generator with custom layouts, multi-model support, and professional design. Create stunning presentations in minutes.",
    url: "https://ekbana.com",
    siteName: "EKbana",
    images: [
      {
        url: "https://ekbana.com/presenton-feature-graphics.png",
        width: 1200,
        height: 630,
        alt: "EKbana Logo",
      },
    ],
    type: "website",
    locale: "en_US",
  },
  alternates: {
    canonical: "https://ekbana.com",
  },
  twitter: {
    card: "summary_large_image",
    title: "EKbana-AI presentation",
    description:
      "AI-powered presentation generator with custom layouts, multi-model support, and professional design. Create stunning presentations in minutes.",
    images: ["https://ekbana.com/presenton-feature-graphics.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {

  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${unbounded.variable} ${syne.variable} antialiased`}
      >
        <Providers>
          <MixpanelInitializer>
            <RouteGuard>
              {children}
            </RouteGuard>

          </MixpanelInitializer>
        </Providers>
        <Toaster position="top-center" />
      </body>
    </html>
  );
}
