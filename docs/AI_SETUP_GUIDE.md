# AI Analysis Setup Guide

Complete guide to configuring AI-powered document analysis in Bates-Labeler.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Configuration](#environment-configuration)
3. [Provider-Specific Setup](#provider-specific-setup)
4. [Testing Your Integration](#testing-your-integration)
5. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Option 1: Web UI (Easiest)

1. **Launch the Web UI**:
   ```bash
   poetry run streamlit run app.py
   ```

2. **Navigate to Advanced Options** in the sidebar

3. **Enable AI Analysis**:
   - ✅ Check "Enable AI Analysis"
   - Select AI Provider (OpenRouter recommended)
   - Enter your API key
   - Choose analysis types

4. **Process documents** as normal - AI analysis runs automatically!

### Option 2: Command Line

1. **Set environment variables**:
   ```bash
   export AI_ANALYSIS_ENABLED=true
   export AI_PROVIDER=openrouter
   export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
   ```

2. **Run bates command**:
   ```bash
   poetry run bates --input document.pdf --bates-prefix "CASE-"
   ```

3. **AI analysis runs automatically** during processing!

## ⚙️ Environment Configuration

### Using .env File (Recommended)

Create a `.env` file in your project root:

```env
# Enable AI Analysis
AI_ANALYSIS_ENABLED=true

# Provider Selection (openrouter, google, anthropic)
AI_PROVIDER=openrouter

# API Keys (only set the one for your chosen provider)
OPENROUTER_API_KEY=sk-or-v1-your-key-here
# GOOGLE_CLOUD_PROJECT=your-project-id
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# Model Configuration (optional - uses sensible defaults)
AI_MODEL=anthropic/claude-3-haiku
AI_MAX_TOKENS=1000
AI_TEMPERATURE=0.3

# Caching (optional - default: enabled)
AI_CACHE_ENABLED=true
AI_CACHE_TTL_HOURS=24

# Analysis Thresholds (optional)
AI_DISCRIMINATION_THRESHOLD=0.7
AI_PROBLEMATIC_THRESHOLD=0.6
```

**Important**: Add `.env` to your `.gitignore`:
```bash
echo ".env" >> .gitignore
```

### Using Shell Environment

For temporary/session-based configuration:

```bash
# Enable AI
export AI_ANALYSIS_ENABLED=true
export AI_PROVIDER=openrouter

# Set API key
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"

# Optional settings
export AI_MODEL="anthropic/claude-3-haiku"
export AI_CACHE_ENABLED=true
```

### Using Python Configuration

For programmatic control:

```python
import os
from bates_labeler.ai_analysis import AIAnalysisConfig

# Method 1: Environment variables (recommended)
os.environ['AI_ANALYSIS_ENABLED'] = 'true'
os.environ['AI_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = 'sk-or-v1-your-key-here'

config = AIAnalysisConfig()  # Loads from environment

# Method 2: Direct configuration (less secure)
config = AIAnalysisConfig()
config.enabled = True
config.provider = 'openrouter'
config.openrouter_api_key = 'sk-or-v1-your-key-here'

# Validate configuration
if config.validate():
    print("✅ Configuration valid!")
else:
    print("❌ Configuration invalid - check API keys")
```

## 🔑 Provider-Specific Setup

### OpenRouter (Recommended)

**Why OpenRouter?**
- Access to 100+ AI models through one API
- Competitive pricing ($0.001-$0.025 per 1K tokens)
- Simple setup
- Automatic fallback to alternative models

**Setup Steps**:

1. **Create Account**:
   - Visit https://openrouter.ai
   - Click "Sign Up" (Google/GitHub OAuth supported)

2. **Generate API Key**:
   - Go to https://openrouter.ai/keys
   - Click "Create Key"
   - Copy the key (starts with `sk-or-v1-`)

3. **Configure Bates-Labeler**:
   ```bash
   export AI_PROVIDER=openrouter
   export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
   ```

4. **Choose Model** (optional):
   ```bash
   # Fast and cheap (recommended)
   export AI_MODEL="anthropic/claude-3-haiku"

   # Balanced performance
   export AI_MODEL="anthropic/claude-3-5-sonnet"

   # Premium quality
   export AI_MODEL="anthropic/claude-3-opus"

   # Google models
   export AI_MODEL="google/gemini-pro"
   export AI_MODEL="google/gemini-flash-1.5"
   ```

5. **Test Integration**:
   ```bash
   # Verify connection
   curl https://openrouter.ai/api/v1/models \
     -H "Authorization: Bearer $OPENROUTER_API_KEY"
   ```

**Pricing Examples** (as of 2025):
- Claude Haiku: $0.00025/1K input, $0.00125/1K output
- Claude Sonnet: $0.003/1K input, $0.015/1K output
- Gemini Pro: $0.00025/1K input, $0.00050/1K output

### Google Cloud Vertex AI

**Why Google Cloud?**
- Enterprise SLA and support
- Integration with Google Cloud ecosystem
- Advanced security and compliance
- Multimodal capabilities

**Setup Steps**:

1. **Create Google Cloud Project**:
   - Visit https://console.cloud.google.com
   - Create new project or select existing
   - Enable billing for the project

2. **Enable Vertex AI API**:
   ```bash
   # Using gcloud CLI
   gcloud services enable aiplatform.googleapis.com
   ```

   Or via Console:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Vertex AI API"
   - Click "Enable"

3. **Create Service Account**:
   ```bash
   # Create service account
   gcloud iam service-accounts create bates-labeler-ai \
     --display-name="Bates Labeler AI Analysis"

   # Grant Vertex AI permissions
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:bates-labeler-ai@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"

   # Generate credentials
   gcloud iam service-accounts keys create ~/bates-labeler-credentials.json \
     --iam-account=bates-labeler-ai@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

4. **Configure Bates-Labeler**:
   ```bash
   export AI_PROVIDER=google
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/bates-labeler-credentials.json"

   # Optional: Choose model
   export AI_MODEL="gemini-pro"  # or "gemini-1.5-pro", "gemini-flash-1.5"
   ```

5. **Secure Credentials**:
   ```bash
   # Restrict permissions
   chmod 600 ~/bates-labeler-credentials.json

   # Add to .gitignore
   echo "*-credentials.json" >> .gitignore
   ```

6. **Test Integration**:
   ```bash
   # Install Google Cloud SDK if needed
   pip install google-cloud-aiplatform

   # Test authentication
   gcloud auth application-default login
   ```

**Pricing** (approximate):
- Gemini Pro: $0.00025/1K characters input, $0.00050/1K output
- Gemini 1.5 Pro: $0.0025/1K input, $0.0075/1K output
- Check current pricing: https://cloud.google.com/vertex-ai/pricing

### Anthropic Claude

**Why Anthropic?**
- Direct access to Claude models
- Privacy-focused design
- Constitutional AI for safety
- Long context windows (200K+ tokens)

**Setup Steps**:

1. **Create Account**:
   - Visit https://console.anthropic.com
   - Sign up with email

2. **Generate API Key**:
   - Navigate to "API Keys" in console
   - Click "Create Key"
   - Copy the key (starts with `sk-ant-`)

3. **Configure Bates-Labeler**:
   ```bash
   export AI_PROVIDER=anthropic
   export ANTHROPIC_API_KEY="sk-ant-your-key-here"

   # Optional: Choose model
   export AI_MODEL="claude-3-haiku-20240307"     # Fast, cheap
   export AI_MODEL="claude-3-5-sonnet-20241022"  # Balanced
   export AI_MODEL="claude-3-opus-20240229"      # Premium
   ```

4. **Test Integration**:
   ```bash
   # Install Anthropic SDK
   pip install anthropic

   # Test API key
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "content-type: application/json" \
     -d '{
       "model": "claude-3-haiku-20240307",
       "max_tokens": 1024,
       "messages": [{"role": "user", "content": "Hello"}]
     }'
   ```

**Pricing** (as of 2025):
- Claude Haiku: $0.00025/1K input, $0.00125/1K output
- Claude Sonnet: $0.003/1K input, $0.015/1K output
- Claude Opus: $0.015/1K input, $0.075/1K output

Check current pricing: https://www.anthropic.com/pricing

## 🧪 Testing Your Integration

### Quick Test (Command Line)

```bash
# Create test script
cat > test_ai.py << 'EOF'
from bates_labeler.ai_analysis import AIAnalysisConfig, get_analyzer

# Load configuration from environment
config = AIAnalysisConfig()

print(f"AI Enabled: {config.enabled}")
print(f"Provider: {config.provider}")
print(f"Configuration Valid: {config.validate()}")

# Test analyzer
if config.validate():
    analyzer = get_analyzer()
    print(f"Analyzer Ready: {analyzer.is_enabled()}")

    # Test analysis
    test_text = "This is a sample legal document for testing AI analysis capabilities."
    result = analyzer.extract_metadata(test_text)

    print(f"\nTest Analysis Result:")
    print(f"Document Type: {result.get('document_type', 'unknown')}")
    print(f"Language: {result.get('language', 'unknown')}")
    print(f"Sentiment: {result.get('sentiment', 'unknown')}")
else:
    print("❌ Configuration is invalid. Check your API keys.")
EOF

# Run test
python test_ai.py
```

### Integration Test (Full Workflow)

```bash
# Create sample PDF for testing
echo "This is a test legal document." > test.txt
# Convert to PDF (requires pdflatex or similar)
# Or use any existing PDF

# Test with Bates numbering
poetry run bates \
  --input test.pdf \
  --bates-prefix "TEST-" \
  --output test_bates.pdf

# Check for AI analysis in output
# Results will be logged to console
```

### Web UI Test

1. **Launch Web UI**:
   ```bash
   poetry run streamlit run app.py
   ```

2. **Configure AI**:
   - Open sidebar → Advanced Options
   - Enable AI Analysis
   - Select provider
   - Enter API key

3. **Upload Test Document**:
   - Upload a sample PDF
   - Process with AI analysis enabled
   - Check "AI Document Analysis Results" section

4. **Verify Results**:
   - Check for discrimination findings
   - Review problematic content alerts
   - Examine metadata extraction

## 🐛 Troubleshooting

### Issue: "AI analysis not enabled or configured"

**Cause**: Missing API key or disabled feature

**Solution**:
```bash
# Check environment
echo $AI_ANALYSIS_ENABLED  # Should be "true"
echo $AI_PROVIDER          # Should be "openrouter", "google", or "anthropic"
echo $OPENROUTER_API_KEY   # Should show key (if using OpenRouter)

# Re-export if needed
export AI_ANALYSIS_ENABLED=true
export AI_PROVIDER=openrouter
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

### Issue: "Invalid API key"

**Cause**: Malformed or incorrect API key

**Solution**:
```bash
# Verify key format
# OpenRouter: starts with "sk-or-v1-"
# Anthropic: starts with "sk-ant-"
# Google: JSON file path

# Test key directly
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"

# If fails, regenerate key from provider dashboard
```

### Issue: "Module not found: ai_analysis"

**Cause**: Missing dependencies or incorrect import

**Solution**:
```bash
# Reinstall with all dependencies
poetry install

# Or with pip
pip install -e .

# Verify installation
python -c "from bates_labeler.ai_analysis import AIAnalyzer; print('OK')"
```

### Issue: "Rate limit exceeded"

**Cause**: Too many API requests

**Solution**:
```bash
# Wait and retry
sleep 60

# Enable caching to reduce requests
export AI_CACHE_ENABLED=true
export AI_CACHE_TTL_HOURS=24

# Use smaller batch sizes
# Process fewer documents at once
```

### Issue: No analysis results appearing

**Cause**: API errors or silent failures

**Solution**:
```bash
# Enable debug logging
python << EOF
import logging
logging.basicConfig(level=logging.DEBUG)

from bates_labeler import BatesNumberer

numberer = BatesNumberer(
    ai_analysis_enabled=True,
    ai_api_key="your-key"
)
numberer.process_pdf("test.pdf", "output.pdf")
EOF

# Check logs for detailed error messages
```

### Issue: Google Cloud authentication errors

**Cause**: Incorrect credentials or permissions

**Solution**:
```bash
# Verify credentials file exists
ls -la $GOOGLE_APPLICATION_CREDENTIALS

# Check file permissions
chmod 600 $GOOGLE_APPLICATION_CREDENTIALS

# Test authentication
gcloud auth application-default login

# Verify service account permissions
gcloud projects get-iam-policy $GOOGLE_CLOUD_PROJECT \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:bates-labeler-ai@*"
```

## 📊 Verification Checklist

Before deploying AI analysis in production:

- [ ] API key is valid and tested
- [ ] Environment variables are set correctly
- [ ] .env file is in .gitignore
- [ ] Test analysis completes successfully
- [ ] Caching is enabled (if desired)
- [ ] Cost monitoring is set up
- [ ] Error handling is working
- [ ] Logs show successful API calls
- [ ] Results are meaningful and accurate
- [ ] Privacy/compliance requirements are met

## 🚀 Next Steps

Once setup is complete:

1. **Read the Features Guide**: [AI_FEATURES.md](AI_FEATURES.md)
2. **Process sample documents** to verify accuracy
3. **Tune thresholds** based on your use case
4. **Monitor API costs** during initial rollout
5. **Set up monitoring/alerting** for production use
6. **Document your configuration** for team members
7. **Train users** on interpreting AI results

## 📞 Support

- **Documentation**: [AI_FEATURES.md](AI_FEATURES.md)
- **GitHub Issues**: https://github.com/thepingdoctor/Bates-Labeler/issues
- **Provider Support**:
  - OpenRouter: https://openrouter.ai/docs
  - Google Cloud: https://cloud.google.com/support
  - Anthropic: https://support.anthropic.com

---

**Security Note**: Never commit API keys to version control. Always use environment variables or secure credential management systems.
