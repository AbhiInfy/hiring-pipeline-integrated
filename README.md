# Hiring Pipeline - Advanced Semantic Matching System

Automated recruitment pipeline with **hybrid semantic embeddings** (Groq + Sentence Transformers) for better candidate-job matching.

---

## 🚀 Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Setup (Optional: Add Groq API Key)
```bash
# Get free key at: https://console.groq.com/
echo "GROQ_API_KEY=gsk_your_key" >> .env
```

### 3. Run
```bash
python run_integrated_pipeline.py --use-embeddings --cache-embeddings
```

### 4. View Results
```bash
streamlit run src/dashboard/app.py
```

---

## 📚 Documentation

### ⭐ COMMAND REFERENCE (START HERE)
- **[COMMAND_REFERENCE.md](COMMAND_REFERENCE.md)** - Complete documentation of all command options
  - All parameters explained with examples
  - Common usage patterns
  - Parameter combinations
  - Best practices

### Getting Started
- **[QUICK_START.md](QUICK_START.md)** - Run pipeline in 5 minutes
- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - Complete setup reference

### Embeddings & Matching
- **[README_EMBEDDINGS.md](README_EMBEDDINGS.md)** - Embeddings overview
- **[HYBRID_EMBEDDINGS_GUIDE.md](HYBRID_EMBEDDINGS_GUIDE.md)** - Complete embeddings guide
- **[GROQ_SETUP.md](GROQ_SETUP.md)** - Groq API setup (2 min)

### Technical Details
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design & data flow
- **[HYBRID_IMPLEMENTATION_SUMMARY.md](HYBRID_IMPLEMENTATION_SUMMARY.md)** - Implementation details

---

## 🎯 Common Commands

### Basic Run
```bash
python run_integrated_pipeline.py
```

### Production Run (Recommended)
```bash
python run_integrated_pipeline.py --use-embeddings --cache-embeddings
```

### With All Options
```bash
python run_integrated_pipeline.py \
  --keyword "python developer" \
  --pages 3 \
  --min-score 0.01 \
  --top-k 5 \
  --use-embeddings \
  --cache-embeddings \
  --send-emails \
  --notification-email your@email.com
```

**→ For all command options, see [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md)**

---

## 🔑 Key Features

✅ **Semantic Matching** - Understands skill context  
✅ **Hybrid Embeddings** - Groq + Sentence Transformers  
✅ **Completely Free** - $0 cost  
✅ **No Setup** - Works out of the box  
✅ **Caching** - Instant reruns  
✅ **Offline** - Local fallback available  

---

## 💰 Cost: $0 🎉

- Groq: Free tier (14,000 calls/month)
- Sentence Transformers: Open source
- Total: **$0**

---

## 📖 Where to Find What

| I want to... | Go to... |
|---|---|
| See all command options | [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md) ⭐ |
| Get started quickly (5 min) | [QUICK_START.md](QUICK_START.md) |
| Understand embeddings | [HYBRID_EMBEDDINGS_GUIDE.md](HYBRID_EMBEDDINGS_GUIDE.md) |
| Setup Groq API key | [GROQ_SETUP.md](GROQ_SETUP.md) |
| See system design | [ARCHITECTURE.md](ARCHITECTURE.md) |

---

**Start here: [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md)** ← All command options explained with examples

Last updated: 2025-07-15 | Status: ✅ Production Ready
