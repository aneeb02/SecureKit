"use client";

import React from "react";
import Link from "next/link";
import {
  QrCode,
  Image as ImageIcon,
  Fish,
  ArrowRight,
  ShieldCheck,
  Lock, 
  Eye,
  Activity, 
  AlertTriangle,
  CheckCircle2
} from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

export default function HomePage() {
  const modules = [
    {
      title: "QR Shield",
      description:
        "Scan and validate QR codes to prevent malicious redirects and phishing attacks.",
      icon: <QrCode className="h-6 w-6 text-emerald-600" />,
      bgClass: "bg-emerald-50",
      iconBg: "bg-emerald-100",
      route: "/qr_shield",
    },
    {
      title: "PixelVault",
      description:
        "Securely encrypt images and analyze metadata with advanced steganography tools.",
      icon: <ImageIcon className="h-6 w-6 text-indigo-600" />,
      bgClass: "bg-indigo-50",
      iconBg: "bg-indigo-100",
      route: "/pixel_vault",
    },
    {
      title: "PhishyWishy",
      description:
        "AI-powered analysis for detecting phishing patterns in emails and URLs.",
      icon: <Fish className="h-6 w-6 text-rose-600" />,
      bgClass: "bg-rose-50",
      iconBg: "bg-rose-100",
      route: "/phishy_wishy",
    },
  ];

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 selection:bg-indigo-100 p-6 md:p-10">
      <div className="mx-auto max-w-6xl space-y-8">
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white shadow-lg">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">SecureKit</h1>
              <p className="text-sm text-slate-500">
                Select a tool to get started
              </p>
            </div>
          </div>
        </header>

        <section>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {modules.map((m) => (
              <Card
                key={m.title}
                className={cn(
                  "group relative overflow-hidden border-slate-200 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg"
                )}
              >
                <div
                  className={cn(
                    "absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100",
                    m.bgClass
                  )}
                />
                <CardHeader className="relative pb-4">
                  <div
                    className={cn(
                      "mb-4 w-fit rounded-xl p-3 shadow-sm transition-transform duration-300 group-hover:scale-110",
                      m.iconBg
                    )}
                  >
                    {m.icon}
                  </div>
                  <CardTitle className="text-lg">{m.title}</CardTitle>
                </CardHeader>
                <CardContent className="relative pb-8">
                  <CardDescription>{m.description}</CardDescription>
                </CardContent>
                <CardFooter className="relative mt-auto">
                  <Link href={m.route} className="w-full">
                    <Button className="w-full justify-between group/btn bg-white text-slate-700 border border-slate-200 hover:bg-white hover:border-slate-300 hover:text-slate-900 shadow-sm">
                      Open Tool
                      <ArrowRight className="h-4 w-4 text-slate-400 transition-transform group-hover/btn:translate-x-1 group-hover/btn:text-slate-600" />
                    </Button>
                  </Link>
                </CardFooter>
              </Card>
            ))}
          </div>
        </section>
        {/* Quick Stats / Info Row */}
        <div className="grid gap-6 md:grid-cols-3">
          <Card className="bg-gradient-to-br from-slate-900 to-slate-800 text-white border-none shadow-xl">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <Activity className="h-4 w-4" /> Protection Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Active</div>
              <p className="text-xs text-slate-400 mt-1">
                Real-time monitoring enabled
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white/60">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">Recent Scans</CardTitle>
              <div className="rounded-full bg-slate-100 p-1.5">
                <Eye className="h-4 w-4 text-slate-500" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline space-x-2">
                <div className="text-2xl font-bold text-slate-900">24</div>
                <span className="text-xs font-medium text-emerald-600 flex items-center">
                  +12% <span className="text-slate-400 ml-1 font-normal">vs last month</span>
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/60">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">Threats Blocked</CardTitle>
              <div className="rounded-full bg-rose-50 p-1.5">
                <AlertTriangle className="h-4 w-4 text-rose-500" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline space-x-2">
                <div className="text-2xl font-bold text-slate-900">3</div>
                <span className="text-xs text-slate-500">
                  Phishing attempts neutralized
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
