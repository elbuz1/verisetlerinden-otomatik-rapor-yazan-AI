# KURULUM REHBERI - Adim Adim

## YONTEM 1: Docker ile Kurulum (Onerilen)

### Gereksinimler
- Docker Desktop (Windows/Mac) veya Docker Engine (Linux)
- Docker Compose v2+
- Minimum 4GB RAM

### Adimlar

```bash
# 1. Proje klasorune girin
cd verisetlerinden_otomatikraporyazanAI

# 2. .env dosyasini olusturun
cp .env.example .env
# (Windows: copy .env.example .env)

# 3. Docker container'lari baslatin
docker-compose up -d

# 4. Container durumlarini kontrol edin
docker-compose ps

# 5. Loglari izleyin (hata varsa gormek icin)
docker-compose logs -f backend
```

### Erisim Adresleri
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- n8n Dashboard: http://localhost:5678 (kullanici: admin, sifre: admin123)

### Durdurma ve Temizleme
```bash
# Container'lari durdurun
docker-compose down

# Verileri de silmek icin
docker-compose down -v
```

---

## YONTEM 2: Manuel Kurulum

### 1. PostgreSQL Kurulumu

```bash
# PostgreSQL 16 kurun (isletim sisteminize gore)
# Windows: https://www.postgresql.org/download/windows/
# Mac: brew install postgresql@16
# Linux: sudo apt install postgresql-16

# PostgreSQL servisini baslatin
# Windows: Otomatik baslar
# Mac: brew services start postgresql@16
# Linux: sudo systemctl start postgresql

# Veritabanini olusturun
psql -U postgres
CREATE DATABASE ai_rapor_db;
\q

# Semalari yukleyin
psql -U postgres -d ai_rapor_db -f database/init.sql
```

### 2. Backend Kurulumu

```bash
cd backend

# Python virtual environment olusturun
python -m venv venv

# Aktif edin
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Bagimliliklari kurun
pip install -r requirements.txt

# .env dosyasini olusturun/duzenleyin
# DATABASE_URL, SECRET_KEY vb. degerlerini ayarlayin

# Sunucuyu baslatin
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend basladiginda:
- http://localhost:8000 -> API root
- http://localhost:8000/docs -> Swagger UI
- http://localhost:8000/health -> Health check

### 3. Frontend Kurulumu

```bash
cd frontend

# Node.js 18+ gerekli
node --version

# Bagimliliklari kurun
npm install

# Gelistirme sunucusunu baslatin
npm run dev
```

Frontend: http://localhost:3000

### 4. n8n Kurulumu (Opsiyonel)

```bash
# Global kurulum
npm install -g n8n

# Baslatin
n8n start

# veya Docker ile
docker run -d --name n8n -p 5678:5678 n8nio/n8n
```

n8n arayuzune girin (http://localhost:5678) ve workflow'u import edin:
1. Sol menude "Workflows" tiklayin
2. "Import from File" secin
3. `workflows/n8n-data-analysis-workflow.json` dosyasini secin
4. "Import" tiklayin

---

## SORUN GIDERME

### "Database connection refused" hatasi
- PostgreSQL servisinin calistigindan emin olun
- .env dosyasindaki DATABASE_URL'i kontrol edin
- Port 5432'nin baska bir uygulama tarafindan kullanilmadigini kontrol edin

### "Module not found" hatasi (Backend)
- Virtual environment aktif mi kontrol edin
- `pip install -r requirements.txt` tekrar calistirin

### "CORS error" (Frontend)
- Backend'in calistigindan emin olun
- config.py'deki CORS_ORIGINS listesinde http://localhost:3000 oldugundan emin olun

### Docker "port already in use" hatasi
- `docker-compose down` ile mevcut container'lari durdurun
- Veya docker-compose.yml'deki portlari degistirin

### Upload hatasi
- uploads/ klasorunun var oldugundan emin olun
- Dosya boyutunun 100MB'i gecmedigini kontrol edin
- Desteklenen format: CSV, XLSX, XLS, JSON
