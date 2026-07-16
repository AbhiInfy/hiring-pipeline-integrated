# Command Reference Guide

Complete documentation of all command-line options for the hiring pipeline.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Stage Options](#stage-options)
3. [Matching Options](#matching-options)
4. [Email Options](#email-options)
5. [Common Examples](#common-examples)
6. [Option Combinations](#option-combinations)

---

## Quick Reference

### Minimal Command (Token-Based)
```bash
python run_integrated_pipeline.py
```

### Recommended (Semantic Matching)
```bash
python run_integrated_pipeline.py --use-embeddings --cache-embeddings
```

### Full Command (All Options)
```bash
python run_integrated_pipeline.py \
  --keyword "python developer" \
  --pages 3 \
  --max-age-hours 24 \
  --delay 2.0 \
  --min-score 0.01 \
  --top-k 5 \
  --use-embeddings \
  --embedding-model hybrid \
  --blend-ratio 0.7 \
  --cache-embeddings \
  --send-emails \
  --email-provider smtp \
  --notification-email your@email.com
```

---

## Stage Options

### Stage 0: Email Extraction (Optional)

Extract candidates from email before pipeline runs.

#### `--extract-from-emails`
**Type**: Flag (boolean)  
**Default**: `False`  
**Description**: Enable email candidate extraction

```bash
python run_integrated_pipeline.py --extract-from-emails
```

**What it does**:
1. Connect to IMAP server (Gmail, Outlook, etc.)
2. Extract candidate info from emails
3. Parse CV attachments (PDF/DOCX)
4. Add to `data/candidate_profiles.xlsx`
5. Then run pipeline

---

#### `--email-hours`
**Type**: Integer  
**Default**: `24`  
**Range**: 1-720  
**Description**: Hours back to scan emails

```bash
python run_integrated_pipeline.py --extract-from-emails --email-hours 48
```

**Examples**:
- `--email-hours 1` = Last 1 hour
- `--email-hours 24` = Last 24 hours (default)
- `--email-hours 168` = Last week
- `--email-hours 720` = Last 30 days

---

#### `--max-emails`
**Type**: Integer  
**Default**: `50`  
**Description**: Maximum emails to process

```bash
python run_integrated_pipeline.py --extract-from-emails --max-emails 100
```

**Why limit**:
- Avoid timeouts
- Control processing time
- Test with small batch first

---

### Stage 1: Job Ingestion

Search and scrape jobs from Naukri.com.

#### `--keyword` 
**Type**: String  
**Default**: `"Oracle Fusion Application"`  
**Description**: Job search keyword

```bash
python run_integrated_pipeline.py --keyword "python developer"
```

**Examples**:
- `--keyword "Java Developer"`
- `--keyword "Data Scientist"`
- `--keyword "Oracle Fusion"`
- `--keyword "Python Engineer"`

**Tip**: Use job titles that match your candidates' skills

---

#### `--pages`
**Type**: Integer  
**Default**: `3`  
**Range**: 1-50  
**Description**: Number of Naukri pages to scrape

```bash
python run_integrated_pipeline.py --pages 5
```

**Page to Job Ratio** (approximate):
- `--pages 1` = ~50 jobs
- `--pages 3` = ~150 jobs (recommended)
- `--pages 5` = ~250 jobs
- `--pages 10` = ~500 jobs

**Processing Time**:
- `--pages 1` = ~30 seconds
- `--pages 3` = ~2 minutes
- `--pages 5` = ~3 minutes
- `--pages 10` = ~5 minutes

---

#### `--max-age-hours`
**Type**: Integer  
**Default**: `24`  
**Description**: Only include jobs posted within N hours

```bash
python run_integrated_pipeline.py --max-age-hours 48
```

**Examples**:
- `--max-age-hours 24` = Posted in last 24 hours (default)
- `--max-age-hours 1` = Posted in last 1 hour (very fresh)
- `--max-age-hours 168` = Posted in last week
- No limit: Use very high number like `10000`

---

#### `--delay`
**Type**: Float  
**Default**: `2.0`  
**Description**: Seconds to wait between requests (rate limiting)

```bash
python run_integrated_pipeline.py --delay 1.0
```

**Why it exists**: 
- Respect Naukri's rate limits
- Avoid IP blocking
- Prevent overwhelming the server

**Values**:
- `--delay 0.5` = Faster (risky)
- `--delay 2.0` = Balanced (default)
- `--delay 5.0` = Slower (safer)

---

#### `--output`
**Type**: Path  
**Default**: `output/job_links.xlsx`  
**Description**: Output path for job links

```bash
python run_integrated_pipeline.py --output custom_output/jobs.xlsx
```

---

### Stage 2: Candidate Database

Load candidates from Excel.

#### `--candidate-profiles-file`
**Type**: Path  
**Default**: `data/candidate_profiles.xlsx`  
**Description**: Path to candidate profile Excel file

```bash
python run_integrated_pipeline.py --candidate-profiles-file data/my_candidates.xlsx
```

**File must have columns**:
- `Candidate Name` (or `Name`)
- `Skills` (comma-separated)
- `Email` (or `Email ID`)
- `Notice Period (Days)` (or `Notice`)

---

#### `--rows`
**Type**: Integer  
**Default**: `None` (all)  
**Description**: Limit JD generation to N rows

```bash
python run_integrated_pipeline.py --rows 10
```

**Use case**: Test with small dataset first

**Examples**:
- `--rows 5` = Process only 5 jobs
- `--rows 50` = Process first 50 jobs
- No flag = Process all jobs

---

### Stage 3: Matching

Configure matching algorithm and thresholds.

#### `--min-score`
**Type**: Float  
**Default**: `0.12`  
**Range**: 0.0 to 1.0  
**Description**: Minimum match score to include candidate

```bash
python run_integrated_pipeline.py --min-score 0.25
```

**Score Meaning** (for blended matching):
- `0.0-0.10` = Very permissive (find many, low quality)
- `0.10-0.20` = Permissive (good quantity)
- `0.20-0.30` = Balanced (default: 0.12)
- `0.30-0.50` = Strict (few, high quality)
- `0.50+` = Very strict (only best matches)

**Impact Examples**:
```
--min-score 0.01  = 300-500 matches (permissive)
--min-score 0.12  = 100-200 matches (balanced, default)
--min-score 0.25  = 30-50 matches (strict)
--min-score 0.50  = 5-10 matches (very strict)
```

---

#### `--top-k`
**Type**: Integer  
**Default**: `5`  
**Description**: Maximum top matches to return per job

```bash
python run_integrated_pipeline.py --top-k 10
```

**Examples**:
- `--top-k 3` = Show 3 best per job
- `--top-k 5` = Show 5 best per job (default)
- `--top-k 10` = Show 10 best per job
- `--top-k 20` = Show 20 best per job

**Use case**:
- Fewer for quick review
- More for comprehensive view

---

## Matching Options (Semantic/Embeddings)

### `--use-embeddings`
**Type**: Flag (boolean)  
**Default**: `False`  
**Description**: Enable semantic matching with embeddings

```bash
python run_integrated_pipeline.py --use-embeddings
```

**What it enables**:
- Groq API integration (if GROQ_API_KEY set)
- Sentence Transformers fallback (always available)
- Blended scoring (semantic + token)
- Better matching quality

**Requires**: Nothing (API key is optional)

---

### `--embedding-model`
**Type**: Choice  
**Default**: `hybrid`  
**Options**: `hybrid`, `groq`, `sentence-transformers`  
**Description**: Which embedding service to use

```bash
python run_integrated_pipeline.py --use-embeddings --embedding-model groq
```

#### `hybrid` (Recommended)
```bash
--embedding-model hybrid
```
- Tries Groq first (50ms)
- Falls back to local (100ms)
- Always works
- Requires: Optional GROQ_API_KEY
- Speed: 50-100ms per embedding

#### `groq`
```bash
--embedding-model groq
```
- Groq API only
- Fast (50ms per embedding)
- Requires: GROQ_API_KEY set
- Falls back to token-based if fails

#### `sentence-transformers`
```bash
--embedding-model sentence-transformers
```
- Local model only
- Medium speed (100ms per embedding)
- Requires: Nothing
- Works offline
- No API key needed

---

### `--blend-ratio`
**Type**: Float  
**Default**: `0.7`  
**Range**: 0.0 to 1.0  
**Description**: Weight for semantic score in blended matching

```bash
python run_integrated_pipeline.py --use-embeddings --blend-ratio 0.5
```

**Formula**: `final_score = (semantic_score * blend_ratio) + (token_score * (1 - blend_ratio))`

**Examples**:
- `--blend-ratio 0.3` = 30% semantic, 70% token (keyword-heavy)
- `--blend-ratio 0.5` = 50% semantic, 50% token (balanced)
- `--blend-ratio 0.7` = 70% semantic, 30% token (recommended)
- `--blend-ratio 0.9` = 90% semantic, 10% token (semantic-heavy)

**When to use**:
- `0.3` = Must have specific keywords
- `0.5` = Balanced matching
- `0.7` = Semantic understanding matters (default)
- `0.9` = Fuzzy, experience-based matching

---

### `--cache-embeddings`
**Type**: Flag (boolean)  
**Default**: `False`  
**Description**: Cache embeddings to disk for faster reruns

```bash
python run_integrated_pipeline.py --use-embeddings --cache-embeddings
```

**Benefits**:
- First run: Normal speed (8-30s)
- Rerun: Instant (1s) ⚡
- Storage: ~5 MB per 100 jobs

**Example**:
```bash
# First time (generates and caches)
python run_integrated_pipeline.py --use-embeddings --cache-embeddings
# Time: 8-30 seconds

# Second time (reuses cache)
python run_integrated_pipeline.py --use-embeddings --cache-embeddings
# Time: 1 second! 🚀
```

---

## Email Options

### `--send-emails`
**Type**: Flag (boolean)  
**Default**: `False`  
**Description**: Actually send emails (vs dry-run)

```bash
python run_integrated_pipeline.py --send-emails
```

**Without flag**: Dry-run (test, no emails sent)  
**With flag**: Actually send emails

**What gets sent**:
- Email to job contact person
- Top 3 candidates for each job
- Match scores and reasoning

---

### `--email-provider`
**Type**: Choice  
**Default**: `smtp`  
**Options**: `smtp`, `sendgrid`  
**Description**: Email sending method

```bash
python run_integrated_pipeline.py --send-emails --email-provider smtp
```

#### `smtp` (Gmail, Outlook)
```bash
--email-provider smtp
```
- Uses SMTP_SERVER, SMTP_PORT from .env
- Requires Gmail app password
- Free
- Setup: Enable 2FA + generate app password

#### `sendgrid`
```bash
--email-provider sendgrid
```
- Uses SendGrid API
- Free tier: 100 emails/day
- Requires: SENDGRID_API_KEY in .env
- Setup: Create SendGrid account

---

### `--notification-email`
**Type**: String  
**Default**: `` (empty)  
**Description**: Email address for pipeline notifications

```bash
python run_integrated_pipeline.py --send-emails --notification-email admin@company.com
```

**What you receive**:
- Email when pipeline completes
- Summary of results
- Links to output files
- Success/failure status

**Example notification**:
```
Pipeline Completed!

Jobs processed: 150
Candidates evaluated: 450
Total matches: 245
Emails sent: 30

Results in: E:\...\output\
```

---

## Common Examples

### Example 1: Quick Test
```bash
python run_integrated_pipeline.py --pages 1 --rows 5 --min-score 0.05
```
**Use case**: Test on small dataset  
**Time**: ~30 seconds  
**Jobs**: ~50  
**Matches**: ~20-50

---

### Example 2: Production Run (Token-Based)
```bash
python run_integrated_pipeline.py \
  --keyword "python developer" \
  --pages 3 \
  --min-score 0.12 \
  --top-k 5 \
  --send-emails \
  --notification-email your@email.com
```
**Use case**: Default production  
**Time**: ~2 minutes  
**Jobs**: ~150  
**Matches**: ~100-150  
**Cost**: $0

---

### Example 3: Production Run (Semantic Matching) ⭐ RECOMMENDED
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
**Use case**: Better matching quality  
**Time**: 8-30 seconds (first), 1s (rerun)  
**Jobs**: ~150  
**Matches**: ~200-300  
**Cost**: $0 (Groq free tier)

---

### Example 4: Permissive Matching
```bash
python run_integrated_pipeline.py \
  --keyword "developer" \
  --pages 5 \
  --min-score 0.01 \
  --top-k 10 \
  --use-embeddings
```
**Use case**: Find all possible matches  
**Matches**: 300-500  
**Jobs**: 250  
**Quality**: Mixed (includes lower matches)

---

### Example 5: Strict Matching
```bash
python run_integrated_pipeline.py \
  --keyword "senior python developer" \
  --pages 2 \
  --min-score 0.30 \
  --top-k 3 \
  --use-embeddings \
  --blend-ratio 0.9
```
**Use case**: Only best matches  
**Matches**: 20-30  
**Quality**: High  
**Jobs**: ~100

---

### Example 6: Extract + Run Pipeline
```bash
python run_integrated_pipeline.py \
  --extract-from-emails \
  --email-hours 48 \
  --keyword "python" \
  --pages 3 \
  --use-embeddings \
  --send-emails
```
**Use case**: Extract candidates from email, then match  
**Time**: 2-3 minutes  
**Result**: Auto-populated candidates + matches

---

## Option Combinations

### Best for Speed
```bash
python run_integrated_pipeline.py --pages 1 --min-score 0.20
```
Time: ~30 seconds

### Best for Quality
```bash
python run_integrated_pipeline.py \
  --use-embeddings \
  --min-score 0.30 \
  --blend-ratio 0.9 \
  --top-k 3
```

### Best for Quantity
```bash
python run_integrated_pipeline.py \
  --pages 5 \
  --min-score 0.01 \
  --top-k 20
```

### Best for Production
```bash
python run_integrated_pipeline.py \
  --keyword "your job title" \
  --pages 3 \
  --min-score 0.12 \
  --use-embeddings \
  --cache-embeddings \
  --send-emails
```

### Best for Testing
```bash
python run_integrated_pipeline.py \
  --pages 1 \
  --rows 5 \
  --min-score 0.01
```

---

## Environment Variables (Alternative to CLI)

Instead of `--use-embeddings`, set in `.env`:

```bash
# .env file
USE_EMBEDDINGS=true
EMBEDDINGS_BLEND_RATIO=0.7
GROQ_API_KEY=gsk_...
```

Then run without these flags:
```bash
python run_integrated_pipeline.py --keyword "python" --pages 3
```

CLI flags **override** environment variables.

---

## Help & Information

### View All Options
```bash
python run_integrated_pipeline.py --help
```

Shows all available options with descriptions.

---

## Parameter Groups

### Efficiency Parameters
- `--pages` - Number of pages
- `--max-emails` - Limit emails
- `--rows` - Limit JDs
- `--delay` - Rate limit

### Quality Parameters
- `--min-score` - Match threshold
- `--top-k` - Candidates per job
- `--blend-ratio` - Semantic weight

### Semantic Parameters
- `--use-embeddings` - Enable embeddings
- `--embedding-model` - Which service
- `--blend-ratio` - Score weight
- `--cache-embeddings` - Caching

### Email Parameters
- `--send-emails` - Actually send
- `--email-provider` - SMTP or SendGrid
- `--notification-email` - Admin email

### Search Parameters
- `--keyword` - Job search term
- `--pages` - Pages to scrape
- `--max-age-hours` - Recent jobs only

---

## Quick Decision Tree

```
Want to test quickly?
  └─ python run_integrated_pipeline.py --pages 1

Want production run?
  └─ python run_integrated_pipeline.py --use-embeddings --cache-embeddings

Want to find ALL candidates?
  └─ python run_integrated_pipeline.py --min-score 0.01 --pages 5

Want ONLY best candidates?
  └─ python run_integrated_pipeline.py --min-score 0.30 --top-k 3

Want to send emails?
  └─ python run_integrated_pipeline.py --use-embeddings --send-emails

Want to extract from email first?
  └─ python run_integrated_pipeline.py --extract-from-emails
```

---

## Tips & Best Practices

✅ **Start with defaults** and adjust as needed  
✅ **Test with `--pages 1`** before large runs  
✅ **Use `--use-embeddings`** for better quality  
✅ **Use `--cache-embeddings`** if running multiple times  
✅ **Set `--notification-email`** to get status updates  
✅ **Check `output/` folder** after each run  

❌ **Don't use high `--pages` (>10)** without testing  
❌ **Don't set `--delay` too low** (<1.0) - risk being blocked  
❌ **Don't use `--send-emails`** without testing first  

---

## Troubleshooting

**No matches found?**
```bash
--min-score 0.01 --use-embeddings
```

**Slow performance?**
```bash
--pages 1 --cache-embeddings
```

**Too many matches?**
```bash
--min-score 0.25 --top-k 3
```

**Want more detail?**
```bash
streamlit run src/dashboard/app.py
```

---

**Need help?** See:
- `QUICK_START.md` - Get running in 5 minutes
- `HYBRID_EMBEDDINGS_GUIDE.md` - Embeddings explained
- `README_EMBEDDINGS.md` - Embeddings overview
