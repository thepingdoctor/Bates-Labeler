# AI Document Analysis Features

## Overview

Bates-Labeler includes powerful AI-powered document analysis capabilities that help legal professionals identify discrimination patterns, problematic content, and extract valuable metadata from PDF documents. This feature leverages leading AI providers to provide intelligent document insights during the Bates numbering workflow.

## 🚀 Key Capabilities

### 1. Discrimination Detection

Automatically identify potential discriminatory language and patterns including:

- **Race, ethnicity, and national origin** - Detect racially biased language or references
- **Gender and sexual orientation** - Identify gender-based discrimination or LGBTQ+ bias
- **Age discrimination** - Flag ageist language or practices
- **Disability discrimination** - Detect ableist content or ADA violations
- **Religious discrimination** - Identify religious bias or intolerance
- **Other protected characteristics** - Catch additional discrimination patterns

Each finding includes:
- **Confidence score** (0-1 scale) indicating detection reliability
- **Severity classification** (low, medium, high, critical)
- **Specific evidence** with exact phrases or patterns identified
- **Category tagging** for easy filtering and review
- **Detailed explanation** of why content was flagged

### 2. Problematic Content Identification

Flag potentially sensitive, inappropriate, or legally concerning content:

- **Offensive or inflammatory language** - Detect hostile or unprofessional communication
- **Potential harassment or threats** - Identify threatening or intimidating language
- **Confidential information exposure** - Find unintended disclosure of sensitive data
- **Misleading or fraudulent statements** - Detect potentially false or deceptive claims
- **Privacy violations** - Identify unauthorized disclosure of personal information
- **Ethical concerns** - Flag ethically questionable content

Each issue includes:
- **Issue type classification** for categorization
- **Severity rating** (low/medium/high/critical)
- **Location markers** pointing to problematic sections
- **Actionable recommendations** for addressing the issue
- **Contextual explanation** of the concern

### 3. Metadata Extraction

Automatically extract structured information from documents:

- **Document type classification** (contract, email, memo, report, legal brief, etc.)
- **Key entities** - Extract important people, organizations, and places
- **Significant dates** - Identify critical dates mentioned in the document
- **Main topics and subjects** - Determine document themes
- **Language detection** - Identify the primary language
- **Sentiment analysis** (positive, negative, neutral)
- **Brief summary** - 1-2 sentence overview of document content
- **Important keywords** - Extract key terms and phrases

## 🔧 Supported AI Providers

### OpenRouter (Recommended)

**Best for**: Cost-effective access to multiple AI models with unified API

- **Access**: https://openrouter.ai
- **Default model**: `anthropic/claude-3-haiku` (fast, accurate, economical)
- **Pricing**: Pay-as-you-go, typically $0.001-$0.025 per 1000 tokens
- **Advantages**:
  - Access to 100+ models from one API
  - Automatic model fallback if one fails
  - Competitive pricing
  - Simple API key setup

**Setup**:
1. Create account at https://openrouter.ai
2. Generate API key from dashboard
3. Add to environment: `export OPENROUTER_API_KEY="sk-or-v1-..."`

### Google Cloud Vertex AI

**Best for**: Enterprise deployments with Google Cloud infrastructure

- **Access**: Google Cloud Console → Vertex AI
- **Default model**: `gemini-pro`
- **Pricing**: Pay-as-you-go, varies by model and usage
- **Advantages**:
  - Enterprise SLA and support
  - Integration with Google Cloud ecosystem
  - Advanced security and compliance features
  - Multimodal capabilities

**Setup**:
1. Enable Vertex AI API in Google Cloud Console
2. Create service account with Vertex AI permissions
3. Download JSON credentials file
4. Set environment:
   ```bash
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
   ```

### Anthropic Claude

**Best for**: Direct access to Claude models with advanced reasoning

- **Access**: https://console.anthropic.com
- **Default model**: `claude-3-haiku-20240307`
- **Pricing**: Pay-as-you-go, competitive rates
- **Advantages**:
  - State-of-the-art reasoning and analysis
  - Long context windows (200K+ tokens)
  - Direct API access to Claude
  - Strong privacy and security

**Setup**:
1. Create account at https://console.anthropic.com
2. Generate API key
3. Add to environment: `export ANTHROPIC_API_KEY="sk-ant-..."`

## 💻 Configuration

### Environment Variables

```bash
# Enable AI analysis
export AI_ANALYSIS_ENABLED=true

# Select provider (openrouter, google, anthropic)
export AI_PROVIDER=openrouter

# Provider-specific API keys
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Model configuration (optional - uses sensible defaults)
export AI_MODEL="anthropic/claude-3-haiku"  # For OpenRouter
export AI_MAX_TOKENS=1000                    # Maximum response length
export AI_TEMPERATURE=0.3                    # Lower = more consistent

# Caching configuration (optional)
export AI_CACHE_ENABLED=true
export AI_CACHE_TTL_HOURS=24

# Analysis thresholds (optional)
export AI_DISCRIMINATION_THRESHOLD=0.7  # Confidence threshold (0-1)
export AI_PROBLEMATIC_THRESHOLD=0.6     # Confidence threshold (0-1)
```

### Sample .env File

Create a `.env` file in your project directory:

```env
# AI Analysis Configuration
AI_ANALYSIS_ENABLED=true
AI_PROVIDER=openrouter

# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-v1-1234567890abcdef1234567890abcdef

# Model Settings
AI_MODEL=anthropic/claude-3-haiku
AI_MAX_TOKENS=1000
AI_TEMPERATURE=0.3

# Caching
AI_CACHE_ENABLED=true
AI_CACHE_TTL_HOURS=24

# Thresholds
AI_DISCRIMINATION_THRESHOLD=0.7
AI_PROBLEMATIC_THRESHOLD=0.6
```

## 🌐 Web UI Usage

### Enabling AI Analysis

1. **Navigate to Advanced Options** in the sidebar
2. **Check "Enable AI Analysis"** checkbox
3. **Select your AI Provider** from dropdown
4. **Enter your API Key** (secure, not stored)
5. **Choose analysis types**:
   - ✅ Detect Discrimination Patterns
   - ✅ Identify Problematic Content
   - ✅ Extract Metadata
6. **Upload and process PDFs** as normal

### Viewing Analysis Results

After processing, AI analysis results appear in a dedicated section:

#### Discrimination Findings
Shown with color-coded severity indicators:
- 🔴 **Critical** - Immediate attention required
- 🟠 **High** - Significant concern
- 🟡 **Medium** - Moderate concern
- 🟢 **Low** - Minor issue or false positive

#### Problematic Content
Each issue displays:
- Type of problem (harassment, threat, bias, etc.)
- Severity level with visual indicator
- Description of the issue
- Recommended actions

#### Metadata Insights
Structured information including:
- Document classification
- Key entities and dates
- Topics and keywords
- Summary and sentiment

### Exporting Results

**Download Analysis Report (JSON)**:
- Click "Export AI Analysis Results"
- Downloads timestamped JSON file with complete findings
- Use for record-keeping or further processing

## ⌨️ Command Line Usage

### Basic Usage

```bash
# Enable AI analysis via environment variables
export AI_ANALYSIS_ENABLED=true
export AI_PROVIDER=openrouter
export OPENROUTER_API_KEY="your-key-here"

# Process with AI analysis
poetry run bates --input document.pdf --bates-prefix "CASE-"
```

### Programmatic Usage

```python
from bates_labeler import BatesNumberer
from bates_labeler.ai_analysis import AIAnalyzer, AIAnalysisConfig

# Option 1: Enable AI in BatesNumberer
numberer = BatesNumberer(
    prefix="CASE-",
    ai_analysis_enabled=True,
    ai_provider="openrouter",
    ai_api_key="your-key-here",
    ai_analysis_callback=lambda result: print(result)
)

# Process PDF with AI analysis
result = numberer.process_pdf(
    "input.pdf",
    "output.pdf",
    return_metadata=True
)

# Access AI analysis results
if result['ai_analysis']:
    print(f"Discrimination detected: {result['ai_analysis']['has_discrimination']}")
    print(f"Problematic content: {len(result['ai_analysis']['issues'])}")

# Option 2: Use AIAnalyzer directly
config = AIAnalysisConfig()  # Loads from environment
analyzer = AIAnalyzer(config)

# Extract and analyze text
text = numberer._extract_text_from_pdf("document.pdf")
discrimination_result = analyzer.detect_discrimination(text)
problematic_result = analyzer.identify_problematic_content(text)
metadata_result = analyzer.extract_metadata(text)

print(f"Confidence: {discrimination_result['confidence']}")
print(f"Categories: {discrimination_result['categories']}")
print(f"Evidence: {discrimination_result['evidence']}")
```

### Analysis Callback Function

Handle analysis results in real-time:

```python
def analysis_callback(result):
    """Process AI analysis results as they're generated."""

    # Check for discrimination
    if result.get('has_discrimination'):
        print(f"⚠️ Discrimination detected!")
        print(f"Categories: {', '.join(result['categories'])}")
        print(f"Severity: {result['severity']}")
        for evidence in result['evidence']:
            print(f"  - {evidence}")

    # Check for problematic content
    if result.get('has_issues'):
        print(f"⚠️ Problematic content found!")
        for issue in result['issues']:
            print(f"  {issue['severity']}: {issue['description']}")

    # Log metadata
    if result.get('document_type'):
        print(f"Document type: {result['document_type']}")
        print(f"Summary: {result.get('summary', 'N/A')}")

numberer = BatesNumberer(
    prefix="CASE-",
    ai_analysis_enabled=True,
    ai_api_key="your-key",
    ai_analysis_callback=analysis_callback
)
```

## 💰 API Cost Considerations

### Cost Estimation

Average costs per document (using OpenRouter with Claude Haiku):

| Document Size | Estimated Pages | Tokens | Cost (USD) |
|--------------|-----------------|--------|------------|
| Small | 1-10 pages | ~2,000 | $0.001-$0.005 |
| Medium | 11-50 pages | ~10,000 | $0.01-$0.025 |
| Large | 51-200 pages | ~40,000 | $0.04-$0.10 |
| Very Large | 200+ pages | ~100,000+ | $0.10-$0.50+ |

**Note**: Costs vary by provider and model. Check current pricing at:
- OpenRouter: https://openrouter.ai/docs#models
- Google Cloud: https://cloud.google.com/vertex-ai/pricing
- Anthropic: https://www.anthropic.com/pricing

### Cost Optimization Strategies

1. **Enable Caching** (default: enabled)
   - Avoids re-analyzing unchanged documents
   - 24-hour default TTL
   - Reduces API calls by 50-80%

2. **Use Efficient Models**
   - Claude Haiku (fastest, cheapest)
   - Gemini Flash (balanced)
   - Claude Sonnet (premium)

3. **Selective Analysis**
   - Enable only needed analysis types
   - Skip metadata if not required
   - Use discrimination detection on high-risk documents only

4. **Batch Processing**
   - Process multiple documents in single session
   - Cache hits across similar documents
   - Amortize API overhead

5. **Text Length Limits**
   - AI analysis automatically limits text to first 2000 characters per page
   - Sufficient for detecting patterns while reducing costs
   - Override via configuration if needed

## 🔒 Privacy and Data Handling

### Data Flow

1. **Text Extraction**: PDF text is extracted locally
2. **API Transmission**: Only text content (not PDFs) sent to AI provider
3. **Analysis**: AI provider processes text and returns JSON results
4. **Storage**: Results cached locally (optional, default: enabled)
5. **No Retention**: AI providers don't retain data (check provider policies)

### Security Best Practices

1. **Environment Variables**: Never hardcode API keys
   ```bash
   # Good ✅
   export OPENROUTER_API_KEY="sk-..."

   # Bad ❌
   ai_api_key = "sk-12345..."  # Don't commit to git!
   ```

2. **Credential Protection**:
   - Use `.env` files (add to `.gitignore`)
   - Restrict file permissions: `chmod 600 .env`
   - Rotate keys regularly

3. **Provider Selection**:
   - **OpenRouter**: Multi-model access, no data retention
   - **Google Cloud**: Enterprise SLA, data residency options
   - **Anthropic**: Privacy-focused, constitutional AI

4. **Local Processing**: Consider local AI models for highly sensitive documents
   - Ollama integration (planned)
   - Local LLM support (future enhancement)

### Compliance Considerations

- **GDPR**: Review provider data processing agreements
- **HIPAA**: Use HIPAA-compliant AI services if analyzing medical records
- **Attorney-Client Privilege**: Ensure provider agreements protect privileged content
- **Data Sovereignty**: Check where AI providers process data

## 🐛 Troubleshooting

### Common Issues

#### 1. API Key Not Working

**Symptoms**: "Invalid API key" or authentication errors

**Solutions**:
```bash
# Verify key format
echo $OPENROUTER_API_KEY  # Should start with "sk-or-v1-"
echo $ANTHROPIC_API_KEY   # Should start with "sk-ant-"

# Test key with curl
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"

# Re-export if needed
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

#### 2. Rate Limiting

**Symptoms**: "Rate limit exceeded" errors

**Solutions**:
- Wait 60 seconds and retry
- Check provider quota/limits
- Use exponential backoff for batch processing
- Consider upgrading account tier

#### 3. Timeout Errors

**Symptoms**: "Request timed out" or slow analysis

**Solutions**:
```python
# Increase timeout (default: 30 seconds)
config = AIAnalysisConfig()
# Custom timeout handled by provider implementations
```

#### 4. Malformed Responses

**Symptoms**: JSON parsing errors or unexpected format

**Solutions**:
- Verify model supports JSON output
- Check AI_MAX_TOKENS setting (default: 1000)
- Try alternative model
- Review provider status page

#### 5. No Analysis Results

**Symptoms**: Processing completes but no AI results

**Solutions**:
```bash
# Verify AI is enabled
export AI_ANALYSIS_ENABLED=true

# Check configuration
python -c "from bates_labeler.ai_analysis import AIAnalysisConfig; c=AIAnalysisConfig(); print(f'Enabled: {c.enabled}, Provider: {c.provider}, Valid: {c.validate()}')"

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 6. Cache Issues

**Symptoms**: Stale results or unexpected cached responses

**Solutions**:
```python
# Clear cache programmatically
from bates_labeler.ai_analysis import get_analyzer

analyzer = get_analyzer()
analyzer.clear_cache()

# Or disable caching
export AI_CACHE_ENABLED=false
```

### Error Messages Explained

| Error Message | Meaning | Solution |
|--------------|---------|----------|
| `AI analysis not enabled or configured` | Missing API key or disabled | Set `AI_ANALYSIS_ENABLED=true` and add API key |
| `No text provided for analysis` | Empty PDF or extraction failed | Verify PDF contains text, check OCR if scanned |
| `Provider initialization failed` | Invalid credentials | Check API key format and validity |
| `Analysis failed: <error>` | API error | Check provider status, retry with backoff |
| `Failed to parse <type> analysis response` | Malformed JSON | Try different model, check token limits |

### Getting Help

If issues persist:

1. **Check Logs**: Review console output for detailed error messages
2. **Provider Status**: Check provider status pages
   - OpenRouter: https://status.openrouter.ai
   - Google Cloud: https://status.cloud.google.com
   - Anthropic: https://status.anthropic.com
3. **Test Independently**: Use provider's API directly to isolate issues
4. **Update Dependencies**: Ensure latest version of bates-labeler
5. **File Issue**: https://github.com/thepingdoctor/Bates-Labeler/issues

## 📊 Analysis Output Schema

### Discrimination Detection Response

```json
{
  "has_discrimination": true,
  "confidence": 0.95,
  "categories": ["racial", "gender"],
  "evidence": [
    "racially charged language on page 3",
    "gender-based stereotyping in paragraph 2"
  ],
  "severity": "high",
  "explanation": "Document contains discriminatory language targeting multiple protected classes",
  "analysis_type": "discrimination",
  "timestamp": "2025-10-27T19:40:00.123Z"
}
```

### Problematic Content Response

```json
{
  "has_issues": true,
  "confidence": 0.88,
  "issues": [
    {
      "type": "harassment",
      "severity": "high",
      "description": "Threatening language detected in email thread"
    },
    {
      "type": "bias",
      "severity": "medium",
      "description": "Unconscious bias in performance evaluation"
    }
  ],
  "locations": ["page 2, paragraph 3", "page 5, section 2.1"],
  "severity": "high",
  "recommendations": [
    "Review threatening language with legal counsel",
    "Consider bias training for evaluators",
    "Redact or modify problematic sections"
  ],
  "explanation": "Multiple issues identified requiring attention",
  "analysis_type": "problematic_content",
  "timestamp": "2025-10-27T19:40:00.456Z"
}
```

### Metadata Extraction Response

```json
{
  "document_type": "contract",
  "key_entities": [
    "Acme Corporation",
    "John Smith",
    "New York",
    "Department of Labor"
  ],
  "dates": [
    "2025-01-15",
    "2025-12-31"
  ],
  "topics": [
    "Employment Agreement",
    "Non-Compete Clause",
    "Intellectual Property"
  ],
  "language": "en",
  "sentiment": "neutral",
  "summary": "Employment contract between Acme Corporation and John Smith detailing compensation, responsibilities, and non-compete terms.",
  "keywords": [
    "employment",
    "compensation",
    "confidentiality",
    "termination",
    "intellectual property"
  ],
  "analysis_type": "metadata",
  "timestamp": "2025-10-27T19:40:00.789Z"
}
```

## 🔄 Advanced Features

### Custom Analysis Configuration

```python
from bates_labeler.ai_analysis import AIAnalysisConfig

# Create custom configuration
config = AIAnalysisConfig()
config.provider = 'anthropic'
config.anthropic_api_key = 'sk-ant-...'
config.default_model = 'claude-3-opus-20240229'  # Premium model
config.max_tokens = 2000  # Longer responses
config.temperature = 0.1  # More deterministic
config.cache_enabled = True
config.cache_ttl_hours = 48  # Extended caching

# Use custom config
from bates_labeler.ai_analysis import AIAnalyzer
analyzer = AIAnalyzer(config)
```

### Batch Analysis

```python
import glob
from bates_labeler.ai_analysis import get_analyzer

analyzer = get_analyzer()
results = []

for pdf_file in glob.glob("discovery/*.pdf"):
    # Extract text
    text = extract_text_from_pdf(pdf_file)  # Your extraction function

    # Analyze
    result = analyzer.analyze_document(text, 'discrimination')
    results.append({
        'file': pdf_file,
        'result': result
    })

# Generate report
import json
with open('analysis_report.json', 'w') as f:
    json.dump(results, f, indent=2)
```

### Integration with Processing Pipeline

```python
from bates_labeler import BatesNumberer

def custom_analysis_handler(analysis_result):
    """Custom handler for AI analysis results."""

    # Log high-severity findings
    if analysis_result.get('severity') in ['high', 'critical']:
        log_to_security_system(analysis_result)

    # Notify stakeholders
    if analysis_result.get('has_discrimination'):
        send_alert_email(analysis_result)

    # Store in database
    save_to_database(analysis_result)

# Use in BatesNumberer
numberer = BatesNumberer(
    prefix="CASE-",
    ai_analysis_enabled=True,
    ai_analysis_callback=custom_analysis_handler
)
```

## 🚀 Best Practices

1. **Start Small**: Test AI analysis on sample documents first
2. **Review Results**: AI is not perfect - manually review high-severity findings
3. **Tune Thresholds**: Adjust confidence thresholds based on your needs
4. **Cache Wisely**: Balance cost savings vs. freshness of analysis
5. **Secure Credentials**: Never commit API keys to version control
6. **Monitor Costs**: Track API usage, especially for large batches
7. **Provider Selection**: Choose provider based on privacy, cost, and accuracy needs
8. **Batch Efficiently**: Process related documents together for cost optimization
9. **Log Everything**: Maintain audit trails of analysis results
10. **Stay Updated**: Check for model updates and new capabilities

## 📚 Additional Resources

- **OpenRouter Documentation**: https://openrouter.ai/docs
- **Google Cloud Vertex AI**: https://cloud.google.com/vertex-ai/docs
- **Anthropic Claude API**: https://docs.anthropic.com
- **Bates-Labeler GitHub**: https://github.com/thepingdoctor/Bates-Labeler
- **Issue Tracker**: https://github.com/thepingdoctor/Bates-Labeler/issues

---

**Note**: AI analysis is a powerful tool but should not replace human judgment, especially in legal contexts. Always review AI-generated findings with qualified professionals.
