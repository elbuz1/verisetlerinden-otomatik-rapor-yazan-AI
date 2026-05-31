"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { uploadAPI, analysisAPI, reportAPI } from "@/lib/api";
import toast from "react-hot-toast";
import {
  Upload, FileSpreadsheet, CheckCircle2, Loader2,
  BarChart3, FileText, Download, Brain, Sparkles,
} from "lucide-react";
import Sidebar from "@/components/layout/Sidebar";

interface UploadResult {
  id: number;
  filename: string;
  file_type: string;
  file_size_readable: string;
  row_count: number;
  column_count: number;
  columns_info: any[];
  preview: any;
}

interface AnalysisResult {
  analysis: any;
  ai_comments: any;
  duration_ms: number;
}

type Step = "upload" | "preview" | "analyzing" | "results" | "report";

export default function UploadPage() {
  const [step, setStep] = useState<Step>("upload");
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [workflowSteps, setWorkflowSteps] = useState<any[]>([]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    const ext = file.name.split(".").pop()?.toLowerCase();
    if (!["csv", "xlsx", "xls", "json"].includes(ext || "")) {
      toast.error("Desteklenmeyen dosya tipi. CSV, Excel veya JSON yukleyin.");
      return;
    }

    setUploading(true);
    try {
      const res = await uploadAPI.upload(file);
      setUploadResult(res.data);
      setStep("preview");
      toast.success("Dosya basariyla yuklendi!");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Yukleme hatasi");
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "application/vnd.ms-excel": [".xls"],
      "application/json": [".json"],
    },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024,
  });

  const runAnalysis = async () => {
    if (!uploadResult) return;
    setAnalyzing(true);
    setStep("analyzing");

    const steps = [
      { name: "Dosya Dogrulama", status: "pending" },
      { name: "Veri Ayristirma", status: "pending" },
      { name: "Istatistiksel Analiz", status: "pending" },
      { name: "Trend Tespiti", status: "pending" },
      { name: "Anomali Algilama", status: "pending" },
      { name: "AI Yorum Uretimi", status: "pending" },
      { name: "Grafik Olusturma", status: "pending" },
      { name: "Veritabani Kayit", status: "pending" },
    ];
    setWorkflowSteps(steps);

    for (let i = 0; i < steps.length; i++) {
      await new Promise((r) => setTimeout(r, 400 + Math.random() * 600));
      setWorkflowSteps((prev) =>
        prev.map((s, idx) => ({
          ...s,
          status: idx < i ? "completed" : idx === i ? "running" : "pending",
        }))
      );
    }

    try {
      const res = await analysisAPI.run(uploadResult.id);
      setAnalysisResult(res.data);
      setWorkflowSteps((prev) => prev.map((s) => ({ ...s, status: "completed" })));
      setStep("results");
      toast.success("Analiz tamamlandi!");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Analiz hatasi");
      setStep("preview");
    } finally {
      setAnalyzing(false);
    }
  };

  const generateReport = async (format: "pdf" | "docx") => {
    if (!uploadResult) return;
    setGenerating(true);
    try {
      const res = await reportAPI.generate(uploadResult.id, format);
      toast.success(`${format.toUpperCase()} rapor olusturuldu!`);

      const downloadRes = await reportAPI.download(res.data.report_id);
      const url = window.URL.createObjectURL(new Blob([downloadRes.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `rapor.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Rapor olusturma hatasi");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950">
      <Sidebar />
      <main className="ml-64 p-8">
        <div className="max-w-5xl mx-auto space-y-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Veri Yukle & Analiz Et</h1>
            <p className="text-gray-400 mt-1">CSV, Excel veya JSON dosyanizi yukleyin</p>
          </div>

          {/* Progress Steps */}
          <div className="flex items-center gap-4">
            {["Yukle", "Onizle", "Analiz", "Sonuclar"].map((label, i) => {
              const stepMap: Step[] = ["upload", "preview", "analyzing", "results"];
              const currentIdx = stepMap.indexOf(step);
              const isCompleted = i < currentIdx;
              const isCurrent = i === currentIdx;
              return (
                <div key={label} className="flex items-center gap-2 flex-1">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                      isCompleted
                        ? "bg-emerald-500 text-white"
                        : isCurrent
                        ? "bg-primary-600 text-white ring-4 ring-primary-600/30"
                        : "bg-white/10 text-gray-500"
                    }`}
                  >
                    {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : i + 1}
                  </div>
                  <span className={`text-sm ${isCurrent ? "text-white font-medium" : "text-gray-500"}`}>{label}</span>
                  {i < 3 && <div className={`flex-1 h-0.5 ${isCompleted ? "bg-emerald-500" : "bg-white/10"}`} />}
                </div>
              );
            })}
          </div>

          {/* Upload Zone */}
          {step === "upload" && (
            <div
              {...getRootProps()}
              className={`glass-card p-16 text-center cursor-pointer transition-all duration-300 ${
                isDragActive ? "border-primary-500 bg-primary-500/10 scale-[1.02]" : "hover:border-white/20"
              }`}
            >
              <input {...getInputProps()} />
              {uploading ? (
                <div className="flex flex-col items-center gap-4">
                  <Loader2 className="w-16 h-16 text-primary-400 animate-spin" />
                  <p className="text-white text-lg">Dosya yukleniyor...</p>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-4">
                  <div className="p-6 bg-primary-600/10 rounded-2xl">
                    <Upload className="w-16 h-16 text-primary-400" />
                  </div>
                  <div>
                    <p className="text-white text-lg font-medium">
                      {isDragActive ? "Dosyayi birakin..." : "Dosya surukleyin veya tiklayin"}
                    </p>
                    <p className="text-gray-500 mt-1">CSV, Excel (.xlsx) veya JSON - Maks 100MB</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Preview */}
          {step === "preview" && uploadResult && (
            <div className="space-y-6">
              <div className="glass-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <FileSpreadsheet className="w-8 h-8 text-primary-400" />
                    <div>
                      <h3 className="text-lg font-semibold text-white">{uploadResult.filename}</h3>
                      <p className="text-gray-400 text-sm">
                        {uploadResult.row_count.toLocaleString()} satir, {uploadResult.column_count} sutun - {uploadResult.file_size_readable}
                      </p>
                    </div>
                  </div>
                  <span className="px-3 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 text-sm font-medium uppercase">
                    {uploadResult.file_type}
                  </span>
                </div>

                {/* Column Info */}
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-400 mb-3">Sutun Bilgileri</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {uploadResult.columns_info?.slice(0, 10).map((col: any, i: number) => (
                      <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-white/5">
                        <span className="text-sm text-white">{col.name}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-500">{col.dtype}</span>
                          {col.null_count > 0 && (
                            <span className="text-xs text-yellow-400">%{col.null_percentage} bos</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Data Preview Table */}
                {uploadResult.preview && (
                  <div className="mt-6 overflow-x-auto">
                    <h4 className="text-sm font-medium text-gray-400 mb-3">Veri Onizleme (ilk 20 satir)</h4>
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-white/10">
                          {uploadResult.preview.columns?.slice(0, 8).map((col: string) => (
                            <th key={col} className="text-left py-2 px-3 text-gray-400 font-medium">{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {uploadResult.preview.data?.slice(0, 10).map((row: any, i: number) => (
                          <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                            {uploadResult.preview.columns?.slice(0, 8).map((col: string) => (
                              <td key={col} className="py-2 px-3 text-gray-300">{String(row[col] ?? "").slice(0, 30)}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              <div className="flex gap-4">
                <button onClick={() => setStep("upload")} className="btn-secondary">
                  Farkli Dosya Yukle
                </button>
                <button onClick={runAnalysis} className="btn-primary flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  AI Analiz Baslat
                </button>
              </div>
            </div>
          )}

          {/* Analyzing - Workflow Animation */}
          {step === "analyzing" && (
            <div className="glass-card p-8">
              <div className="flex items-center gap-3 mb-8">
                <div className="p-3 bg-primary-600/20 rounded-xl">
                  <Sparkles className="w-8 h-8 text-primary-400 animate-pulse" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">AI Analiz Calisiyor</h3>
                  <p className="text-gray-400">Veri setiniz analiz ediliyor...</p>
                </div>
              </div>

              <div className="space-y-3">
                {workflowSteps.map((s, i) => (
                  <div key={i} className="flex items-center gap-4 p-3 rounded-xl bg-white/5">
                    <div className="w-8 h-8 flex items-center justify-center">
                      {s.status === "completed" ? (
                        <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                      ) : s.status === "running" ? (
                        <Loader2 className="w-6 h-6 text-primary-400 animate-spin" />
                      ) : (
                        <div className="w-3 h-3 rounded-full bg-gray-600" />
                      )}
                    </div>
                    <span className={`text-sm ${s.status === "running" ? "text-white font-medium" : s.status === "completed" ? "text-gray-300" : "text-gray-500"}`}>
                      {s.name}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Results */}
          {step === "results" && analysisResult && (
            <div className="space-y-6">
              {/* Executive Summary */}
              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
                  <Brain className="w-5 h-5 text-primary-400" />
                  AI Yonetici Ozeti
                </h3>
                <div className="prose prose-invert max-w-none">
                  {analysisResult.ai_comments?.executive_summary?.split("\n\n").map((p: string, i: number) => (
                    <p key={i} className="text-gray-300 leading-relaxed mb-3">{p}</p>
                  ))}
                </div>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                  { label: "Toplam Satir", value: analysisResult.analysis?.basic_stats?.total_rows?.toLocaleString() },
                  { label: "Toplam Sutun", value: analysisResult.analysis?.basic_stats?.total_columns },
                  { label: "Kalite Skoru", value: `${analysisResult.analysis?.data_quality_score?.overall || 0}/100` },
                  { label: "Analiz Suresi", value: `${(analysisResult.duration_ms / 1000).toFixed(1)}s` },
                ].map((item, i) => (
                  <div key={i} className="glass-card p-4 text-center">
                    <p className="text-gray-400 text-xs">{item.label}</p>
                    <p className="text-2xl font-bold text-white mt-1">{item.value}</p>
                  </div>
                ))}
              </div>

              {/* AI Comments */}
              {analysisResult.ai_comments?.trend_comments?.length > 0 && (
                <div className="glass-card p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Trend Analizi</h3>
                  <div className="space-y-3">
                    {analysisResult.ai_comments.trend_comments.map((tc: any, i: number) => (
                      <div key={i} className="p-3 rounded-xl bg-white/5">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`w-2 h-2 rounded-full ${tc.direction === "yukari" ? "bg-emerald-400" : tc.direction === "asagi" ? "bg-red-400" : "bg-gray-400"}`} />
                          <span className="text-sm font-medium text-white">{tc.column}</span>
                        </div>
                        <p className="text-sm text-gray-300">{tc.comment}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {analysisResult.ai_comments?.recommendations?.length > 0 && (
                <div className="glass-card p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">AI Onerileri</h3>
                  <div className="space-y-3">
                    {analysisResult.ai_comments.recommendations.map((rec: any, i: number) => (
                      <div key={i} className="p-3 rounded-xl bg-white/5 flex gap-3">
                        <span className="text-primary-400 font-bold text-sm mt-0.5">{rec.priority}.</span>
                        <div>
                          <span className="text-xs font-medium text-primary-400 bg-primary-500/10 px-2 py-0.5 rounded-full">
                            {rec.category}
                          </span>
                          <p className="text-sm text-gray-300 mt-1">{rec.recommendation}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Report Generation */}
              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-purple-400" />
                  Rapor Olustur
                </h3>
                <p className="text-gray-400 text-sm mb-4">
                  Analiz sonuclarinizi profesyonel rapor olarak indirin
                </p>
                <div className="flex gap-4">
                  <button
                    onClick={() => generateReport("pdf")}
                    disabled={generating}
                    className="btn-primary flex items-center gap-2"
                  >
                    {generating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Download className="w-5 h-5" />}
                    PDF Rapor Indir
                  </button>
                  <button
                    onClick={() => generateReport("docx")}
                    disabled={generating}
                    className="btn-secondary flex items-center gap-2"
                  >
                    {generating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Download className="w-5 h-5" />}
                    DOCX Rapor Indir
                  </button>
                </div>
              </div>

              <button onClick={() => { setStep("upload"); setUploadResult(null); setAnalysisResult(null); }} className="btn-secondary">
                Yeni Analiz Baslat
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
