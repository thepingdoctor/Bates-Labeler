# AI Analysis - Quick Start Guide

## 5-Minute Setup

### Step 1: Install Provider Dependencies

Choose **ONE** provider and install its dependencies:

```bash
# Option A: OpenRouter (Recommended - supports 100+ models)
pip install requests

# Option B: Google Cloud
pip install google-cloud-aiplatform

# Option C: Anthropic
pip install anthropic
```

### Step 2: Get API Key

**OpenRouter (Easiest):**
1. Visit https://openrouter.ai/
2. Sign up for free account
3. Generate API key
4. Get $1 free credit (usually 1000+ requests)

**Google Cloud:**
1. Create GCP project at https://console.cloud.google.com
2. Enable Vertex AI API
3. Create service account and download credentials

**Anthropic:**
1. Visit https://console.anthropic.com/
2. Sign up for account
3. Generate API key

### Step 3: Configure Environment

```bash
# For OpenRouter (Recommended)
export AI_ANALYSIS_ENABLED=true
export AI_PROVIDER=openrouter
export OPENROUTER_API_KEY=sk-or-v1-your-key-here

# For Google Cloud
export AI_ANALYSIS_ENABLED=true
export AI_PROVIDER=google
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# For Anthropic
export AI_ANALYSIS_ENABLED=true
export AI_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 4: Test Installation

```python
from bates_labeler.ai_analysis import is_ai_enabled, detect_discrimination

# Check if working
if is_ai_enabled():
    print("✅ AI Analysis is ready!")

    # Test with sample text
    result = detect_discrimination("This is a test document.")
    print(f"Analysis complete: {result}")
else:
    print("❌ AI Analysis not configured")
```

## Common Usage Patterns

### Pattern 1: Analyze Single Document

```python
from bates_labeler.ai_analysis import AIAnalyzer

analyzer = AIAnalyzer()

text = "Your document text here..."

# Check for discrimination
disc = analyzer.detect_discrimination(text)
if disc['has_discrimination']:
    print(f"⚠️ Discrimination detected: {disc['categories']}")

# Check for problematic content
prob = analyzer.identify_problematic_content(text)
if prob['has_issues']:
    print(f"⚠️ Issues: {prob['issues']}")

# Extract metadata
meta = analyzer.extract_metadata(text)
print(f"Document type: {meta['document_type']}")
print(f"Topics: {meta['topics']}")
```

### Pattern 2: Process PDF

```python
from pypdf import PdfReader
from bates_labeler.ai_analysis import AIAnalyzer

analyzer = AIAnalyzer()
reader = PdfReader("document.pdf")

for i, page in enumerate(reader.pages):
    text = page.extract_text()

    if analyzer.is_enabled():
        result = analyzer.detect_discrimination(text)
        if result.get('has_discrimination'):
            print(f"Page {i+1}: ⚠️ Issues detected")
```

### Pattern 3: Batch Processing

```python
from bates_labeler.ai_analysis import AIAnalyzer

analyzer = AIAnalyzer()
documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

for doc_path in documents:
    # Extract text from document...
    text = extract_text(doc_path)

    # Analyze (uses cache for duplicates)
    result = analyzer.identify_problematic_content(text)

    # Process result...
    if result['has_issues']:
        print(f"{doc_path}: Issues - {result['severity']}")

# Check cache efficiency
stats = analyzer.get_cache_stats()
print(f"Cache hits saved {stats['total_entries']} API calls")
```

## Configuration Options

### Basic Settings

```bash
AI_ANALYSIS_ENABLED=true         # Enable AI (default: false)
AI_PROVIDER=openrouter           # Provider: openrouter|google|anthropic
AI_MODEL=anthropic/claude-3-haiku # Model name (provider-specific)
```

### Performance Tuning

```bash
AI_MAX_TOKENS=1000               # Max response length (default: 1000)
AI_TEMPERATURE=0.3               # Consistency (0-1, default: 0.3)
AI_CACHE_ENABLED=true            # Enable caching (default: true)
AI_CACHE_TTL_HOURS=24            # Cache lifetime (default: 24)
```

### Analysis Thresholds

```bash
AI_DISCRIMINATION_THRESHOLD=0.7  # Confidence threshold (default: 0.7)
AI_PROBLEMATIC_THRESHOLD=0.6     # Confidence threshold (default: 0.6)
```

## Model Recommendations

### For Cost Optimization
```bash
# OpenRouter
AI_MODEL=anthropic/claude-3-haiku        # Fast, cheap, good quality
AI_MODEL=google/gemini-flash-1.5         # Very fast, cheapest

# Google Cloud
AI_MODEL=gemini-1.5-flash                # Fastest, most cost-effective

# Anthropic
AI_MODEL=claude-3-haiku-20240307         # Balanced speed/cost
```

### For Highest Quality
```bash
# OpenRouter
AI_MODEL=anthropic/claude-3-5-sonnet     # Best overall quality
AI_MODEL=openai/gpt-4-turbo              # Alternative high quality

# Google Cloud
AI_MODEL=gemini-1.5-pro                  # Google's best

# Anthropic
AI_MODEL=claude-3-opus-20240229          # Highest quality
```

## Troubleshooting

### Issue: "AI analysis not enabled or configured"

**Solution:**
```bash
# Check environment variables are set
echo $AI_ANALYSIS_ENABLED
echo $AI_PROVIDER
echo $OPENROUTER_API_KEY  # or other provider key

# Set if missing
export AI_ANALYSIS_ENABLED=true
export AI_PROVIDER=openrouter
export OPENROUTER_API_KEY=your_key
```

### Issue: "requests library required"

**Solution:**
```bash
pip install requests
```

### Issue: High API costs

**Solution:**
```bash
# Enable caching (if disabled)
export AI_CACHE_ENABLED=true

# Use cheaper model
export AI_MODEL=anthropic/claude-3-haiku

# Reduce max tokens
export AI_MAX_TOKENS=500
```

### Issue: Poor analysis quality

**Solution:**
```bash
# Increase temperature for creativity
export AI_TEMPERATURE=0.5

# Increase max tokens for detail
export AI_MAX_TOKENS=2000

# Use higher quality model
export AI_MODEL=anthropic/claude-3-5-sonnet
```

### Issue: Timeout errors

**Solution:**
```bash
# Reduce max tokens
export AI_MAX_TOKENS=500

# Use faster model
export AI_MODEL=anthropic/claude-3-haiku
```

## Cost Estimates

### OpenRouter Pricing (approximate)
- **Claude 3 Haiku**: $0.25 per 1M input tokens (~$0.00025 per document)
- **Gemini Flash**: $0.075 per 1M input tokens (~$0.00008 per document)
- **Claude 3 Sonnet**: $3.00 per 1M input tokens (~$0.003 per document)

### Typical Usage
- Average document: ~1000 tokens
- With caching: 60-90% reduction
- 1000 documents: $0.25-$3.00 (depending on model)

## Best Practices

### 1. Enable Caching
Always keep caching enabled to reduce costs:
```python
# Cache is enabled by default
analyzer = AIAnalyzer()
```

### 2. Use Appropriate Models
- **Standard documents**: Claude 3 Haiku or Gemini Flash
- **Critical analysis**: Claude 3 Sonnet or Opus
- **High volume**: Gemini Flash

### 3. Batch Similar Documents
Process similar documents together to maximize cache hits:
```python
# Good: Process all contracts together
for contract in contracts:
    analyze(contract)

# Then process all emails together
for email in emails:
    analyze(email)
```

### 4. Monitor Cache Performance
```python
stats = analyzer.get_cache_stats()
hit_rate = stats['total_entries'] / total_analyzed
print(f"Cache hit rate: {hit_rate:.1%}")
```

### 5. Handle Errors Gracefully
```python
result = analyzer.detect_discrimination(text)

if result.get('error'):
    print(f"Analysis failed: {result['message']}")
    # Continue processing...
else:
    # Process result...
```

## Environment File Template

Create `.env` file in project root:

```bash
# AI Analysis Configuration
AI_ANALYSIS_ENABLED=true
AI_PROVIDER=openrouter

# API Keys (add your actual keys)
OPENROUTER_API_KEY=sk-or-v1-your-key-here
# GOOGLE_CLOUD_PROJECT=your-project-id
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# Model Configuration
AI_MODEL=anthropic/claude-3-haiku
AI_MAX_TOKENS=1000
AI_TEMPERATURE=0.3

# Cache Settings
AI_CACHE_ENABLED=true
AI_CACHE_TTL_HOURS=24

# Analysis Thresholds
AI_DISCRIMINATION_THRESHOLD=0.7
AI_PROBLEMATIC_THRESHOLD=0.6
```

Then load with:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Quick Reference

### Check if enabled
```python
from bates_labeler.ai_analysis import is_ai_enabled
print(is_ai_enabled())  # True/False
```

### Detect discrimination
```python
from bates_labeler.ai_analysis import detect_discrimination
result = detect_discrimination("text")
print(result['has_discrimination'])
```

### Find problematic content
```python
from bates_labeler.ai_analysis import identify_problematic_content
result = identify_problematic_content("text")
print(result['has_issues'])
```

### Extract metadata
```python
from bates_labeler.ai_analysis import extract_metadata
result = extract_metadata("text")
print(result['document_type'])
```

### Clear cache
```python
from bates_labeler.ai_analysis import get_analyzer
analyzer = get_analyzer()
analyzer.clear_cache()
```

## Next Steps

1. ✅ **Setup complete** - AI analysis ready
2. 📖 **Read full docs** - See `/docs/AI_ANALYSIS.md`
3. 🧪 **Run examples** - Try `/docs/ai_analysis_example.py`
4. 🔧 **Integrate** - Add to your workflow
5. 📊 **Monitor** - Check cache stats and costs

## Support

- **Documentation**: `/docs/AI_ANALYSIS.md`
- **Examples**: `/docs/ai_analysis_example.py`
- **Tests**: `/tests/test_ai_analysis.py`
- **Issues**: GitHub Issues

---

**Ready to analyze!** 🚀
