"use client";

import { useState, useEffect } from "react";
import { uploadAPI, analysisAPI } from "@/lib/api";
import toast from "react-hot-toast";
import Sidebar from "@/components/layout/Sidebar";
import { BarChart3, Brain, Loader2, Database, TrendingUp, AlertTriangle } from "lucide-react";

export default function AnalysisPage() {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState<number | null>(null);

  useEffect(() => {
    loadDatasets();
  }, []);

  async function loadDatasets() {
    try {
      const res = await uploadAPI.list();
      setDatasets(res.data);
    } catch {
    } finally {
      setLoading(false);
    }
  }

  async function viewAnalysis(datasetId: number) {
    try {
      const res = await analysisAPI.get(datasetId);
      setSelectedAnalysis(res.data);
    } catch {
      toast.error("Analiz bulunamadi. Once analiz calistirin.");
    }
  }

  async function runAnalysis(datasetId: number) {
    setAnalyzing(datasetId);
    try {
      const res = await analysisAPI.run(datasetId);
      setSelectedAnalysis(res.data);
      toast.success("Analiz tamamlandi!");
      loadDatasets();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Analiz hatasi");
    } finally {
      setAnalyzing(null);
    }
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <Sidebar />
      <main className="ml-64 p-8">
        <div className="space-y-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Analizler</h1>
            <p className="text-gray-400 mt-1">Veri setlerinizin analiz sonuclarini goruntueleyin</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Dataset List */}
            <div className="glass-card p-6">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Database className="w-5 h-5 text-primary-400" />
                Veri Setleri
              </h2>
              <div className="space-y-2">
                {loading ? (
                  <div className="flex justify-center py-8">
                    <Loader2 className="w-6 h-6 text-primary-400 animate-spin" />
                  </div>
                ) : datasets.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">Veri seti bulunamadi</p>
                ) : (
                  datasets.map((ds) => (
                    <div key={ds.id} className="p-3 rounded-xl bg-white/5 hover:bg-white/10 transition cursor-pointer">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-white truncate">{ds.filename}</span>
                        <span className="text-xs text-gray-500 uppercase">{ds.file_type}</span>
                      </div>
                      <p className="text-xs text-gray-500 mb-2">{ds.row_count?.toLocaleString()} satir</p>
                      <div className="flex gap-2">
                        {ds.status === "analyzed" ? (
                          <button onClick={() => viewAnalysis(ds.id)} className="text-xs bg-primary-600/20 text-primary-400 px-3 py-1 rounded-lg hover:bg-primary-600/30 transition">
                            Sonuclari Gor
                          </button>
                        ) : (
                          <button
                            onClick={() => runAnalysis(ds.id)}
                            disabled={analyzing === ds.id}
                            className="text-xs bg-emerald-600/20 text-emerald-400 px-3 py-1 rounded-lg hover:bg-emerald-600/30 transition flex items-center gap-1"
                          >
                            {analyzing === ds.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <Brain className="w-3 h-3" />}
                            Analiz Et
                          </button>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Analysis Results */}
            <div className="lg:col-span-2 space-y-6">
              {!selectedAnalysis ? (
                <div className="glass-card p-12 text-center">
                  <BarChart3 className="w-16 h-16 text-gray-700 mx-auto mb-4" />
                  <p className="text-gray-500">Analiz sonuclarini gormek icin soldaki listeden bir veri seti secin</p>
                </div>
              ) : (
                <>
                  {/* Executive Summary */}
                  <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
                      <Brain className="w-5 h-5 text-primary-400" />
                      Yonetici Ozeti
                    </h3>
                    {selectedAnalysis.ai_comments?.executive_summary?.split("\n\n").map((p: string, i: number) => (
                      <p key={i} className="text-gray-300 text-sm leading-relaxed mb-2">{p}</p>
                    )) || (
                      <p className="text-gray-300 text-sm">{selectedAnalysis.executive_summary}</p>
                    )}
                  </div>

                  {/* Stats */}
                  {selectedAnalysis.analysis?.basic_stats?.columns && (
                    <div className="glass-card p-6">
                      <h3 className="text-lg font-semibold text-white mb-4">Istatistikler</h3>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-white/10">
                              <th className="text-left py-2 px-3 text-gray-400">Sutun</th>
                              <th className="text-right py-2 px-3 text-gray-400">Ortalama</th>
                              <th className="text-right py-2 px-3 text-gray-400">Medyan</th>
                              <th className="text-right py-2 px-3 text-gray-400">Std Sapma</th>
                              <th className="text-right py-2 px-3 text-gray-400">Min</th>
                              <th className="text-right py-2 px-3 text-gray-400">Max</th>
                            </tr>
                          </thead>
                          <tbody>
                            {Object.entries(selectedAnalysis.analysis.basic_stats.columns).slice(0, 10).map(([col, stats]: [string, any]) => (
                              <tr key={col} className="border-b border-white/5 hover:bg-white/5">
                                <td className="py-2 px-3 text-white font-medium">{col}</td>
                                <td className="py-2 px-3 text-right text-gray-300">{stats.mean?.toFixed(2)}</td>
                                <td className="py-2 px-3 text-right text-gray-300">{stats.median?.toFixed(2)}</td>
                                <td className="py-2 px-3 text-right text-gray-300">{stats.std?.toFixed(2)}</td>
                                <td className="py-2 px-3 text-right text-gray-300">{stats.min?.toFixed(2)}</td>
                                <td className="py-2 px-3 text-right text-gray-300">{stats.max?.toFixed(2)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Trends */}
                  {selectedAnalysis.ai_comments?.trend_comments?.length > 0 && (
                    <div className="glass-card p-6">
                      <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
                        <TrendingUp className="w-5 h-5 text-emerald-400" />
                        Trend Yorumlari
                      </h3>
                      {selectedAnalysis.ai_comments.trend_comments.map((tc: any, i: number) => (
                        <div key={i} className="p-3 rounded-xl bg-white/5 mb-2">
                          <p className="text-sm text-gray-300">{tc.comment}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Anomalies */}
                  {selectedAnalysis.ai_comments?.anomaly_comments?.length > 0 && (
                    <div className="glass-card p-6">
                      <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
                        <AlertTriangle className="w-5 h-5 text-amber-400" />
                        Anomali Tespitleri
                      </h3>
                      {selectedAnalysis.ai_comments.anomaly_comments.map((ac: any, i: number) => (
                        <div key={i} className="p-3 rounded-xl bg-white/5 mb-2 border-l-2 border-amber-500/50">
                          <p className="text-sm text-gray-300">{ac.comment}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
