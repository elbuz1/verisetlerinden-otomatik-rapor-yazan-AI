"use client";

import { useState, useEffect } from "react";
import { useAppStore } from "@/lib/store";
import { authAPI } from "@/lib/api";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { Brain, BarChart3, FileText, Sparkles } from "lucide-react";

export default function HomePage() {
  const { isAuthenticated, setAuth, initAuth } = useAppStore();
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    username: "",
    password: "",
    email: "",
    full_name: "",
  });

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  useEffect(() => {
    if (isAuthenticated) router.push("/dashboard");
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (isLogin) {
        const res = await authAPI.login({
          username: form.username,
          password: form.password,
        });
        setAuth(res.data.user, res.data.access_token);
        toast.success("Giris basarili!");
      } else {
        const res = await authAPI.register(form);
        setAuth(res.data.user, res.data.access_token);
        toast.success("Kayit basarili!");
      }
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Bir hata olustu");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-950 via-primary-900 to-purple-900 p-12 flex-col justify-between relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 w-72 h-72 bg-primary-400 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-400 rounded-full blur-3xl" />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <Brain className="w-10 h-10 text-primary-400" />
            <h1 className="text-3xl font-bold text-white">AI Rapor Sistemi</h1>
          </div>
          <p className="text-primary-200 text-lg">
            Veri setlerinden otomatik akilli rapor uretimi
          </p>
        </div>

        <div className="relative z-10 space-y-8">
          <Feature
            icon={<BarChart3 className="w-6 h-6" />}
            title="Otomatik Analiz"
            desc="Istatistik, trend ve anomali tespiti tek tikla"
          />
          <Feature
            icon={<Sparkles className="w-6 h-6" />}
            title="AI Yorumlari"
            desc="Veriye ozel dinamik yorum ve oneri uretimi"
          />
          <Feature
            icon={<FileText className="w-6 h-6" />}
            title="Profesyonel Raporlar"
            desc="PDF ve DOCX formatinda detayli raporlar"
          />
        </div>

        <p className="relative z-10 text-primary-300 text-sm">
          Harici AI API kullanmadan, tamamen local analiz
        </p>
      </div>

      {/* Right Side - Auth Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
            <Brain className="w-8 h-8 text-primary-400" />
            <h1 className="text-2xl font-bold gradient-text">AI Rapor Sistemi</h1>
          </div>

          <div className="glass-card p-8">
            <h2 className="text-2xl font-bold text-white mb-2">
              {isLogin ? "Giris Yap" : "Kayit Ol"}
            </h2>
            <p className="text-gray-400 mb-6">
              {isLogin ? "Hesabiniza giris yapin" : "Yeni hesap olusturun"}
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <>
                  <input
                    type="text"
                    placeholder="Ad Soyad"
                    className="input-field w-full"
                    value={form.full_name}
                    onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                  />
                  <input
                    type="email"
                    placeholder="E-posta"
                    className="input-field w-full"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    required
                  />
                </>
              )}
              <input
                type="text"
                placeholder="Kullanici Adi"
                className="input-field w-full"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                required
              />
              <input
                type="password"
                placeholder="Sifre"
                className="input-field w-full"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
              />

              <button type="submit" className="btn-primary w-full" disabled={loading}>
                {loading ? "Yukleniyor..." : isLogin ? "Giris Yap" : "Kayit Ol"}
              </button>
            </form>

            <div className="mt-6 text-center">
              <button
                onClick={() => setIsLogin(!isLogin)}
                className="text-primary-400 hover:text-primary-300 text-sm transition"
              >
                {isLogin ? "Hesabiniz yok mu? Kayit olun" : "Zaten hesabiniz var mi? Giris yapin"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Feature({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div className="flex items-start gap-4">
      <div className="p-3 bg-white/10 rounded-xl text-primary-300">{icon}</div>
      <div>
        <h3 className="text-white font-semibold">{title}</h3>
        <p className="text-primary-200 text-sm">{desc}</p>
      </div>
    </div>
  );
}
