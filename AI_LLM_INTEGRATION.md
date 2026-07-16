# AI/LLM Integration in Hiring Pipeline

Documentation of how AI and Language Models are used in the hiring pipeline.

---

## Overview

The hiring pipeline uses AI-powered semantic embeddings for intelligent candidate-job matching.

### AI Components

- **Groq API** - Cloud-based LLM for embeddings
- **Sentence Transformers** - Local LLM for fallback
- **Semantic Matching** - Vector-based comparison
- **Blended Scoring** - Combines semantic + keyword matching

---

## AI Models Used

### 1. Groq API (Primary)

**Model**: Mixtral-8x7b via Groq
**Type**: Cloud LLM
**Speed**: 50ms per embedding
**Cost**: Free (14,000 calls/month)
**Location**: `src/embeddings/groq_embeddings.py`

How it works:
```
Text → Groq Cloud LLM → Semantic Vector (1536 dimensions)
```

### 2. Sentence Transformers (Fallback)

**Model**: all-MiniLM-L6-v2 (BERT-based)
**Type**: Local LLM
**Speed**: 100ms per embedding
**Cost**: Free (open source)
**Size**: 22 MB
**Memory**: 200 MB

How it works:
```
Text → Local LLM Processing → Semantic Vector (1536 dimensions)
```

Features:
- Works offline (no internet required)
- No API key needed
- Always available as fallback

### 3. Hybrid Service

**Location**: `src/embeddings/hybrid_embeddings.py`

Strategy:
```
1. Try Groq API (fast, 50ms)
2. If unavailable: Use local Sentence Transformers (100ms)
3. Result: Always AI-powered embeddings
```

---

## How AI Works

### Embeddings

An embedding is a numerical vector that captures semantic meaning:

```
"Python Developer"
       ↓
    LLM Processing
       ↓
[0.234, 0.891, 0.456, ..., 0.123]
```

### Semantic Similarity

AI compares embeddings using cosine similarity:

```
Job Embedding:        [0.234, 0.891, 0.456, ..., 0.123]
Candidate Embedding:  [0.245, 0.889, 0.451, ..., 0.125]
                            ↓
                    Cosine Similarity
                            ↓
                    Score: 0.87 (87%)
```

---

## Where AI is Used

### 1. Job Description Embeddings

Process:
```
Job Text → Groq/Sentence Transformers → Semantic Vector
```

Captures:
- Role level and responsibilities
- Technical skills required
- Experience requirements
- Job context

### 2. Candidate Skill Embeddings

Process:
```
Candidate Skills → Same LLM Model → Semantic Vector
```

Captures:
- Technical skills
- Experience profile
- Skill combinations

### 3. Semantic Matching

Process:
```
Job Embedding + Candidate Embedding → Cosine Similarity → Score
```

**Location**: `src/matching/semantic_matching.py`

### 4. Blended Scoring

Formula:
```
final_score = (semantic_score * 0.7) + (token_score * 0.3)
```

Benefits:
- AI understanding (70% semantic)
- Keyword validation (30% token)
- Best of both approaches

---

## AI-Powered Matching Flow

```
Job Description
       ↓
LLM Embedding (Groq or Local)
       ↓
Semantic Vector (1536 dims)
       ↓
Cosine Similarity + Token Match
       ↓
Blended Score (70% + 30%)
       ↓
Ranked Matches
```

---

## Configuration

### Enable AI/LLM Matching

```bash
# Default: Hybrid (Groq + local fallback)
python run_integrated_pipeline.py --use-embeddings

# With caching for speed
python run_integrated_pipeline.py --use-embeddings --cache-embeddings
```

### Command Options

```bash
--use-embeddings                    # Enable AI embeddings
--embedding-model hybrid            # Groq + local (default)
--embedding-model groq              # Groq only
--embedding-model sentence-transformers  # Local only
--blend-ratio 0.7                   # 70% semantic, 30% token
--cache-embeddings                  # Cache for faster reruns
```

### Environment Variables

```bash
GROQ_API_KEY=gsk_your_key_here      # For Groq (optional)
USE_EMBEDDINGS=true                 # Enable by default
EMBEDDINGS_BLEND_RATIO=0.7          # Semantic weight
EMBEDDINGS_MODEL=hybrid             # Which model to use
```

---

## Performance

### Speed
- Token-based only: 5 seconds
- AI (first run): 8-30 seconds
- AI (cached): 1 second

### Cost
- Groq: Free (14,000 calls/month)
- Sentence Transformers: Free (open source)
- Total: $0

---

## Summary

### AI/LLM Components

✅ **Groq Cloud LLM** - Primary embeddings (50ms)
✅ **Sentence Transformers LLM** - Fallback embeddings (100ms)
✅ **Semantic Vectors** - 1536-dimensional representations
✅ **Cosine Similarity** - Vector comparison
✅ **Blended Scoring** - AI + keyword validation
✅ **Hybrid Approach** - Cloud + Local for reliability

### Key Features

- AI understands meaning and context
- Always intelligent matching (never degrades)
- Completely free (both models free)
- Works with or without internet
- Fallback ensures reliability

