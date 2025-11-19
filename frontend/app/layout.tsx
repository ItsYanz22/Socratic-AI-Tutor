import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "./context/AuthContext"; // <-- 1. IMPORT YOUR PROVIDER

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// (I've updated the metadata to match our project)
export const metadata: Metadata = {
  title: "Sahayogi AI Tutor",
  description: "Your AI-powered cognitive gym",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {/* 2. WRAP YOUR CHILDREN WITH THE PROVIDER */}
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}