# Travel Agent — AI-Powered Travel Planning Assistant

LangGraph tabanlı çok adımlı AI agent uygulaması / LangGraph-based multi-step AI agent application

---

<details>
<summary>🇹🇷 Türkçe</summary>

## Proje Hakkında

Travel Agent, kullanıcının doğal dil ile seyahat taleplerini ilettiği ve AI agent'ın adım adım uçuş → otel → transfer sürecini yönettiği bir uygulamadır. Her aşamada kullanıcıdan onay alınır; seçimler bir sonraki aşamaya otomatik taşınır.

### Hedef Kitle

- Seyahat planlamayı tek bir arayüzden yapmak isteyen bireysel kullanıcılar
- Uçuş + konaklama + transfer kombosunu karşılaştırmalı görmek isteyen gezginler
- AI agent mimarilerini öğrenmek isteyen geliştiriciler

---

## Mimari

```
┌─────────────────────┐        ┌──────────────────────────────────────┐
│   Frontend          │        │   Backend                            │
│   React + Vite      │◄──────►│   FastAPI                            │
│   Railway'de host   │        │   └── LangGraph Agent                │
└─────────────────────┘        │        ├── search_flights (SerpAPI)  │
                                │        ├── search_hotels  (SerpAPI)  │
                                │        └── search_transport(SerpAPI) │
                                │   LLM: Cerebras (Qwen-3-235B)        │
                                │   Tracing: LangSmith                 │
                                │   Testing: DeepEval + Groq judge     │
                                └──────────────────────────────────────┘
```

### Agent Akışı

```
Kullanıcı Mesajı
      │
      ▼
  orchestrator  ──► tools (SerpAPI arama)
      │                    │
      ▼                    ▼
   approval  ◄──── sonuçları listele
  (kullanıcı seçim yapar)
      │
      ▼
  phase: flight → hotel → transport → done
      │
      ▼
  summary_node (seyahat özeti)
```

---

## Teknoloji Stack

| Katman | Teknoloji |
|---|---|
| Frontend | React 19, Vite 5 |
| Backend | FastAPI, Uvicorn |
| Agent Framework | LangGraph |
| LLM | Cerebras Cloud (Qwen-3-235B) |
| Arama | SerpAPI (Google Flights, Hotels, Maps) |
| Observability | LangSmith |
| Evaluation | DeepEval + Confident AI |
| Deploy | Railway (backend + frontend ayrı servis) |

---

## Klasör Yapısı

```
TravelAgent/
├── backend/
│   ├── main.py              # FastAPI uygulama, endpoint'ler
│   ├── railway.toml         # Railway deploy konfigürasyonu
│   ├── requirements.txt     # Python bağımlılıkları
│   ├── .env                 # API key'ler (git'e gitmez)
│   ├── agent/
│   │   ├── graph.py         # LangGraph agent tanımı
│   │   ├── state.py         # Pydantic model'ler (FlightOption, HotelOption...)
│   │   └── tools/
│   │       ├── flights.py   # Uçuş arama tool'u
│   │       ├── hotels.py    # Otel arama tool'u
│   │       └── transport.py # Transfer arama tool'u
│   └── tests/
│       └── test_example.py  # DeepEval test dosyası
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Ana uygulama, API entegrasyonu
│   │   └── components/      # TravelForm, FlightCards, HotelCards, SummaryCard
│   ├── railway.toml         # Railway static site konfigürasyonu
│   └── package.json
└── .gitignore
```

---

## Kurulum — Local Geliştirme

### Gereksinimler

- Python 3.11+
- Node.js 20+
- Git

### 1. Repoyu Klonla

```bash
git clone https://github.com/AE1024/Travel-Agent.git
cd Travel-Agent
```

### 2. Backend Kurulumu

```bash
# Sanal ortam oluştur
python -m venv agent_v

# Aktive et (Windows)
agent_v\Scripts\Activate.ps1

# Aktive et (macOS/Linux)
source agent_v/bin/activate

# Bağımlılıkları yükle
cd backend
pip install -r requirements.txt
```

### 3. Environment Variables

`backend/.env` dosyası oluştur:

```env
# Zorunlu
SERPAPI_KEY      = your_serpapi_key
CEREBRAS_API_KEY = your_cerebras_key

# LangSmith (opsiyonel — tracing için)
LANGCHAIN_TRACING_V2 = true
LANGCHAIN_API_KEY    = your_langsmith_key
LANGCHAIN_PROJECT    = travel-agent

# DeepEval (opsiyonel — testler için)
CONFIDENT_API_KEY = your_confident_ai_key
GROQ_API_KEY      = your_groq_key
```

**API Key Alma:**

| Servis | URL |
|---|---|
| SerpAPI | https://serpapi.com |
| Cerebras | https://cloud.cerebras.ai |
| LangSmith | https://smith.langchain.com |
| Confident AI | https://app.confident-ai.com |
| Groq | https://console.groq.com |

### 4. Backend'i Başlat

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API dökümantasyonu: http://localhost:8000/docs

### 5. Frontend Kurulumu

```bash
cd frontend
npm install
npm run dev
```

Uygulama: http://localhost:5173

---

## Kullanım

1. Tarayıcıda uygulamayı aç
2. Seyahat formunu doldur: nereden, nereye, tarih, kişi sayısı
3. AI agent uçuşları listeler → bir uçuş seç
4. Agent kaç gece kalacağını sorar → otel tercihlerini belirt
5. Agent otelleri listeler → bir otel seç
6. Agent transfer seçeneklerini listeler → seç veya atla
7. Seyahat özeti ve rezervasyon linkleri gösterilir

---

## API Endpoint'leri

| Method | Endpoint | Açıklama |
|---|---|---|
| GET | `/health` | Servis sağlık kontrolü |
| POST | `/chat` | Agent ile sohbet |
| POST | `/search-flights` | Direkt uçuş arama |
| POST | `/search-hotels` | Direkt otel arama |

---

## Testleri Çalıştırma

```bash
cd backend
deepeval test run tests/test_example.py
```

**Test Kapsamı:**
- IATA kodu doğruluğu (IST, CDG, LHR, JFK...)
- Faz geçişleri (uçuş → otel → transfer)
- Eksik bilgi yönetimi
- Konu dışı sorgu reddi
- Geçmiş tarih reddi

---

## Deploy — Railway

| Servis | Root Dir | URL |
|---|---|---|
| Backend (FastAPI) | `backend/` | `travel-agent-production-d4c2.up.railway.app` |
| Frontend (React) | `frontend/` | `delightful-vitality-production-149d.up.railway.app` |

### Backend Variables (Railway)

```
CEREBRAS_API_KEY
SERPAPI_KEY
LANGCHAIN_TRACING_V2 = true
LANGCHAIN_API_KEY
LANGCHAIN_PROJECT    = travel-agent
```

### Frontend Variables (Railway)

```
VITE_API_URL = https://travel-agent-production-d4c2.up.railway.app
```

### Yeniden Deploy

```bash
git add .
git commit -m "feat: açıklama"
git push origin main
```

---

## Observability — LangSmith

- **Dashboard:** https://smith.langchain.com
- **Proje:** `travel-agent`
- Görüntülenenler: tool çağrıları, token sayıları, latency, hata ayıklama

---

## Geliştirme Notları

- Agent `MemorySaver` kullanır — her `thread_id` bağımsız bir konuşma oturumudir
- LLM olarak Cerebras üzerinde Qwen-3-235B kullanılır (OpenAI uyumlu API)
- SerpAPI Google Flights, Google Hotels ve Google Maps verilerini çeker
- CORS tüm origin'lere açıktır; production'da `ALLOWED_ORIGINS` env var ile kısıtlanabilir

</details>

---

<details open>
<summary>🇬🇧 English</summary>

## About the Project

Travel Agent is an application where users communicate travel requests in natural language and an AI agent manages the step-by-step flight → hotel → transfer process. User confirmation is collected at each stage; selections are automatically carried to the next phase.

### Target Audience

- Individual users who want to plan trips from a single interface
- Travelers who want to compare flight + accommodation + transfer combinations
- Developers looking to learn AI agent architectures

---

## Architecture

```
┌─────────────────────┐        ┌──────────────────────────────────────┐
│   Frontend          │        │   Backend                            │
│   React + Vite      │◄──────►│   FastAPI                            │
│   Hosted on Railway │        │   └── LangGraph Agent                │
└─────────────────────┘        │        ├── search_flights (SerpAPI)  │
                                │        ├── search_hotels  (SerpAPI)  │
                                │        └── search_transport(SerpAPI) │
                                │   LLM: Cerebras (Qwen-3-235B)        │
                                │   Tracing: LangSmith                 │
                                │   Testing: DeepEval + Groq judge     │
                                └──────────────────────────────────────┘
```

### Agent Flow

```
User Message
      │
      ▼
  orchestrator  ──► tools (SerpAPI search)
      │                    │
      ▼                    ▼
   approval  ◄──── list results
  (user makes a selection)
      │
      ▼
  phase: flight → hotel → transport → done
      │
      ▼
  summary_node (travel summary)
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 5 |
| Backend | FastAPI, Uvicorn |
| Agent Framework | LangGraph |
| LLM | Cerebras Cloud (Qwen-3-235B) |
| Search | SerpAPI (Google Flights, Hotels, Maps) |
| Observability | LangSmith |
| Evaluation | DeepEval + Confident AI |
| Deploy | Railway (backend + frontend as separate services) |

---

## Folder Structure

```
TravelAgent/
├── backend/
│   ├── main.py              # FastAPI app, endpoints
│   ├── railway.toml         # Railway deploy configuration
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # API keys (not committed to git)
│   ├── agent/
│   │   ├── graph.py         # LangGraph agent definition
│   │   ├── state.py         # Pydantic models (FlightOption, HotelOption...)
│   │   └── tools/
│   │       ├── flights.py   # Flight search tool
│   │       ├── hotels.py    # Hotel search tool
│   │       └── transport.py # Transfer search tool
│   └── tests/
│       └── test_example.py  # DeepEval test file
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app, API integration
│   │   └── components/      # TravelForm, FlightCards, HotelCards, SummaryCard
│   ├── railway.toml         # Railway static site configuration
│   └── package.json
└── .gitignore
```

---

## Setup — Local Development

### Requirements

- Python 3.11+
- Node.js 20+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/AE1024/Travel-Agent.git
cd Travel-Agent
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv agent_v

# Activate (Windows)
agent_v\Scripts\Activate.ps1

# Activate (macOS/Linux)
source agent_v/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Environment Variables

Create `backend/.env`:

```env
# Required
SERPAPI_KEY      = your_serpapi_key
CEREBRAS_API_KEY = your_cerebras_key

# LangSmith (optional — for tracing)
LANGCHAIN_TRACING_V2 = true
LANGCHAIN_API_KEY    = your_langsmith_key
LANGCHAIN_PROJECT    = travel-agent

# DeepEval (optional — for testing)
CONFIDENT_API_KEY = your_confident_ai_key
GROQ_API_KEY      = your_groq_key
```

**Where to get API keys:**

| Service | URL |
|---|---|
| SerpAPI | https://serpapi.com |
| Cerebras | https://cloud.cerebras.ai |
| LangSmith | https://smith.langchain.com |
| Confident AI | https://app.confident-ai.com |
| Groq | https://console.groq.com |

### 4. Start the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

---

## How to Use

1. Open the app in your browser
2. Fill in the travel form: origin, destination, date, number of passengers
3. The AI agent lists flights → select a flight
4. The agent asks how many nights → specify hotel preferences
5. The agent lists hotels → select a hotel
6. The agent lists transfer options → select or skip
7. A travel summary with booking links is displayed

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health check |
| POST | `/chat` | Chat with the agent |
| POST | `/search-flights` | Direct flight search |
| POST | `/search-hotels` | Direct hotel search |

---

## Running Tests

```bash
cd backend
deepeval test run tests/test_example.py

# Run a specific test
deepeval test run tests/test_example.py::test_iata_istanbul_paris
```

**Test Coverage:**
- IATA code accuracy (IST, CDG, LHR, JFK...)
- Phase transitions (flight → hotel → transfer)
- Missing information handling
- Off-topic query rejection
- Past date rejection

Results appear in the terminal and on the Confident AI dashboard.

---

## Deploy — Railway

| Service | Root Dir | URL |
|---|---|---|
| Backend (FastAPI) | `backend/` | `travel-agent-production-d4c2.up.railway.app` |
| Frontend (React) | `frontend/` | `delightful-vitality-production-149d.up.railway.app` |

### Backend Variables (Railway)

```
CEREBRAS_API_KEY
SERPAPI_KEY
LANGCHAIN_TRACING_V2 = true
LANGCHAIN_API_KEY
LANGCHAIN_PROJECT    = travel-agent
```

### Frontend Variables (Railway)

```
VITE_API_URL = https://travel-agent-production-d4c2.up.railway.app
```

### Redeploy

```bash
git add .
git commit -m "feat: description"
git push origin main
# Railway deploys automatically
```

---

## Observability — LangSmith

All agent runs are automatically sent to LangSmith while the backend is running.

- **Dashboard:** https://smith.langchain.com
- **Project:** `travel-agent`
- Visible: tool calls, token counts, latency, debugging

---

## Development Notes

- The agent uses `MemorySaver` — each `thread_id` is an independent conversation session
- Uses Qwen-3-235B on Cerebras (OpenAI-compatible API)
- SerpAPI fetches data from Google Flights, Google Hotels, and Google Maps
- CORS is open to all origins; restrict in production using the `ALLOWED_ORIGINS` env var

</details>
