# DOSYA DOSYA ACIKLAMA

## Backend Dosyalari

### backend/app/main.py
Uygulamanin giris noktasi. FastAPI uygulamasini olusturur, CORS middleware'i ekler,
rate limiter'i yapilandirir ve tum router'lari baglar. Uygulama basladiginda
veritabani tablolarini otomatik olusturur (init_db).

### backend/app/config.py
Tum yapilandirma ayarlari. Pydantic Settings kullanarak .env dosyasindan veya
ortam degiskenlerinden ayarlari okur. Veritabani URL'i, JWT secret key, upload
limitleri, CORS ayarlari burada tanimlidir.

### backend/app/database.py
SQLAlchemy async engine ve session olusturma. get_db dependency injection ile
her API istemine ayrı bir veritabani oturumu saglar. Otomatik commit/rollback
yapar.

### backend/app/models/user.py
Kullanici veritabani modeli. email ve username unique, sifreler hashlenip
hashed_password alaninda saklanir. datasets ve reports ile one-to-many iliski.

### backend/app/models/dataset.py
Yuklenen veri setlerinin modeli. Dosya bilgileri, satir/sutun sayilari,
columns_info (JSONB - her sutunun tip ve istatistikleri), status (uploaded,
processing, analyzed, error) alanlari icerir.

### backend/app/models/analytics.py
Analiz sonuc modeli. Tum analiz verileri JSONB alanlarda saklanir:
basic_stats, correlation_matrix, missing_data, distribution_info,
trend_analysis, anomalies, category_analysis, ai_insights.

### backend/app/models/report.py
Rapor modeli. Dosya yolu, format (pdf/docx), boyut, executive_summary (metin),
ai_comments (JSONB), recommendations (JSONB) alanlari icerir.

### backend/app/models/workflow_log.py
Workflow izleme modeli. Her analiz isleminin adim adim durumunu kayit eder.
step_details JSONB alani her adimin detaylarini tutar.

### backend/app/services/data_parser.py
Veri okuma servisi. CSV, Excel ve JSON dosyalarini pandas DataFrame'e cevirir.
CSV icin otomatik encoding tespiti (chardet) ve separator tespiti yapar.
JSON icin liste/dict/nested formatlari otomatik algilar. On izleme ve
sutun bilgisi cikarma fonksiyonlari icerir.

### backend/app/services/analysis_service.py
Istatistiksel analiz motoru. Sistemin beyni sayilabilecek dosya. Icerir:
- Temel istatistikler (ortalama, medyan, standart sapma, carpiklik, basiklik)
- Korelasyon analizi (Pearson korelasyonu, guclu korelasyon tespiti)
- Eksik veri analizi (yuzde, siddet seviyesi)
- Dagilim analizi (normallik testi, carpiklik yonu)
- Trend analizi (lineer regresyon, segment bazli degisim)
- Anomali tespiti (IQR yontemi + Isolation Forest)
- Kategori analizi (frekans, entropi)
- Veri kalitesi skorlamasi (tamlik, teklik, tutarlilik)

### backend/app/services/nlp_service.py
AI benzeri yorum uretme motoru. PROJENIN EN ONEMLI DOSYASI. 300+ Turkce
sablon iceren kural tabanli bir NLP sistemi. Analiz sonuclarina gore
dinamik olarak farkli sablonlar secer ve degiskenleri gercek verilerle
doldurur. Her calistirmada farkli yorumlar uretir.

Urettigi yorum turleri:
- Yonetici ozeti (executive summary)
- Trend yorumlari (artis/azalis/duragan)
- Korelasyon yorumlari (pozitif/negatif guclu iliskiler)
- Anomali uyarilari (siddet seviyesine gore)
- Eksik veri degerlendirmesi (dusuk/orta/yuksek)
- Dagilim yorumlari (normal/carpik)
- Oneriler (veri kalitesi, anomali yonetimi, trend takibi)

### backend/app/services/chart_service.py
Grafik olusturma servisi. matplotlib ve seaborn kullanarak profesyonel
grafikler uretir:
- Dagilim histogramlari
- Korelasyon isi haritasi
- Kutu grafikleri (boxplot)
- Trend grafikleri (hareketli ortalama + lineer trend)
- Kategori bar grafikleri
- Eksik veri grafigi
- Kalite skoru grafigi
- Genel bakis dashboard grafigi

### backend/app/services/report_service.py
PDF ve DOCX rapor uretme servisi. ReportLab ile profesyonel PDF,
python-docx ile Word belgesi olusturur. Her iki formatta da:
- Kapak sayfasi
- Icindekiler
- Yonetici ozeti
- Veri genel bakis tablosu
- Istatistik tablolari
- Grafikler
- AI yorumlari
- Oneriler
- Sonuc

### backend/app/services/workflow_service.py
Workflow izleme servisi. n8n benzeri bir pipeline mantigi ile her analiz
adimini loglar. Adimlari baslat/guncelle/tamamla/hata olarak isaretler.
Frontend'de canli ilerleme gosterimi icin kullanilir.

### backend/app/utils/auth.py
JWT kimlik dogrulama yardimcilari. Sifre hashleme (bcrypt), token
olusturma ve dogrulama, mevcut kullaniciyi getirme fonksiyonlari.

### backend/app/middleware/rate_limiter.py
IP bazli rate limiting. Saniyede/dakikada maksimum istek sayisini sinirlar.
429 Too Many Requests hatasi dondurur.

### backend/app/routers/auth.py
Kimlik dogrulama API'si. /register (kayit), /login (giris), /me (profil).
OAuth2 uyumlu token akisi.

### backend/app/routers/upload.py
Dosya yukleme API'si. Drag & drop ile gelen dosyalari alir, dogrular,
kaydeder ve on izleme verisini dondurur. Desteklenen formatlar: CSV, XLSX, JSON.

### backend/app/routers/analysis.py
Analiz API'si. POST /{id} ile analiz baslatir, GET /{id} ile sonuclari dondurur.
Tum analiz servislerini orkestra eder ve workflow loglarini tutar.

### backend/app/routers/reports.py
Rapor API'si. POST /generate/{id} ile rapor olusturur (format parametresiyle
pdf veya docx), GET /download/{id} ile rapor dosyasini indirir.

### backend/app/routers/dashboard.py
Dashboard API'si. Genel istatistikler, son veri setleri, son raporlar
ve workflow durumlari icin endpointler saglar.

## Frontend Dosyalari

### frontend/src/app/layout.tsx
Root layout. Inter fontu, global stiller, Toaster (bildirim) bilesenini icerir.
HTML lang="tr" ve dark mode varsayilan olarak aktif.

### frontend/src/app/page.tsx
Giris/kayit sayfasi. Sol tarafta marka tanitimi (branding), sag tarafta
giris/kayit formu. Glassmorphism tasarimli. Kimlik dogrulama sonrasi
/dashboard'a yonlendirir.

### frontend/src/app/dashboard/layout.tsx
Dashboard layout. Sidebar bilesenini icerir ve kimlik dogrulama kontrolu yapar.
Giris yapilmamissa ana sayfaya yonlendirir.

### frontend/src/app/dashboard/page.tsx
Ana dashboard sayfasi. 6 istatistik karti, son veri setleri ve son raporlar
listesi. Tum veriler paralel API cagrilari ile yuklenir.

### frontend/src/app/upload/page.tsx
Dosya yukleme ve analiz sayfasi. 4 adimli wizard:
1. Drag & drop ile dosya yukleme
2. Veri on izleme ve sutun bilgileri
3. AI analiz calismasi (canli workflow animasyonu)
4. Sonuclar ve rapor indirme

### frontend/src/app/analysis/page.tsx
Analiz listesi sayfasi. Sol panelde veri setleri, sag panelde secili
analizin detaylari: yonetici ozeti, istatistik tablosu, trend yorumlari,
anomali tespitleri.

### frontend/src/app/reports/page.tsx
Rapor listesi sayfasi. Grid gorunumunde tum raporlar. Her kart dosya
formati, tarih ve indirme butonu icerir.

### frontend/src/components/layout/Sidebar.tsx
Sol menu. Navigation linkleri, aktif sayfa vurgulama, kullanici bilgisi
ve cikis butonu. Glassmorphism tasarimli.

### frontend/src/lib/api.ts
Axios tabanli API istemci. Tum backend endpointlerini fonksiyon olarak
sunar. JWT token'i otomatik olarak Authorization header'ina ekler.
401 hatalarinda otomatik cikis yapar.

### frontend/src/lib/store.ts
Zustand state management. Kullanici bilgileri, token ve kimlik dogrulama
durumunu yonetir. localStorage ile kalici oturum saglar.

### frontend/src/styles/globals.css
TailwindCSS ile global stiller. Ozel siniflar:
- glass-card: Glassmorphism kart
- btn-primary/btn-secondary: Buton stilleri
- input-field: Form input stili
- gradient-text: Degrade metin

## Diger Dosyalar

### docker-compose.yml
4 servis tanimlar: PostgreSQL, Backend (FastAPI), Frontend (Next.js), n8n.
Volume'lar ile veri kaliciligi saglar.

### database/init.sql
PostgreSQL sema olusturma. 5 tablo ve indexleri tanimlar.

### workflows/n8n-data-analysis-workflow.json
n8n'e import edilebilir workflow JSON'i. Webhook tetikleme, veri dogrulama,
analiz calistirma, rapor olusturma adimlarini icerir.

### sample-data/satis_verileri.csv
30 satirlik ornek satis verisi. Tarih, urun, kategori, satis miktari,
fiyat, gelir, maliyet, kar, bolge, musteri tipi sutunlari.

### sample-data/musteri_analizi.json
20 musterili ornek JSON veri seti. Demografik ve davranissal veriler.
