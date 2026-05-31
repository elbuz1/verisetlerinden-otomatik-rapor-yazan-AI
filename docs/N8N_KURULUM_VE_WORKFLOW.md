# n8n DETAYLI KURULUM VE WORKFLOW OLUSTURMA REHBERI

## n8n Nedir?

n8n, tarayici uzerinden calisan gorsel bir otomasyon aracidir. Programlama bilmeden
bile node'lari (dugumler) surukleyip birakarak, aralarinda baglantilar cizerek
otomasyon akislari olusturabilirsin.

Her node bir is yapar:
- Webhook Node: Dis sistemlerden istek alir
- HTTP Request Node: API cagrilari yapar
- IF Node: Kosul kontrol eder
- Set Node: Veri hazirlar
- Function Node: JavaScript kodu calistirir

## Bu Projede n8n'in Rolu

ONEMLI: n8n bu projede OPSIYONEL bir katmandir. Sistem n8n OLMADAN da calisiyor.

Backend icindeki WorkflowService (workflow_service.py) zaten n8n'in yaptigini
yapan dahili bir pipeline motoru. Her analiz adimini logluyor ve frontend'e
raporluyor.

n8n'in eklenmesinin amaci:
1. Gorsel workflow gosterimi (sunumda cok iyi gorununr)
2. Ek otomasyonlar (ornegin: her yukleme sonrasi otomatik analiz)
3. Production ortaminda zamanlama ve tetikleme

## n8n Nasil Kurulur?

### Yontem 1: npm ile (Onerilen - Docker gerektirmez)

```bash
# Global olarak kur
npm install -g n8n

# Baslat
n8n start

# Tarayicida ac: http://localhost:5678
```

### Yontem 2: npx ile (Kurulum gerektirmez)

```bash
npx n8n
# Tarayicida ac: http://localhost:5678
```

### Yontem 3: Docker ile

```bash
docker run -d --name n8n -p 5678:5678 n8nio/n8n
```

## GORSEL WORKFLOW OLUSTURMA - ADIM ADIM

n8n acildiktan sonra tarayicida http://localhost:5678 adresine git.
Asagidaki adimlari takip ederek workflow'u GORSEL olarak olustur:

### ADIM 1: Yeni Workflow Olustur
- Sag ustte "New Workflow" butonuna tikla
- Isim ver: "AI Rapor - Veri Analizi Workflow"

### ADIM 2: Webhook Trigger Node Ekle
- Sol menude veya + butonuyla "Webhook" ara
- Webhook node'unu calisma alanina surekle
- Ayarlar:
  - HTTP Method: POST
  - Path: analyze
  - Response Mode: "Using Respond to Webhook Node"
- Bu node, dis sistemlerden gelen istekleri alacak

### ADIM 3: HTTP Request Node Ekle - "Veri Seti Bilgisi Al"
- + butonuyla "HTTP Request" node'u ekle
- Webhook'tan bu node'a bir cizgi cek (baglanti olustur)
- Ayarlar:
  - Method: GET
  - URL: http://localhost:8000/api/upload/datasets/{{ $json.dataset_id }}
  - Bu backend'den veri seti bilgilerini ceker

### ADIM 4: IF Node Ekle - "Veri Seti Dogrula"
- "IF" node'u ekle
- Onceki node'dan baglanti cek
- Ayarlar:
  - Condition: {{ $json.status }} is not empty
  - True: sonraki adima gider
  - False: hata yanitina gider

### ADIM 5: HTTP Request Node - "Analiz Calistir"
- Yeni HTTP Request node'u ekle
- IF node'unun TRUE ciktisindan baglanti cek
- Ayarlar:
  - Method: POST
  - URL: http://localhost:8000/api/analysis/{{ $json.id }}
  - Timeout: 120000 (2 dakika - analiz uzun surebilir)

### ADIM 6: HTTP Request Node - "PDF Rapor Olustur"
- Yeni HTTP Request node'u ekle
- Analiz node'undan baglanti cek
- Ayarlar:
  - Method: POST
  - URL: http://localhost:8000/api/reports/generate/{{ $json.dataset_id }}?format=pdf

### ADIM 7: HTTP Request Node - "DOCX Rapor Olustur"
- Yeni HTTP Request node'u ekle
- Analiz node'undan AYNI baglanti cek (paralel calisacak)
- Ayarlar:
  - Method: POST
  - URL: http://localhost:8000/api/reports/generate/{{ $json.dataset_id }}?format=docx

### ADIM 8: Set Node - "Yanit Hazirla"
- Set node'u ekle
- Her iki rapor node'undan baglanti cek
- Ayarlar:
  - status: "completed"
  - message: "Analiz ve rapor olusturma tamamlandi"

### ADIM 9: Respond to Webhook Node
- "Respond to Webhook" node'u ekle
- Set node'undan baglanti cek
- Ayarlar:
  - Respond With: JSON
  - Response Body: {{ JSON.stringify($json) }}

### ADIM 10: Hata Yaniti (IF False yolu)
- Baska bir "Respond to Webhook" node'u ekle
- IF node'unun FALSE ciktisindan baglanti cek
- Ayarlar:
  - Response Code: 400
  - Response Body: {"status": "error", "message": "Veri seti bulunamadi"}

### ADIM 11: Kaydet ve Aktif Et
- Sag ustte "Save" butonuna tikla
- "Active" toggle'ini ac

## SONUC GORUNUMU

Workflow gorsel olarak soyle gorunecek:

```
[Webhook] --> [Veri Seti Bilgisi Al] --> [IF Dogrula]
                                              |
                                         TRUE | FALSE
                                              |      |
                                    [Analiz Calistir] [Hata Yaniti]
                                         |
                                    /         \
                              [PDF Olustur] [DOCX Olustur]
                                    \         /
                                   [Yanit Hazirla]
                                         |
                                   [Webhook Yanit]
```

## WORKFLOW JSON IMPORT (ALTERNATIF)

Gorsel olusturmak yerine hazir JSON'u import etmek istersen:
1. n8n arayuzunde sol menude "Workflows" tikla
2. Sag ustte 3 nokta menusune tikla
3. "Import from File" sec
4. workflows/n8n-data-analysis-workflow.json dosyasini sec
5. Import'u onayla
6. Aktif et

## WORKFLOW'U TEST ETME

1. n8n'de workflow'u ac
2. Webhook node'una tikla
3. "Test URL"yi kopyala (ornek: http://localhost:5678/webhook-test/analyze)
4. Terminal'den test et:

```bash
curl -X POST http://localhost:5678/webhook-test/analyze \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 1}'
```

## ONEMLI NOTLAR

- n8n olmadan da sistem calisir (WorkflowService backend'de dahili)
- n8n sadece ek otomasyon ve gorsel gosterim icin
- Sunumda n8n arayuzunu gostermek cok etkileyici olur
- Workflow'u olustururken her node'u tiklayip ayarlarini yapmani unutma
- Node'lar arasi baglanti cizmek icin bir node'un sag tarafindaki
  noktayi tutup diger node'un sol noktasina cek
