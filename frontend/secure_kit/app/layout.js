import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "SecureKit",
  description: "SecureKit dashboard and tools",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-slate-50 overflow-x-hidden`}
      >
        <Sidebar />
        {/* Main content area - accounts for sidebar on desktop and top bar on mobile */}
        <div className="w-full md:pl-72">
          <div className="pt-[64px] md:pt-0 w-full">
            <main className="min-h-screen w-full">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
