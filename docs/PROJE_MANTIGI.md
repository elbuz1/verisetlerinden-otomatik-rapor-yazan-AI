# PROJE MANTIGI - Detayli Sistem Aciklamasi

## 1. Sistemin Genel Calisma Mantigi

Bu sistem, kullanicinin yukladigi veri setlerini (CSV, Excel, JSON) otomatik olarak
analiz eden, istatistiksel sonuclar cikaran ve bu sonuclari "insan yazimi gibi"
yorumlayarak profesyonel PDF/DOCX raporlari ureten bir platformdur.

Kritik fark: Sistem OpenAI, Claude veya Gemini gibi harici AI API'leri KULLANMAZ.
Bunun yerine, kural tabanli (rule-based) bir yapay zeka motoru kullanir. Bu motor,
veri analiz sonuclarina bakarak onceden tanimlanmis yuzlerce sablon arasindan
en uygunlarini secer ve degiskenleri doldurarak dogal dilde yorum uretir.

## 2. Veri Akisi (Data Flow)

```
[1] Kullanici dosya yukler (Drag & Drop)
         |
[2] Frontend --> POST /api/upload/ --> Backend
         |
[3] DataParser servisi dosyayi okur (pandas ile)
    - CSV: otomatik encoding ve separator tespiti
    - Excel: openpyxl motoru ile
    - JSON: liste veya dict formatini otomatik algilar
         |
[4] Dosya bilgileri ve on izleme veritabanina kaydedilir
    (datasets tablosu)
         |
[5] Kullanici "AI Analiz Baslat" butonuna tiklar
         |
[6] Frontend --> POST /api/analysis/{id} --> Backend
         |
[7] Workflow motoru baslar, her adimi loglar:
    a) Dosya dogrulama
    b) Veri ayristirma (parsing)
    c) Istatistiksel analiz (AnalysisService)
       - Temel istatistikler (ortalama, medyan, std sapma...)
       - Korelasyon matrisi
       - Eksik veri analizi
       - Dagilim analizi (normallik testi)
       - Trend tespiti (lineer regresyon)
       - Anomali algilama (IQR + Isolation Forest)
       - Kategori analizi
       - Veri kalitesi skorlamasi
    d) AI yorum uretimi (NLPCommentGenerator)
       - Yonetici ozeti
       - Trend yorumlari
       - Korelasyon yorumlari
       - Anomali uyarilari
       - Eksik veri degerlendirmesi
       - Dagilim yorumlari
       - Oneriler
    e) Grafik olusturma (ChartService)
       - Dagilim histogramlari
       - Korelasyon isisi haritasi
       - Kutu grafikleri
       - Trend grafikleri
       - Kategori grafikleri
       - Eksik veri grafigi
       - Kalite skoru grafigi
       - Genel bakis grafigi
    f) Veritabanina kayit
         |
[8] Sonuclar Frontend'e doner, kullanici goruntuler
         |
[9] Kullanici "PDF/DOCX Indir" tiklar
         |
[10] ReportService rapor olusturur:
     - Kapak sayfasi
     - Icindekiler
     - Yonetici ozeti
     - Veri genel bakis
     - Istatistiksel analiz tablolari
     - Grafikler
     - Trend analizi yorumlari
     - Anomali raporlari
     - AI yorumlari
     - Oneriler
     - Sonuc
         |
[11] Rapor dosyasi indirilir
```

## 3. n8n Ne Yapiyor?

n8n, sistemdeki otomasyon katmanidir. Iki sekilde calisir:

### a) Webhook Tabanli Tetikleme
n8n'de tanimli workflow, bir webhook URL'i uzerinden tetiklenir.
Backend'den veya dis sistemlerden gelen istekler bu webhook'a yonlendirilir.
Workflow sirasi: Veri al -> Dogrula -> Analiz -> Rapor olustur -> Yanit don

### b) Dahili Workflow Motoru
Backend icindeki WorkflowService, n8n benzeri bir pipeline mantigi calistirir.
Her analiz adimi bir "step" olarak izlenir ve loglanir. Frontend'de kullanici
bu adimlari canli olarak gorebilir (animasyonlu ilerleme cubugu).

Workflow JSON dosyalari `workflows/` klasorunde saklanir ve n8n arayuzune
import edilebilir.

## 4. Backend Ne Yapiyor?

FastAPI uzerine kurulu backend 5 ana sorumluluga sahiptir:

### a) Dosya Yonetimi (upload router)
- Dosya yukleme, dogrulama, depolama
- Veri on izleme ve sutun analizi
- Desteklenen formatlar: CSV, XLSX, XLS, JSON

### b) Analiz Motoru (analysis router + services)
- AnalysisService: Istatistiksel hesaplamalar
- NLPCommentGenerator: Dinamik yorum uretimi
- ChartService: Grafik ve gorsellestirme
- WorkflowService: Adim izleme ve loglama

### c) Rapor Uretimi (reports router)
- PDF: ReportLab kutuphanesi ile profesyonel PDF
- DOCX: python-docx kutuphanesi ile Word belgesi
- Her iki formatta da grafik, tablo ve AI yorumlari yer alir

### d) Kimlik Dogrulama (auth router)
- JWT token tabanli kimlik dogrulama
- Bcrypt ile sifre hashleme
- Kullanici kayit ve giris

### e) Dashboard (dashboard router)
- Genel istatistikler
- Son veri setleri ve raporlar
- Workflow durumu takibi

## 5. Database Ne Yapiyor?

PostgreSQL veritabani 5 ana tablodan olusur:

### users
Kullanici hesaplari. Email ve username uzerinde unique index.
Sifreler bcrypt ile hashlenip saklanir.

### datasets
Yuklenen veri setleri. Her kayit bir dosyayi temsil eder.
columns_info JSONB alani, sutun bilgilerini (tip, bos deger orani vb.) saklar.
status alani: uploaded -> processing -> analyzed -> error

### analytics_results
Analiz sonuclari. Her kayit bir analizin tum sonuclarini JSONB olarak saklar.
basic_stats, correlation_matrix, trend_analysis, anomalies, ai_insights...

### reports
Olusturulan raporlar. Dosya yolu, boyut, format ve AI yorumlarini icerir.
executive_summary ve recommendations alanlari dogal dil metinleri barindirir.

### workflow_logs
Her analiz isleminin adim adim logunu tutar.
step_details JSONB alani, her adimin durumunu ve detaylarini saklar.

Iliskiler:
- users 1:N datasets (bir kullanici birden fazla veri seti yukleyebilir)
- users 1:N reports
- datasets 1:N analytics_results
- datasets 1:N reports
- datasets 1:N workflow_logs

## 6. Dashboard Nasil Calisiyor?

Dashboard, backend'deki /api/dashboard/* endpointlerinden veri ceker:

- /stats: Toplam veri seti, rapor, satir sayisi, ortalama kalite skoru
- /recent-datasets: Son 10 yuklenen veri seti
- /recent-reports: Son 10 olusturulan rapor
- /workflows: Son workflow loglari

Frontend'de Zustand state management ile veri yonetilir.
Sayfa yuklendiginde 3 API cagrisinin hepsi paralel yapilir (Promise.all).

## 7. AI Benzeri Yorum Sistemi Nasil Calisiyor?

Bu sistemin en kritik parcasi NLPCommentGenerator sinifidir.
Harici API KULLANMADAN "AI gibi" yorum uretir. Mantigi soyledir:

### Sablon Havuzu
300+ onceden yazilmis Turkce sablon vardir. Her sablon icinde
degiskenler ({col}, {value}, {percentage} vb.) bulunur.

### Kural Motoru
Analiz sonuclarina gore kurallar tetiklenir:
- Trend yukari ise -> yiükselis sablonlarindan sec
- Anomali varsa -> uyari sablonlarindan sec
- Korelasyon gucluyse -> iliski sablonlarindan sec

### Dinamik Secim
Her calistirildiginda random.choice() ile farkli sablonlar secilir.
Boylece ayni veri seti icin bile farkli yorumlar uretilir.

### Degisken Doldurma
Secilen sablondaki degiskenler gercek veri degerleriyle doldurulur.
Ornek: "{col} degiskeninde %{change} artis" -> "satis_miktari degiskeninde %23.5 artis"

Bu yaklasim, GPT veya Claude kullanan bir sistemden farkli olarak:
- Tamamen offine calisir
- Tahmin edilebilir ve tutarli sonuclar verir
- Maliyet sifirdir (API ucreti yok)
- Turkce gramer ve terim tutarliligi garanti edilir
