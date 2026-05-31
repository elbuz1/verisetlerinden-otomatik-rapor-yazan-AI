"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAppStore } from "@/lib/store";
import Sidebar from "@/components/layout/Sidebar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, initAuth } = useAppStore();
  const router = useRouter();
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    initAuth();
    setAuthChecked(true);
  }, [initAuth]);

  useEffect(() => {
    if (!authChecked) return; // initAuth bitmeden redirect yapma
    if (!isAuthenticated) {
      const token = localStorage.getItem("token");
      if (!token) router.push("/");
    }
  }, [isAuthenticated, authChecked, router]);

  // Auth kontrolü tamamlanana kadar loading göster
  if (!authChecked) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <Sidebar />
      <main className="ml-64 p-8">{children}</main>
    </div>
  );
}
