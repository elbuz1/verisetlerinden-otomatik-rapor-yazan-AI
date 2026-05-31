"use client";

import { useState, useEffect } from "react";
import { reportAPI } from "@/lib/api";
import toast from "react-hot-toast";
import Sidebar from "@/components/layout/Sidebar";
import { FileText, Download, Loader2, Calendar } from "lucide-react";

export default function ReportsPage() {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState<number | null>(null);

  useEffect(() => {
    loadReports();
  }, []);

  async function loadReports() {
    try {
      const res = await reportAPI.list();
      setReports(res.data);
    } catch {
    } finally {
      setLoading(false);
    }
  }

  async function downloadReport(reportId: number, format: string, title: string) {
    setDownloading(reportId);
    try {
      const res = await reportAPI.download(reportId);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${title}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("Rapor indirildi!");
    } catch {
      toast.error("Indirme hatasi");
    } finally {
      setDownloading(null);
    }
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <Sidebar />
      <main className="ml-64 p-8">
        <div className="space-y-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Raporlar</h1>
            <p className="text-gray-400 mt-1">Olusturulan tum raporlari goruntueleyin ve indirin</p>
          </div>

          {loading ? (
            <div className="flex justify-center py-16">
              <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
            </div>
          ) : reports.length === 0 ? (
            <div className="glass-card p-16 text-center">
              <FileText className="w-16 h-16 text-gray-700 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-400">Henuz rapor olusturulmadi</h3>
              <p className="text-gray-500 mt-2">Veri yukleyip analiz ettikten sonra rapor olusturabilirsiniz</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {reports.map((report) => (
                <div key={report.id} className="glass-card-hover p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 bg-purple-600/20 rounded-xl">
                      <FileText className="w-8 h-8 text-purple-400" />
                    </div>
                    <span className="px-2 py-1 rounded-lg bg-primary-500/20 text-primary-400 text-xs font-bold uppercase">
                      {report.format}
                    </span>
                  </div>
                  <h3 className="text-white font-semibold mb-2 line-clamp-2">{report.title}</h3>
                  <div className="flex items-center gap-2 text-gray-500 text-xs mb-4">
                    <Calendar className="w-3 h-3" />
                    {report.created_at ? new Date(report.created_at).toLocaleDateString("tr-TR", {
                      year: "numeric", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit",
                    }) : ""}
                  </div>
                  <button
                    onClick={() => downloadReport(report.id, report.format, report.title)}
                    disabled={downloading === report.id}
                    className="btn-primary w-full flex items-center justify-center gap-2 py-2 text-sm"
                  >
                    {downloading === report.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Download className="w-4 h-4" />
                    )}
                    Indir
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
