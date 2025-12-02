"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Menu,
  X,
  Grid as GridIcon,
  QrCode,
  Image as ImageIcon,
  Fish,
  ShieldCheck,
  Settings,
  LogOut,
  User,
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function Sidebar() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  const navItems = [
    { label: "Dashboard", href: "/", icon: GridIcon },
    { label: "QR Shield", href: "/qr_shield", icon: QrCode },
    { label: "PixelVault", href: "/pixel_vault", icon: ImageIcon },
    { label: "PhishyWishy", href: "/phishy_wishy", icon: Fish },
  ];

  const NavLink = ({ item, mobile = false }) => {
    const Icon = item.icon;
    const active = pathname === item.href;

    return (
      <Link
        href={item.href}
        onClick={() => {
          if (mobile) setOpen(false);
        }}
        className={cn(
          "group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
          active
            ? "bg-indigo-50 text-indigo-600 shadow-sm ring-1 ring-indigo-200"
            : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
        )}
      >
        <Icon
          className={cn(
            "h-5 w-5 transition-colors",
            active
              ? "text-indigo-600"
              : "text-slate-400 group-hover:text-slate-600"
          )}
        />
        <span>{item.label}</span>
        {active && (
          <div className="ml-auto h-1.5 w-1.5 rounded-full bg-indigo-600" />
        )}
      </Link>
    );
  };

  return (
    <>
      {/* Mobile Top Bar */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-4 py-3 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="flex items-center space-x-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 text-white">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <span className="font-bold text-slate-900 tracking-tight">
            SecureKit
          </span>
        </div>
        <button
          aria-label={open ? "Close menu" : "Open menu"}
          onClick={() => setOpen((s) => !s)}
          className="inline-flex h-9 w-9 items-center justify-center rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-900 transition-colors"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Desktop Sidebar */}
      <aside className="hidden md:flex md:w-72 md:flex-col md:fixed md:inset-y-0 bg-white border-r border-slate-200 shadow-[4px_0_24px_-12px_rgba(0,0,0,0.1)] z-40">
        {/* Brand */}
        <div className="p-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white shadow-lg shadow-slate-900/20">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">
              SecureKit
            </h2>
            <p className="text-xs text-slate-500 font-medium">
              Security Suite v1.0
            </p>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex-1 px-4 py-4 space-y-6 overflow-y-auto">
          <div>
            <h3 className="mb-2 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Tools
            </h3>
            <nav className="space-y-1">
              {navItems.map((item) => (
                <NavLink key={item.href} item={item} />
              ))}
            </nav>
          </div>

          <div>
            <h3 className="mb-2 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">
              System
            </h3>
            <nav className="space-y-1">
              <button className="w-full group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-all">
                <Settings className="h-5 w-5 text-slate-400 group-hover:text-slate-600" />
                <span>Settings</span>
              </button>
            </nav>
          </div>
        </div>

        {/* User Profile Footer */}
        <div className="p-4 border-t border-slate-100">
          <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-3 border border-slate-100 hover:border-slate-200 transition-colors cursor-pointer group">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-100 text-indigo-600 border border-indigo-200">
              <User className="h-5 w-5" />
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-sm font-medium text-slate-900">
                Admin User
              </p>
              <p className="truncate text-xs text-slate-500">
                admin@securekit.dev
              </p>
            </div>
            <LogOut className="h-4 w-4 text-slate-400 group-hover:text-red-500 transition-colors" />
          </div>
        </div>
      </aside>

      {/* Mobile Overlay & Drawer */}
      {open && (
        <div className="md:hidden fixed inset-0 z-50 pt-[64px]">
          <div
            className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm transition-opacity"
            onClick={() => setOpen(false)}
          />
          <div className="absolute left-0 top-[64px] bottom-0 w-[80%] max-w-xs bg-white shadow-2xl p-6 overflow-y-auto">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 text-white">
                  <ShieldCheck className="h-5 w-5" />
                </div>
                <span className="font-bold text-lg text-slate-900">
                  SecureKit
                </span>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="rounded-md p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-500"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <nav className="space-y-1">
              {navItems.map((item) => (
                <NavLink key={item.href} item={item} mobile />
              ))}
            </nav>

            <div className="mt-8">
              <button className="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50">
                <LogOut className="h-4 w-4" />
                Sign out
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
