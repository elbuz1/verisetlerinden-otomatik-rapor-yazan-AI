"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAppStore } from "@/lib/store";
import {
  LayoutDashboard, Upload, BarChart3, FileText,
  Settings, LogOut, Brain, Activity,
} from "lucide-react";
import clsx from "clsx";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/upload", label: "Veri Yukle", icon: Upload },
  { href: "/analysis", label: "Analizler", icon: BarChart3 },
  { href: "/reports", label: "Raporlar", icon: FileText },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAppStore();

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-gray-950/80 backdrop-blur-xl border-r border-white/5 flex flex-col z-50">
      <div className="p-6 border-b border-white/5">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="p-2 bg-primary-600/20 rounded-xl">
            <Brain className="w-6 h-6 text-primary-400" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">AI Rapor</h1>
            <p className="text-xs text-gray-500">Otomatik Analiz</p>
          </div>
        </Link>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-primary-600/20 text-primary-400 border border-primary-500/20"
                  : "text-gray-400 hover:bg-white/5 hover:text-white"
              )}
            >
              <Icon className="w-5 h-5" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-white/5">
        <div className="flex items-center gap-3 px-4 py-3 mb-2">
          <div className="w-8 h-8 bg-primary-600/30 rounded-full flex items-center justify-center">
            <span className="text-sm font-bold text-primary-400">
              {user?.username?.charAt(0).toUpperCase() || "U"}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">{user?.username}</p>
            <p className="text-xs text-gray-500 truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-gray-400 hover:bg-red-500/10 hover:text-red-400 w-full transition-all"
        >
          <LogOut className="w-5 h-5" />
          Cikis Yap
        </button>
      </div>
    </aside>
  );
}
