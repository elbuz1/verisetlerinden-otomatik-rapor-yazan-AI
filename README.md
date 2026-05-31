# AI Destekli Veri Setlerinden Otomatik Rapor Yazma Sistemi

Kullanicilarin CSV, Excel veya JSON formatinda yukledikleri veri setlerini otomatik olarak analiz edip, istatistiksel bulgulari yorumlayan ve profesyonel PDF/DOCX raporlar ureten bir web uygulamasidir.

Sistem **hicbir harici AI API kullanmaz** (OpenAI, Claude, Gemini vb. yok). Tum yorumlar ve analizler kendi buyunyesindeki rule-based NLP motoru ve istatistiksel analiz servisleri tarafindan uretilir.

## Ozellikler

- **Veri Yukleme:** CSV, Excel (.xlsx/.xls) ve JSON dosya destegi, otomatik encoding/separator tespiti
- **Istatistiksel Analiz:** Ortalama, medyan, standart sapma, korelasyon matrisi, dagilim analizi
- **Trend Tespiti:** Linear regresyon ile trend yonu, egim, R-kare ve p-value hesaplama
- **Anomali Algilama:** IQR yontemi ve Isolation Forest ile aykiri deger tespiti
- **AI Yorum Uretimi:** 300+ Turkce sablon ile dinamik, veriye ozel yorumlar (harici API olmadan)
- **Grafik Olusturma:** 8 farkli grafik tipi (histogram, heatmap, boxplot, trend, bar, vs.)
- **Rapor Uretimi:** PDF (ReportLab) ve DOCX (python-docx) formatinda profesyonel raporlar
- **n8n Entegrasyonu:** Disaridan yapilandirilmis n8n workflow ile analiz pipeline orkestrasyonu
- **Dashboard:** Gercek zamanli istatistikler, son veri setleri ve raporlar
- **Guvenlik:** JWT token authentication, bcrypt sifre hashleme, rate limiting

## Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.14, FastAPI, SQLAlchemy (async), SQLite |
| Frontend | Next.js 14, React, TypeScript, TailwindCSS, Zustand |
| Analiz | pandas, numpy, scipy, scikit-learn |
| NLP | Rule-based template engine (300+ Turkce sablon) |
| Grafik | matplotlib, seaborn |
| Rapor | ReportLab (PDF), python-docx (DOCX) |
| Otomasyon | n8n (self-hosted, webhook tabanli) |
| Guvenlik | JWT, bcrypt, CORS, rate limiting |

## Gereksinimler

- **Python** 3.10 veya ustu
- **Node.js** 18 veya ustu
- **npm** 9 veya ustu
- **n8n** (npm ile global kurulum)

## Kurulum

### 1. Repoyu klonla

```bash
git clone https://github.com/enesbagis/verisetlerinden-otomatik-rapor-yazan-AI.git
cd verisetlerinden-otomatik-rapor-yazan-AI
```

### 2. Backend kurulumu

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Frontend kurulumu

```bash
cd frontend
npm install
```

### 4. n8n kurulumu

```bash
npm install -g n8n
```

### 5. n8n workflow import

```bash
n8n import:workflow --input="n8n-workflow/data-analysis-workflow.json"
n8n publish:workflow --id=1
```

## Calistirma

Uc ayri terminal penceresi acin:

**Terminal 1 - Backend:**
```bash
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - n8n:**
```bash
n8n start
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

Servisler basladiktan sonra:

| Servis | Adres |
|--------|-------|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Dokumantasyonu | http://localhost:8000/docs |
| n8n Editoru | http://localhost:5678 |

## Proje Yapisi

```
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI uygulama giris noktasi
│   │   ├── config.py                  # Yapilandirma ayarlari
│   │   ├── database.py                # SQLAlchemy async veritabani
│   │   ├── models/                    # Veritabani modelleri
│   │   │   ├── user.py                # Kullanici modeli
│   │   │   ├── dataset.py             # Veri seti modeli
│   │   │   ├── analytics.py           # Analiz sonuclari modeli
│   │   │   ├── report.py              # Rapor modeli
│   │   │   └── workflow_log.py        # Workflow log modeli
│   │   ├── routers/                   # API endpoint'leri
│   │   │   ├── auth.py                # Kayit/giris/profil
│   │   │   ├── upload.py              # Dosya yukleme
│   │   │   ├── analysis.py            # Analiz baslat/sonuc al
│   │   │   ├── reports.py             # Rapor olustur/indir
│   │   │   ├── dashboard.py           # Dashboard istatistikleri
│   │   │   └── n8n_webhook.py         # n8n entegrasyon endpoint'leri
│   │   ├── services/                  # Is mantigi servisleri
│   │   │   ├── data_parser.py         # CSV/Excel/JSON ayristirici
│   │   │   ├── analysis_service.py    # Istatistiksel analiz motoru
│   │   │   ├── nlp_service.py         # Rule-based AI yorum motoru
│   │   │   ├── chart_service.py       # Grafik olusturucu
│   │   │   ├── report_service.py      # PDF/DOCX rapor uretici
│   │   │   ├── workflow_service.py    # Dahili workflow motoru
│   │   │   └── n8n_trigger_service.py # n8n tetikleme servisi
│   │   ├── utils/
│   │   │   └── auth.py                # JWT ve sifreleme
│   │   └── middleware/
│   │       └── rate_limiter.py        # Istek hizi sinirlandirma
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx               # Giris/kayit sayfasi
│   │   │   ├── dashboard/page.tsx     # Dashboard
│   │   │   ├── upload/page.tsx        # Veri yukleme ve analiz
│   │   │   ├── analysis/page.tsx      # Analiz sonuclari
│   │   │   └── reports/page.tsx       # Rapor listesi
│   │   ├── components/layout/
│   │   │   └── Sidebar.tsx            # Navigasyon sidebar
│   │   └── lib/
│   │       ├── api.ts                 # API istemcisi (axios)
│   │       └── store.ts              # Zustand durum yonetimi
│   ├── package.json
│   └── tailwind.config.ts
├── n8n-workflow/
│   └── data-analysis-workflow.json    # n8n workflow tanimi
├── sample-data/
│   ├── satis_verileri.csv             # Ornek satis verisi (30 satir)
│   └── musteri_analizi.json           # Ornek musteri verisi (20 kayit)
├── docs/
│   ├── AI_Rapor_Sistemi_Proje_Raporu.docx  # IEEE formatinda proje raporu
│   ├── PROJE_MANTIGI.md               # Sistem mimarisi aciklamasi
│   ├── DOSYA_ACIKLAMALARI.md           # Dosya bazinda aciklamalar
│   ├── KURULUM_REHBERI.md              # Detayli kurulum rehberi
│   ├── N8N_BAGLANTI_REHBERI.md         # n8n yapilandirma rehberi
│   └── VIDEO_SUNUM_METNI.md            # Video sunum senaryosu
├── docker-compose.yml
└── .gitignore
```

## Kullanim

1. Tarayicida `http://localhost:3000` adresine gidin
2. Yeni hesap olusturun (Kayit Ol)
3. Dashboard'dan sisteme goz atin
4. **Veri Yukle** sayfasindan CSV/Excel/JSON dosyanizi yukleyin
5. Yuklenen veri onizlemesini kontrol edin
6. **AI Analiz Baslat** butonuna basin
7. Analiz tamamlaninca sonuclari (AI yorumlari, trendler, anomaliler) inceleyin
8. **PDF Rapor Indir** veya **DOCX Rapor Indir** ile profesyonel raporu indirin

## API Endpoint'leri

| Method | Endpoint | Aciklama |
|--------|----------|----------|
| POST | /api/auth/register | Yeni kullanici kaydi |
| POST | /api/auth/login | Kullanici girisi |
| GET | /api/auth/me | Mevcut kullanici bilgisi |
| POST | /api/upload/ | Dosya yukleme |
| GET | /api/upload/datasets | Veri setlerini listele |
| POST | /api/analysis/{id} | Analiz baslat |
| GET | /api/analysis/{id} | Analiz sonuclarini al |
| POST | /api/reports/generate/{id} | Rapor olustur |
| GET | /api/reports/download/{id} | Rapor indir |
| GET | /api/dashboard/stats | Dashboard istatistikleri |
| GET | /api/n8n/health | n8n baglanti durumu |

## n8n Workflow

Sistem, n8n uzerinden disaridan yapilandirilmis bir analiz pipeline'i kullanir:

```
Webhook Trigger → Workflow Baslat → Veri Parse → Istatistiksel Analiz →
AI Yorum Uret → Grafik Olustur → Rapor Olustur → Tamamla → Yanit
```

n8n editoru (`http://localhost:5678`) uzerinden workflow gorsel olarak izlenebilir ve yonetilebilir.

## Katki

1. Bu repoyu fork edin
2. Yeni bir branch olusturun (`git checkout -b ozellik/yeni-ozellik`)
3. Degisikliklerinizi commit edin (`git commit -m 'Yeni ozellik eklendi'`)
4. Branch'inizi push edin (`git push origin ozellik/yeni-ozellik`)
5. Pull Request olusturun

## Lisans

Bu proje egitim amacli gelistirilmistir.
