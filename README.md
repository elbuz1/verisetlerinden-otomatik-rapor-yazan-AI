# AI Destekli Veri Setlerinden Otomatik Rapor Yazma Sistemi

Kullanicilarin CSV, Excel veya JSON formatinda yukledikleri veri setlerini otomatik olarak analiz eden, istatistiksel bulgulari Turkce yorumlayan ve profesyonel PDF/DOCX raporlar ureten bir web uygulamasidir.

**Harici AI API kullanilmaz.** OpenAI, Claude, Gemini gibi hicbir dis servis yoktur. Tum yorumlar ve analizler sistemin kendi bunyesindeki rule-based NLP motoru ve istatistiksel analiz servisleri tarafindan uretilir.

---

## Nasil Calisiyor?

```
Kullanici dosya yukler (CSV/Excel/JSON)
        |
        v
   n8n Webhook tetiklenir
        |
        v
   Backend analiz pipeline'i baslar:
   1. Dosya parse edilir (encoding otomatik algilanir)
   2. Istatistiksel analiz yapilir (ortalama, medyan, std sapma, korelasyon)
   3. Trend tespiti (linear regresyon, p-value, R²)
   4. Anomali algilama (IQR + Isolation Forest)
   5. 300+ Turkce sablondan dinamik AI yorumlari uretilir
   6. 8 farkli grafik olusturulur (matplotlib/seaborn)
   7. PDF veya DOCX rapor uretilir
        |
        v
   Kullanici raporu indirir
```

Her calistirmada farkli sablonlar secilir, bu sayede ayni veriye bile farkli yorumlar uretilir. Raporlar kapak sayfasi, icerik tablosu, istatistik tablolari, grafikler, AI yorumlari ve oneriler icerir.

---

## Ozellikler

- **Coklu Format Destegi:** CSV, Excel (.xlsx/.xls) ve JSON dosya yukleme
- **Otomatik Encoding Tespiti:** chardet ile Turkce karakterler dahil tum kodlamalar
- **Istatistiksel Analiz:** Ortalama, medyan, standart sapma, korelasyon matrisi, dagilim analizi
- **Trend Tespiti:** Linear regresyon ile trend yonu, egim, R-kare ve p-value
- **Anomali Algilama:** IQR yontemi ve Isolation Forest ile aykiri deger tespiti
- **Veri Kalite Skoru:** Tamlik, tutarlilik ve benzersizlik bazli A/B/C/D derecelendirme
- **AI Yorum Uretimi:** 300+ Turkce sablon ile veriye ozel dinamik yorumlar
- **Grafik Olusturma:** Histogram, korelasyon heatmap, boxplot, trend, bar, missing data, kalite gauge, dashboard
- **Rapor Uretimi:** PDF (ReportLab) ve DOCX (python-docx) formatinda profesyonel raporlar
- **n8n Entegrasyonu:** Disaridan yapilandirilmis workflow ile pipeline orkestrasyonu
- **Kullanici Yonetimi:** JWT token authentication, bcrypt sifre hashleme
- **Dashboard:** Toplam veri seti, rapor sayisi, analiz istatistikleri

---

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

---

## Sistem Mimarisi

```
+-----------------------+     +------------------------+     +-------------------+
|   Frontend (Next.js)  |     |   Backend (FastAPI)    |     |   n8n Workflow    |
|   localhost:3000      |---->|   localhost:8000       |<--->|   localhost:5678  |
|                       |     |                       |     |                  |
|  - Giris/Kayit        |     |  - Auth (JWT+bcrypt)  |     |  - Webhook       |
|  - Dashboard          |     |  - Upload             |     |  - HTTP Request  |
|  - Veri Yukleme       |     |  - Analysis           |     |  - Pipeline      |
|  - Analiz Sonuclari   |     |  - Reports            |     |    orkestrasyonu |
|  - Rapor Indirme      |     |  - Dashboard API      |     |                  |
+-----------------------+     |  - n8n Webhook API    |     +-------------------+
                              +-----------+-----------+
                                          |
                      +-------------------+-------------------+
                      |                   |                   |
               +------+------+    +-------+-------+   +------+------+
               | DataParser   |    | AnalysisServ  |   | NLP Service |
               | CSV/Excel/   |    | Stats/Trend/  |   | 300+ Turkce |
               | JSON parse   |    | Anomali/Corr  |   | sablon      |
               +------+------+    +-------+-------+   +------+------+
                      |                   |                   |
               +------+------+    +-------+-------+   +------+------+
               | ChartService |    | ReportService |   |  SQLite DB  |
               | 8 grafik tipi|    | PDF + DOCX    |   |  5 tablo    |
               +--------------+    +---------------+   +-------------+
```

---

## Gereksinimler

- Python 3.10 veya ustu
- Node.js 18 veya ustu
- npm 9 veya ustu

---

## Kurulum

### 1. Repoyu klonla

```bash
git clone https://github.com/elbuz1/verisetlerinden-otomatik-rapor-yazan-AI.git
cd verisetlerinden-otomatik-rapor-yazan-AI
```

### 2. Backend kurulumu

```bash
cd backend
python -m venv venv
```

Windows:
```bash
.\venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

Paketleri kur:
```bash
pip install -r requirements.txt
```

> Python 3.14 kullaniyorsaniz bazi paketlerde `pip install --pre -r requirements.txt` gerekebilir.

### 3. Backend ortam degiskenleri

`backend/.env` dosyasi olusturun:
```
SECRET_KEY=super-secret-key-change-in-production-2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=["http://localhost:3000"]
```

### 4. Frontend kurulumu

```bash
cd frontend
npm install
```

### 5. n8n kurulumu

```bash
npm install -g n8n
```

Workflow'u ice aktar:
```bash
n8n import:workflow --input="n8n-workflow/data-analysis-workflow.json"
n8n publish:workflow --id=1
```

---

## Calistirma

**3 ayri terminal penceresi** acin. Her servis kendi terminalinde calisir:

### Terminal 1 - Backend
```bash
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```
> `Application startup complete` mesajini gorunce hazir.

### Terminal 2 - n8n
```bash
n8n start
```
> `Editor is now accessible via: http://localhost:5678` mesajini gorunce hazir.

### Terminal 3 - Frontend
```bash
cd frontend
npm run dev
```
> `Ready in X.Xs` mesajini gorunce hazir.

### Erisim adresleri

| Servis | Adres |
|--------|-------|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Dokumantasyonu (Swagger) | http://localhost:8000/docs |
| n8n Workflow Editoru | http://localhost:5678 |

---

## Kullanim

1. Tarayicida `http://localhost:3000` adresine gidin
2. **Kayit Ol** ile yeni hesap olusturun
3. Giris yaptiktan sonra **Dashboard** ekranini goreceksiniz
4. Sol menuden **Veri Yukle** sayfasina gidin
5. CSV, Excel veya JSON dosyanizi surukleyip birakin ya da tiklayarak secin
6. Yuklenen verinin onizlemesini ve sutun bilgilerini kontrol edin
7. **AI Analiz Baslat** butonuna basin
8. Analiz sirasinda workflow adimlari canli olarak gosterilir (8 adim)
9. Analiz tamamlaninca sonuclari inceleyin:
   - AI yonetici ozeti
   - Trend analizleri ve yorumlar
   - Anomali tespitleri
   - Korelasyon bulgulari
   - AI onerileri
10. **PDF Rapor Indir** veya **DOCX Rapor Indir** ile profesyonel raporu indirin

### Ornek veri setleri

`sample-data/` klasorunde hazir veri setleri bulunur:
- `satis_verileri.csv` - 30 satirlik Turkce satis verisi
- `musteri_analizi.json` - 20 kayitlik musteri memnuniyet verisi

---

## n8n Workflow Yapilandirmasi

n8n, analiz pipeline'ini disaridan yoneten orkestrasyon aracidir. Workflow su adimlari sirasyla calistirir:

```
Webhook Trigger --> Workflow Baslat --> Veri Parse Et --> Istatistiksel Analiz -->
AI Yorum Uret --> Grafik Olustur --> Rapor Olustur --> Tamamla --> Yanit
```

### n8n'de workflow'u gormek:
1. `http://localhost:5678` adresine gidin
2. Ilk giriste hesap olusturun
3. Sol menuden **Workflows** tiklayin
4. **Veri Analiz Pipeline - AI Rapor Sistemi** workflow'unu acin
5. Sag ustteki toggle'in **Active** oldugunu dogrulayin

Her node, backend'deki `/api/n8n/` endpoint'lerini cagirir. n8n editoru uzerinden veri akisini gorsel olarak takip edebilirsiniz.

---

## Proje Yapisi

```
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI uygulama giris noktasi
│   │   ├── config.py                  # Yapilandirma ayarlari
│   │   ├── database.py                # SQLAlchemy async veritabani baglantisi
│   │   ├── models/                    # Veritabani modelleri
│   │   │   ├── user.py                # Kullanici (email, username, hashed_password)
│   │   │   ├── dataset.py             # Veri seti (dosya bilgileri, sutun bilgileri)
│   │   │   ├── analytics.py           # Analiz sonuclari (stats, korelasyon, anomali)
│   │   │   ├── report.py              # Rapor (PDF/DOCX, AI yorumlari)
│   │   │   └── workflow_log.py        # Workflow calisma kayitlari
│   │   ├── routers/                   # API endpoint'leri
│   │   │   ├── auth.py                # POST /api/auth/register, /login, GET /me
│   │   │   ├── upload.py              # POST /api/upload/, GET /datasets
│   │   │   ├── analysis.py            # POST /api/analysis/{id}, GET sonuclar
│   │   │   ├── reports.py             # POST /api/reports/generate, GET /download
│   │   │   ├── dashboard.py           # GET /api/dashboard/stats, recent-*
│   │   │   └── n8n_webhook.py         # n8n'in cagirdigi 7 pipeline endpoint'i
│   │   ├── services/                  # Is mantigi servisleri
│   │   │   ├── data_parser.py         # CSV/Excel/JSON parser (encoding tespiti)
│   │   │   ├── analysis_service.py    # Istatistik, trend, anomali, korelasyon
│   │   │   ├── nlp_service.py         # 300+ sablonla Turkce yorum uretimi
│   │   │   ├── chart_service.py       # 8 grafik tipi (matplotlib/seaborn)
│   │   │   ├── report_service.py      # PDF (ReportLab) + DOCX (python-docx)
│   │   │   ├── workflow_service.py    # Dahili workflow takip motoru
│   │   │   └── n8n_trigger_service.py # n8n webhook tetikleme servisi
│   │   ├── utils/auth.py              # JWT token + bcrypt sifreleme
│   │   └── middleware/rate_limiter.py  # IP bazli istek sinirlandirma
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx               # Giris / Kayit sayfasi
│   │   │   ├── dashboard/page.tsx     # Dashboard (6 istatistik karti)
│   │   │   ├── upload/page.tsx        # Veri yukleme + analiz + rapor indirme
│   │   │   ├── analysis/page.tsx      # Analiz sonuclari goruntuleyici
│   │   │   └── reports/page.tsx       # Rapor listesi
│   │   ├── components/layout/
│   │   │   └── Sidebar.tsx            # Sol navigasyon menusu
│   │   └── lib/
│   │       ├── api.ts                 # Axios API istemcisi (JWT interceptor)
│   │       └── store.ts               # Zustand global state yonetimi
│   ├── package.json
│   └── next.config.js                 # Backend API proxy ayari
├── n8n-workflow/
│   └── data-analysis-workflow.json    # n8n workflow tanimlamasi
├── sample-data/                       # Test icin ornek veri setleri
├── docs/
│   └── AI_Rapor_Sistemi_Proje_Raporu.docx  # IEEE formatinda proje raporu
├── docker-compose.yml
└── .gitignore
```

---

## API Endpoint'leri

| Method | Endpoint | Aciklama |
|--------|----------|----------|
| POST | `/api/auth/register` | Yeni kullanici kaydi |
| POST | `/api/auth/login` | Kullanici girisi (JWT token doner) |
| GET | `/api/auth/me` | Mevcut kullanici bilgisi |
| POST | `/api/upload/` | Dosya yukleme (CSV/Excel/JSON) |
| GET | `/api/upload/datasets` | Kullanicinin veri setlerini listele |
| POST | `/api/analysis/{id}` | Analiz baslat |
| GET | `/api/analysis/{id}` | Analiz sonuclarini getir |
| POST | `/api/reports/generate/{id}` | PDF veya DOCX rapor olustur |
| GET | `/api/reports/download/{id}` | Raporu indir |
| GET | `/api/dashboard/stats` | Dashboard istatistikleri |
| GET | `/api/n8n/health` | n8n baglanti durumu |
| POST | `/api/n8n/trigger` | n8n workflow'u tetikle |

Tum endpoint'lerin detayli dokumantasyonu: `http://localhost:8000/docs` (Swagger UI)

---

## Veritabani Yapisi

SQLite uzerinde 5 tablo:

- **users** - Kullanici bilgileri ve kimlik dogrulama
- **datasets** - Yuklenen dosyalarin meta verileri ve sutun bilgileri
- **analytics_results** - Analiz sonuclari (JSON alanlarinda stats, korelasyon, anomali vb.)
- **reports** - Olusturulan raporlarin kayitlari ve dosya yollari
- **workflow_logs** - Her analiz calismasinin adim adim kaydi

---

## Lisans

Bu proje universite bitirme projesi olarak gelistirilmistir.
