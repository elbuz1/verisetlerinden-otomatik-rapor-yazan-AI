# VIDEO SUNUM METNI - Ekran Kaydi Anlatim Rehberi

## Genel Bilgi
- Toplam sure: 25-35 dakika
- Hedef kitle: Bilgisayar muhendisligi seviyesi
- Ton: Dogal, teknik ama anlasilir, ezber gibi olmayan

---

## BOLUM 1 - GIRIS (3-4 dk)
**Ekranda: Masaustu, proje klasoru kapali**

"Merhabalar, bugun sizlere gelistirdigim AI Destekli Veri Setlerinden Otomatik
Rapor Yazma Sistemi'ni gosterecegim.

Projenin temel amaci su: bir kullanici CSV, Excel veya JSON formatinda bir veri
seti yukluyor, sistem bu veriyi otomatik olarak analiz ediyor -- istatistik
cikariyor, trendleri buluyor, anomalileri tespit ediyor -- ve sonra bu analiz
sonuclarina bakarak insan yazimi gibi yorumlar uretiyor. En sonunda da
profesyonel bir PDF veya Word raporu olusturuyor.

Burada kritik bir detay var: bu sistemde OpenAI, Claude veya Gemini gibi harici
bir AI API kullanilmiyor. Yani disa bagimli degil. Tum zeka kismi, kural tabanli
bir yapay zeka motoru uzerine kurulu. Birazdan bunu detayli gorecegiz.

Kullandigim teknolojilere hizlica degineyim: Backend tarafinda Python FastAPI
kullandim. Veri analizi icin pandas, numpy, scikit-learn var. Frontend React ve
Next.js ile. Veritabani PostgreSQL. Otomasyon katmaninda n8n workflow sistemi
kullandim. Her sey Docker uzerinde calisabiliyor."

---

## BOLUM 2 - PROJE YAPISI (4-5 dk)
**Ekranda: VS Code veya dosya gezgini acik, proje klasoru**

"Simdi proje yapisina bakalim. Ana klasoru aciyorum.

*(klasoru ac)*

Gordugunuz gibi temiz bir yapilandirma var. Birer birer gecelim:

**backend/** klasoru -- burada tum sunucu tarafi kodlari var. FastAPI uygulamasi,
veritabani modelleri, analiz servisleri, rapor uretici, NLP motoru... Hepsini
ayri ayri inceleyecegiz.

**frontend/** klasoru -- Next.js ile yazilmis arayuz. Dashboard, dosya yukleme
sayfasi, analiz sonuclari, rapor listesi burada.

**database/** klasoru -- PostgreSQL sema dosyasi. Tablolarin tanimlamalari burada.
init.sql dosyasini acarsaniz users, datasets, reports, analytics_results,
workflow_logs tablolarini gorursunuz.

**workflows/** klasoru -- n8n workflow JSON dosyalari. Bunlari n8n arayuzune
import edebilirsiniz.

**sample-data/** klasoru -- test icin hazirledigim ornek veri setleri var. Bir
satis verisi CSV'si ve bir musteri analizi JSON'i.

**docker-compose.yml** -- tek komutla tum sistemi ayaga kaldiran Docker dosyasi.
PostgreSQL, backend, frontend ve n8n hepsini birlikte baslatir.

Simdi backend'in ic yapisina girelim."

**Ekranda: backend/app/ klasoru acik**

"backend/app/ icinde gorudugunuz yapiya bakin:

- **main.py** -- uygulamanin giris noktasi. FastAPI uygulamasini burada
  olusturuyorum, middleware'leri ekliyorum, router'lari bagliyorum.

- **config.py** -- tum ayarlar burada. Veritabani URL'i, JWT secret key, upload
  limitleri... .env dosyasindan otomatik okuyor.

- **models/** -- veritabani modelleri. SQLAlchemy kullanarak 5 tablo tanimladim.

- **routers/** -- API endpoint'leri. auth, upload, analysis, reports, dashboard
  olmak uzere 5 ayri router var.

- **services/** -- ve burasi projenin en onemli kismi. Is mantigi burada.
  Analiz motoru, NLP yorum uretici, grafik servisi, rapor servisi, workflow
  servisi..."

---

## BOLUM 3 - ANALIZ MOTORU (5-6 dk)
**Ekranda: backend/app/services/analysis_service.py**

"Simdi analizin beynini gorelim. analysis_service.py dosyasini aciyorum.

*(dosyayi ac, run_full_analysis metodunu goster)*

Bu AnalysisService sinifi, tum istatistiksel analizi yapiyor. run_full_analysis
metodu cagirildiginda neler oluyor sirayla gorelim:

Oncelikle veriyi sayisal ve kategorik olarak ayiriyor. Sonra sirayla:

1. **_basic_statistics** -- ortalama, medyan, standart sapma, carpiklik, basiklik,
   degisim katsayisi hesapliyor. Her sayisal sutun icin ayri ayri.

2. **_correlation_analysis** -- Pearson korelasyon matrisi cikariyor. r degeri 0.7'den
   buyuk olanlari 'guclu korelasyon' olarak isaretiyor.

3. **_missing_data_analysis** -- eksik veri oranini hesapliyor. Her sutun icin eksik
   sayisi, yuzde ve siddet seviyesi (dusuk/orta/yuksek) belirliyor.

4. **_distribution_analysis** -- normallik testi yapiyor (scipy normaltest).
   Carpiklik yonunu ve basiklik tipini belirliyor.

5. **_trend_analysis** -- lineer regresyon ile trend tespit ediyor. Egim, R-kare
   ve p-degeri hesaplayarak trendin anlamli olup olmadigini belirliyor.

6. **_anomaly_detection** -- iki yontem kullaniyorum. IQR yontemi ile klasik
   aykiri deger tespiti, bir de scikit-learn'den Isolation Forest ile cok
   degiskenli anomali algilama.

7. **_data_quality_score** -- veri kalitesini 0-100 arasinda puanliyor. Tamlik,
   teklik ve tutarlilik kriterlerine bakiyor. A-B-C-D gibi not veriyor.

Bu kadar cok analiz islemi, tek bir fonksiyon cagrisiyla otomatik calisiyor.
Kullanici hicbir parametre secmek zorunda degil."

---

## BOLUM 4 - NLP / AI YORUM MOTORU (5-6 dk)
**Ekranda: backend/app/services/nlp_service.py**

"Simdi projenin bence en etkileyici kismina gelelim. nlp_service.py dosyasi.

*(dosyayi ac, _init_templates metodunu goster)*

Bu NLPCommentGenerator sinifi, harici AI API kullanmadan dinamik yorum uretiyor.
Nasil calisiyor anlatayim:

Sinif icinde yuzlerce Turkce sablon var. Mesela su trend sablonlarina bakin:

*(TREND_UP listesini goster)*

Gordugunuz gibi 4 farkli sablon var artis trendi icin. Her birinde {col}, {slope},
{change} gibi degiskenler var. Sistem analiz sonuclarina bakiyor: mesela satis_miktari
sutununda yukselis trendi var, eğim 0.45, degisim %23 diyelim. Bu bilgileri aliyor,
random.choice ile sablonlardan birini seciyor ve degiskenleri dolduruyor.

Sonuc: 'satis_miktari degiskeninde belirgin bir yukselis trendi gozlemlenmektedir
(egim: 0.45, R-kare: 0.82)' gibi dogal bir cumle cikiyor.

*(generate_executive_summary metodunu goster)*

Yonetici ozeti olusturmaya bakin: sistem once genel bir giris cumlesi seciyor, sonra
veri kalitesine bakip bir yorum ekliyor, trendleri, anomalileri, korelasyonlari
siraliyor. Her birini ayri sablonlardan uretiyor.

Onemli nokta: her calistirildiginda random.choice yuzunden farkli sablonlar seciliyor.
Yani ayni veriyi iki kez analiz etseniz bile biraz farkli yorumlar gorursunuz. Bu da
sisteme gercek bir AI hissi veriyor.

*(generate_recommendations metodunu goster)*

Oneriler kismi da ayni mantikla calisiyor. Eksik veri yuksekse veri tamamlama onerisi,
anomali varsa inceleme onerisi, trend dususu varsa acil mudahale onerisi... Her biri
kurallarla tetikleniyor ve ilgili sablondan uretiliyor."

---

## BOLUM 5 - RAPOR URETIMI (3-4 dk)
**Ekranda: backend/app/services/report_service.py**

"Rapor servisi iki format destekliyor: PDF ve DOCX.

*(generate_pdf metodunu goster)*

PDF icin ReportLab kutuphanesini kullaniyorum. Profesyonel bir rapor yapisi
olusturdum: kapak sayfasi, icindekiler, yonetici ozeti, veri tabloları,
grafikler, trendler, anomaliler, AI yorumlari, oneriler ve sonuc.

Her bolum icin ozel stiller tanimladim -- baslik renkleri, tablo stilleri,
arka plan renkleri. Raporun gorunumu gercekten profesyonel.

*(generate_docx metodunu goster)*

DOCX icin python-docx kullaniyorum. Ayni icerik yapisi Word formatinda.
Tablolar, basliklar, grafikler hepsi mevcut."

---

## BOLUM 6 - FRONTEND DEMO (5-7 dk)
**Ekranda: Tarayici, http://localhost:3000**

"Simdi sistemi canli olarak gorelim. Tarayicida localhost:3000'i aciyorum.

*(giris sayfasini goster)*

Gordugunuz gibi modern bir giris sayfasi. Sol tarafta sistemin ozellikleri,
sag tarafta giris formu. Dark mode, glassmorphism tasarim.

*(kayit ol veya giris yap)*

Giris yaptiktan sonra dashboard'a yonlendirildim.

*(dashboard'i goster)*

Dashboard'da istatistik kartlari goruyorsunuz: toplam veri seti, rapor sayisi,
analiz edilen satir sayisi, ortalama kalite skoru. Altta son yuklenen dosyalar
ve raporlar listeleniyor.

*(Veri Yukle sayfasina git)*

Simdi asil demoyu yapalim. Veri Yukle sayfasina geciyorum. Burada drag & drop
alani var.

*(ornek CSV dosyasini surukleyip birak)*

Satis verisi CSV'mizi surukleyip birakiyorum... Yuklendi! Gordugunuz gibi
dosya bilgileri geldi: 30 satir, 10 sutun. Sutun bilgileri ve veri on izlemesi
gorunuyor.

*(AI Analiz Baslat butonuna tikla)*

Simdi 'AI Analiz Baslat' butonuna tikliyorum...

*(workflow animasyonunu goster)*

Bakin, her adim tek tek ilerliyor: Dosya Dogrulama, Veri Ayristirma,
Istatistiksel Analiz, Trend Tespiti, Anomali Algilama, AI Yorum Uretimi,
Grafik Olusturma, Veritabani Kayit... Hepsi tamamlandi!

*(sonuclari goster)*

Sonuclara bakalim. En ustte AI'in yazdigi Yonetici Ozeti var. Bunu okuyun,
gercekten insan yazimi gibi gorunuyor. Veri setinin boyutunu, kalite skorunu,
trend bilgilerini, anomalileri ozetlemis.

*(trend yorumlarini goster)*

Asagida trend yorumlari var. Her sutun icin artis mi dusus mu, istatistiksel
olarak anlamli mi, ne kadar degismis -- hepsini dogal dilde anlatmis.

*(onerileri goster)*

AI onerileri bolumine bakin: eksik veri varsa ne yapilmali, anomaliler nasil
ele alinmali, hangi korelasyonlara dikkat edilmeli... Hepsi otomatik uretilmis.

*(PDF Indir butonuna tikla)*

Simdi PDF raporumuzu indirelim... Indi! Acalim:

*(PDF'i ac ve sayfalarini goster)*

Bakin: kapak sayfasi, icindekiler, yonetici ozeti, veri genel bakis tablosu,
istatistik tablolari, grafikler -- dagilim, korelasyon matrisi, kutu grafikleri,
trend grafikleri... AI yorumlari, oneriler ve sonuc. Tam profesyonel bir rapor."

---

## BOLUM 7 - VERITABANI VE DOCKER (3-4 dk)
**Ekranda: database/init.sql veya pgAdmin/DBeaver**

"Veritabani tarafina hizlica bakalim. PostgreSQL kullaniyorum. 5 tablo var:

- users: kullanici hesaplari
- datasets: yuklenen veri setleri
- analytics_results: analiz sonuclari (JSONB formatinda)
- reports: olusturulan raporlar
- workflow_logs: workflow izleme loglari

Tablolar arasinda foreign key iliskileri var. Cascade delete tanimli, yani
bir kullanici silinirse onunla iliskili tum veriler de temizlenir.

*(docker-compose.yml goster)*

Docker Compose ile tek komutla her seyi baslatabilirim:
docker-compose up -d

4 container ayaga kalkiyor: PostgreSQL, Backend, Frontend ve n8n."

---

## BOLUM 8 - N8N WORKFLOW (2-3 dk)
**Ekranda: n8n arayuzu veya workflow JSON**

"n8n otomasyon arayuzune bakalim. localhost:5678'de calisiyor.

workflows/ klasorundeki JSON dosyasini import ettim. Workflow soyle calisiyor:

1. Webhook tetiklenir (bir veri seti ID'si gelir)
2. Dataset bilgisi cekilir
3. Dogrulama yapilir
4. Analiz endpointi cagirilir
5. PDF ve DOCX raporlari paralel olusturulur
6. Sonuc webhook'a doner

Backend icinde de bunun bir yansimasi var: WorkflowService her adimi canli
olarak logluyor. Frontend'de kullanici bu adimlari animasyonlu olarak goruyor."

---

## BOLUM 9 - KAPATIS (2-3 dk)
**Ekranda: Genel bakis veya VS Code**

"Ozetleyecek olursam: bu sistem harici AI API'ye ihtiyac duymadan, kural
tabanli bir zeka motoru ile veri analizi ve rapor uretimi yapiyor.

Teknik acidan neler basardik:
- 7 farkli istatistiksel analiz turu
- 300'den fazla Turkce sablon ile dinamik yorum uretimi
- Profesyonel PDF ve DOCX rapor ciktisi
- Modern React/Next.js dashboard
- PostgreSQL ile veri yonetimi
- Docker ile kolay kurulum
- n8n ile workflow otomasyonu

Projenin en guclu yani: farkli veri setleri yukleyin, farkli yorumlar
gorursunuz. Sabit metin degil, veriye ozel, dinamik ve dogal yorumlar.

Sistem, gercek dunyada bir SaaS urunu olarak kullanilabilecek olgunlukta.
Guvenlik, performans ve kullanici deneyimi acisindan production seviyesinde.

Izlediginiz icin tesekkurler."

---

## DEMO SENARYOSU - ADIM ADIM

| Sira | Ekran | Sure | Anlatim |
|------|-------|------|---------|
| 1 | Masaustu | 30sn | Giris, projenin ne oldugunu anlat |
| 2 | VS Code - proje klasoru | 2dk | Dosya yapisini gez |
| 3 | VS Code - backend/app/ | 2dk | Backend yapisini anlat |
| 4 | VS Code - analysis_service.py | 3dk | Analiz motorunu acikla |
| 5 | VS Code - nlp_service.py | 4dk | NLP/AI yorum motorunu goster |
| 6 | VS Code - report_service.py | 2dk | Rapor uretimini anlat |
| 7 | Tarayici - giris sayfasi | 1dk | Giris yap |
| 8 | Tarayici - dashboard | 1dk | Dashboard'i goster |
| 9 | Tarayici - veri yukle | 1dk | CSV yukle |
| 10 | Tarayici - on izleme | 1dk | Veri on izlemeyi goster |
| 11 | Tarayici - analiz | 2dk | AI analizi calistir, animasyonu goster |
| 12 | Tarayici - sonuclar | 3dk | AI yorumlarini, onerileri goster |
| 13 | PDF rapor | 2dk | Indirilen raporu ac, sayfalari gez |
| 14 | VS Code - docker-compose.yml | 1dk | Docker yapisini anlat |
| 15 | VS Code - init.sql | 1dk | Veritabani semAsini goster |
| 16 | n8n arayuzu | 1dk | Workflow'u goster |
| 17 | Masaustu | 1dk | Ozet ve kapatis |

## ANLATIM IPUCLARI

- Hizli konusmayin, her bolumde biraz duraklatin
- Kodda bir seyi gosterirken imleci o satira goturun
- "Burada su oluyor" yerine "Simdi dikkat edin, bu kisim onemli" gibi doğal gecisler kullanin
- Her bolum sonunda bir ozet cumle soyeyin
- Demo sirasinda hata olursa paniik yapmayin, "canli demoda boyle seyler olur" deyin
- PDF raporu actiginizda sayfalari yavas yavas gecin, her bolumu isaret edin
- NLP motorunu anlatirken "bu proje GPT kullanmiyor" vurgusunu en az 2 kez yapin
