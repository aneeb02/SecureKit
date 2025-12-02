"use client";

import React from "react";
import Link from "next/link";
import {
  QrCode,
  Image as ImageIcon,
  Fish,
  ArrowRight,
  ShieldCheck,
  Eye,
  AlertTriangle,
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

export default function DashboardPage() {
  const handleNavigation = (moduleName) => {
    console.log(`Navigating to ${moduleName}...`);
  };

  const modules = [
    {
      title: "QR Shield",
      description:
        "Analyze and generate secure QR codes. Protects against malicious redirects.",
      icon: <QrCode className="h-8 w-8 text-emerald-500" />,
      color: "bg-emerald-50/50 hover:bg-emerald-50",
      borderColor: "border-emerald-100",
      route: "/qr_shield",
    },
    {
      title: "PixelVault",
      description:
        "Securely encrypt your images and metadata. Steganography tools included.",
      icon: <ImageIcon className="h-8 w-8 text-indigo-500" />,
      color: "bg-indigo-50/50 hover:bg-indigo-50",
      borderColor: "border-indigo-100",
      route: "/pixel_vault",
    },
    {
      title: "PhishyWishy",
      description:
        "AI-powered phishing detection and email header analysis playground.",
      icon: <Fish className="h-8 w-8 text-rose-500" />,
      color: "bg-rose-50/50 hover:bg-rose-50",
      borderColor: "border-rose-100",
      route: "/phishy_wishy",
    },
  ];

  return (
    <div className="min-h-screen bg-slate-50/50 p-6 md:p-10 font-sans text-slate-900">
      <div className="mx-auto max-w-5xl space-y-8">
        {/* Header Section */}
        <div className="flex flex-col space-y-2">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="h-8 w-8 text-slate-900" />
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">
              SecureKit
            </h1>
          </div>
          <p className="text-slate-500 text-lg">
            Welcome back. Select a security tool to get started.
          </p>
        </div>

        {/* Modules Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {modules.map((module, index) => (
            <Card
              key={index}
              className={cn(
                "transition-all duration-200 hover:shadow-md",
                module.color,
                module.borderColor
              )}
            >
              <CardHeader className="pb-4">
                <div className="mb-2 flex h-14 w-14 items-center justify-center rounded-2xl bg-white shadow-sm ring-1 ring-slate-900/5">
                  {module.icon}
                </div>
                <CardTitle className="text-xl">{module.title}</CardTitle>
              </CardHeader>
              <CardContent className="pb-4">
                <CardDescription className="text-base leading-relaxed text-slate-600">
                  {module.description}
                </CardDescription>
              </CardContent>
              <CardFooter>
                <Link href={module.route} className="w-full">
                  <Button className="w-full justify-between group">
                    Open Tool
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </Button>
                </Link>
              </CardFooter>
            </Card>
          ))}
        </div>

        {/* Quick Stats / Info Row */}
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Recent Scans
              </CardTitle>
              <Eye className="h-4 w-4 text-slate-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">24</div>
              <p className="text-xs text-slate-500">+12% from last month</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Threats Blocked
              </CardTitle>
              <AlertTriangle className="h-4 w-4 text-rose-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-rose-600">3</div>
              <p className="text-xs text-slate-500">
                Phishing attempts neutralized
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
