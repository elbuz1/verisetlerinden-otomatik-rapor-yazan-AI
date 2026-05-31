# n8n Dışarıdan Yapılandırma ve Bağlantı Rehberi

## Genel Mimari

```
┌─────────────────────────────────────────────────────────────────────┐
│                         KULLANICI                                     │
│                    (Dosya Yükler)                                     │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────┐     ┌──────────────────────────────────┐
│    FRONTEND (Next.js)       │     │         n8n (Port 5678)          │
│    http://localhost:3000    │     │    Görsel Workflow Editörü        │
│                             │     │                                  │
│  "Analiz Başlat" butonu ────┼────►│  Webhook Trigger                 │
│                             │     │       │                          │
└─────────────────────────────┘     │       ▼                          │
                                    │  1. Workflow Başlat               │
┌─────────────────────────────┐     │       │                          │
│   BACKEND (FastAPI)         │◄────┤       ▼                          │
│   http://localhost:8000     │     │  2. Veri Parse Et                │
│                             │     │       │                          │
│  /api/n8n/trigger          │◄────┤       ▼                          │
│  /api/n8n/parse-data       │◄────┤  3. İstatistiksel Analiz         │
│  /api/n8n/run-analysis     │◄────┤       │                          │
│  /api/n8n/generate-comments│◄────┤       ▼                          │
│  /api/n8n/generate-charts  │◄────┤  4. AI Yorum Üret                │
│  /api/n8n/generate-report  ��◄────┤       │                          │
│  /api/n8n/complete         │◄────┤       ▼                          │
│                             │     │  5. Grafik Oluştur               │
└─────────────────────────────┘     │       │                          │
                                    │       ▼                          │
                                    │  6. Rapor Oluştur                │
                                    │       │                          │
                                    │       ▼                          │
                                    │  7. Tamamla → Webhook Yanıtı     │
                                    └──────────────────────────────────┘
```

## 1. n8n Kurulumu

```bash
# Global olarak kur
npm install -g n8n

# Versiyonu kontrol et
n8n --version
```

## 2. n8n'i Başlat

```bash
n8n start
```

Tarayıcıda `http://localhost:5678` adresini aç.

**İlk açılışta:**
- E-posta ve şifre ile bir owner hesabı oluşturman istenecek
- Bu bilgileri gir ve devam et

## 3. Workflow'u n8n'e İçe Aktar (Import)

### Yöntem A: CLI ile (Otomatik - Zaten Yapıldı)
```bash
n8n import:workflow --input="n8n-workflow/data-analysis-workflow.json"
n8n publish:workflow --id=1
```

### Yöntem B: n8n Arayüzünden (Manuel)
1. n8n editörüne git: `http://localhost:5678`
2. Sol menüden **"Workflows"** tıkla
3. Sağ üst köşeden **"..."** → **"Import from File"** tıkla
4. `n8n-workflow/data-analysis-workflow.json` dosyasını seç
5. Import edildikten sonra sağ üstteki **"Inactive"** toggle'ını **"Active"** yap

## 4. n8n'de Workflow'u Görsel Olarak Yapılandırma

n8n editöründe (`http://localhost:5678`) workflow'u açtığında şu node'ları göreceksin:

### Node 1: Webhook Trigger
- **Tür:** Webhook
- **HTTP Method:** POST
- **Path:** `data-analysis`
- **Webhook URL:** `http://localhost:5678/webhook/data-analysis`
- Bu URL'e POST request geldiğinde workflow başlar

### Node 2: 1. Workflow Başlat
- **Tür:** HTTP Request
- **Method:** POST
- **URL:** `http://localhost:8000/api/n8n/trigger`
- **Body:** `{ "dataset_id": {{$json.body.dataset_id}}, "user_id": {{$json.body.user_id}}, "format": "{{$json.body.format}}" }`
- Backend'de workflow kaydı oluşturur

### Node 3: 2. Veri Parse Et
- **Tür:** HTTP Request
- **Method:** POST
- **URL:** `http://localhost:8000/api/n8n/parse-data`
- **Body:** `{ "dataset_id": {{$json.dataset_id}}, "workflow_id": {{$json.workflow_id}} }`
- CSV/Excel/JSON dosyasını parse eder

### Node 4: 3. İstatistiksel Analiz
- **Tür:** HTTP Request
- **Method:** POST
- **URL:** `http://localhost:8000/api/n8n/run-analysis`
- **Body:** `{ "dataset_id": {{$json.dataset_id}}, "workflow_id": {{$json.workflow_id}} }`
- Ortalama, medyan, standart sapma, korelasyon, trend, anomali hesaplar

### Node 5: 4. AI Yorum Üret
- **Tür:** HTTP Request
- **Method:** POST
- **URL:** `http://localhost:8000/api/n8n/generate-comments`
- **Body:** `{ "dataset_id": {{$json.dataset_id}}, "workflow_id": {{$json.workflow_id}} }`
- 300+ Türkçe şablondan dinamik yorumlar üretir (harici API YOK)

### Node 6: 5. Grafik Oluştur
- **Tür:** HTTP Request
- **Method:** POST
- **URL:** `http://localhost:8000/api/n8n/generate-charts`
- **Body:** `{ "dataset_id": {{$json.dataset_id}}, "workflow_id": {{$json.workflow_id}} }`
- 8 farklı grafik tipi üretir

### Node 7: 6. Rapor Oluştur
- **Tür:** HTTP Request
- **Method:** POST
- **URL:** `http://localhost:8000/api/n8n/generate-report`
- **Body:** `{ "dataset_id": {{$json.dataset_id}}, "user_id": {{$json.user_id}}, "format": "pdf", "workflow_id": {{$json.workflow_id}} }`
- PDF veya DOCX rapor üretir

### Node 8: 7. Tamamla
- **Tür:** HTTP Request
- **Method:** POST
- **URL:** `http://localhost:8000/api/n8n/complete`
- **Body:** `{ "dataset_id": {{$json.dataset_id}}, "workflow_id": {{$json.workflow_id}} }`
- Workflow'u tamamlandı olarak işaretler

### Node 9: Webhook Yanıtı
- **Tür:** Respond to Webhook
- İstemciye sonucu döner

## 5. Bağlantıları (Connections) Oluşturma

n8n editöründe her node'un sağ tarafındaki çıkış noktasını (●) tutup bir sonraki node'un sol tarafındaki giriş noktasına (●) sürükle:

```
Webhook Trigger ──→ 1. Workflow Başlat ──→ 2. Veri Parse Et ──→ 
3. İstatistiksel Analiz ──→ 4. AI Yorum Üret ──→ 5. Grafik Oluştur ──→ 
6. Rapor Oluştur ──→ 7. Tamamla ──→ Webhook Yanıtı
```

## 6. Workflow'u Aktif Et

- Sağ üst köşedeki toggle'ı **Active** yap
- "Workflow has been activated" mesajını gör

## 7. Test Et

### Terminal'den test:
```bash
curl -X POST http://localhost:5678/webhook/data-analysis \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 1, "user_id": 1, "format": "pdf"}'
```

### PowerShell'den test:
```powershell
$body = '{"dataset_id": 1, "user_id": 1, "format": "pdf"}'
Invoke-RestMethod -Uri "http://localhost:5678/webhook/data-analysis" -Method POST -Body $body -ContentType "application/json"
```

### n8n Editöründen test:
1. Workflow'u aç
2. Sol üstte "Test workflow" butonuna bas
3. Webhook node'una tıkla → "Test" tab → "Listen for test event" → 
4. Başka bir terminalde yukarıdaki curl/PowerShell komutunu çalıştır
5. n8n'de verilerin node'dan node'a aktığını göreceksin

## 8. Backend Bağlantı Kontrolü

```bash
# n8n'in backend'e erişebildiğini doğrula:
curl http://localhost:8000/api/n8n/health
```

Beklenen yanıt:
```json
{
  "status": "healthy",
  "service": "AI Rapor Sistemi Backend",
  "n8n_integration": "active",
  "available_endpoints": [...]
}
```

## 9. n8n Arayüzünde Ne Göreceksin

n8n editöründe (`http://localhost:5678`):

1. **Canvas (Tuval):** Node'ları ve bağlantıları görsel olarak görürsün
2. **Execution Log:** Her çalışma kaydedilir (sol menü → "Executions")
3. **Her Node'un Çıktısı:** Node'a tıklayınca girdi/çıktı JSON'ını görürsün
4. **Hata Takibi:** Bir node hata verirse kırmızı olur ve hata mesajı görünür

## 10. Sunumda Gösterilecekler

1. **n8n Editörü:** Workflow'un görsel halini göster (node'lar ve bağlantılar)
2. **Test Çalıştırma:** "Test workflow" ile canlı çalıştır
3. **Execution Log:** Başarılı çalışma logunu göster
4. **Her Node'un Çıktısı:** Veri akışını göster (parsing → analiz → yorum → rapor)
5. **Backend Logları:** n8n'den gelen isteklerin backend'e ulaştığını göster

## Hızlı Başlatma Komutu

```bash
# 1. Terminal: Backend
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# 2. Terminal: n8n
n8n start

# 3. Terminal: Frontend
cd frontend
npm run dev
```

Üç servis de çalıştıktan sonra:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- n8n Editörü: http://localhost:5678
