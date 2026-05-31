"use client";

import { useState, useEffect } from "react";
import { dashboardAPI } from "@/lib/api";
import {
  Database, FileText, BarChart3, HardDrive,
  TrendingUp, Award, Clock, Activity,
} from "lucide-react";

interface Stats {
  total_datasets: number;
  total_reports: number;
  total_rows_analyzed: number;
  total_data_size_mb: number;
  total_analyzed: number;
  average_quality_score: number;
}

interface RecentDataset {
  id: number;
  filename: string;
  file_type: string;
  row_count: number;
  column_count: number;
  status: string;
  created_at: string;
}

interface RecentReport {
  id: number;
  title: string;
  format: string;
  status: string;
  created_at: string;
  download_url: string;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentDatasets, setRecentDatasets] = useState<RecentDataset[]>([]);
  const [recentReports, setRecentReports] = useState<RecentReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      const [statsRes, dsRes, rpRes] = await Promise.allSettled([
        dashboardAPI.stats(),
        dashboardAPI.recentDatasets(),
        dashboardAPI.recentReports(),
      ]);
      if (statsRes.status === "fulfilled") setStats(statsRes.value.data);
      if (dsRes.status === "fulfilled") setRecentDatasets(dsRes.value.data);
      if (rpRes.status === "fulfilled") setRecentReports(rpRes.value.data);
    } catch {
    } finally {
      setLoading(false);
    }
  }

  const statCards = stats
    ? [
        { label: "Toplam Veri Seti", value: stats.total_datasets, icon: Database, color: "from-blue-500 to-cyan-500" },
        { label: "Toplam Rapor", value: stats.total_reports, icon: FileText, color: "from-purple-500 to-pink-500" },
        { label: "Analiz Edilen Satir", value: stats.total_rows_analyzed.toLocaleString(), icon: BarChart3, color: "from-emerald-500 to-teal-500" },
        { label: "Veri Boyutu (MB)", value: stats.total_data_size_mb, icon: HardDrive, color: "from-orange-500 to-amber-500" },
        { label: "Tamamlanan Analiz", value: stats.total_analyzed, icon: TrendingUp, color: "from-rose-500 to-red-500" },
        { label: "Ort. Kalite Skoru", value: stats.average_quality_score, icon: Award, color: "from-indigo-500 to-violet-500" },
      ]
    : [];

  const statusBadge = (status: string) => {
    const colors: Record<string, string> = {
      uploaded: "bg-blue-500/20 text-blue-400",
      analyzed: "bg-emerald-500/20 text-emerald-400",
      error: "bg-red-500/20 text-red-400",
      completed: "bg-emerald-500/20 text-emerald-400",
      pending: "bg-yellow-500/20 text-yellow-400",
    };
    return colors[status] || "bg-gray-500/20 text-gray-400";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-400 mt-1">Sistem durumu ve son aktiviteler</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div key={i} className="stat-card group">
              <div className={`absolute inset-0 bg-gradient-to-br ${card.color} opacity-0 group-hover:opacity-5 transition-opacity rounded-2xl`} />
              <div className="relative z-10 flex items-start justify-between">
                <div>
                  <p className="text-gray-400 text-sm">{card.label}</p>
                  <p className="text-3xl font-bold text-white mt-2">{card.value}</p>
                </div>
                <div className={`p-3 rounded-xl bg-gradient-to-br ${card.color} bg-opacity-20`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Datasets */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Database className="w-5 h-5 text-primary-400" />
              Son Veri Setleri
            </h2>
          </div>
          <div className="space-y-3">
            {recentDatasets.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Henuz veri seti yuklenmedi</p>
            ) : (
              recentDatasets.map((ds) => (
                <div key={ds.id} className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary-600/20 flex items-center justify-center">
                      <span className="text-xs font-bold text-primary-400 uppercase">{ds.file_type}</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{ds.filename}</p>
                      <p className="text-xs text-gray-500">{ds.row_count?.toLocaleString()} satir, {ds.column_count} sutun</p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-lg text-xs font-medium ${statusBadge(ds.status)}`}>
                    {ds.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Reports */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <FileText className="w-5 h-5 text-purple-400" />
              Son Raporlar
            </h2>
          </div>
          <div className="space-y-3">
            {recentReports.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Henuz rapor olusturulmadi</p>
            ) : (
              recentReports.map((rp) => (
                <div key={rp.id} className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-purple-600/20 flex items-center justify-center">
                      <span className="text-xs font-bold text-purple-400 uppercase">{rp.format}</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{rp.title}</p>
                      <p className="text-xs text-gray-500">
                        {rp.created_at ? new Date(rp.created_at).toLocaleDateString("tr-TR") : ""}
                      </p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-lg text-xs font-medium ${statusBadge(rp.status)}`}>
                    {rp.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
