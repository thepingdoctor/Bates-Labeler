# AI Analysis Module Documentation

## Overview

The AI Analysis module (`bates_labeler/ai_analysis.py`) provides intelligent document analysis capabilities for Bates-Labeler, including discrimination detection, problematic content identification, and metadata extraction.

## Features

### Multi-Provider Support
- **OpenRouter**: Access to multiple AI models through a unified API
- **Google Cloud**: Vertex AI and Gemini integration
- **Anthropic**: Direct Claude API integration

### Analysis Capabilities
1. **Discrimination Detection**: Identifies potential discrimination based on protected characteristics
2. **Problematic Content**: Detects offensive language, privacy violations, ethical concerns
3. **Metadata Extraction**: Extracts document type, entities, dates, topics, sentiment

### Performance Optimizations
- **Intelligent Caching**: In-memory cache with configurable TTL (default 24 hours)
- **Cost Reduction**: Cache prevents duplicate API calls for same content
- **Graceful Degradation**: Continues working even if AI is disabled or fails

## Configuration

### Environment Variables

```bash
# Core Configuration
AI_ANALYSIS_ENABLED=true              # Enable/disable AI features
AI_PROVIDER=openrouter                # Provider: openrouter|google|anthropic

# Provider API Keys
OPENROUTER_API_KEY=your_key_here      # OpenRouter API key
GOOGLE_CLOUD_PROJECT=project-id       # Google Cloud project
GOOGLE_APPLICATION_CREDENTIALS=/path  # Google credentials file
ANTHROPIC_API_KEY=your_key_here       # Anthropic API key

# Model Configuration
AI_MODEL=anthropic/claude-3-haiku     # Model to use (provider-specific)
AI_MAX_TOKENS=1000                    # Maximum response tokens
AI_TEMPERATURE=0.3                    # Temperature (0-1, lower = more focused)

# Cache Configuration
AI_CACHE_ENABLED=true                 # Enable response caching
AI_CACHE_TTL_HOURS=24                 # Cache time-to-live in hours

# Analysis Thresholds
AI_DISCRIMINATION_THRESHOLD=0.7       # Confidence threshold for discrimination
AI_PROBLEMATIC_THRESHOLD=0.6          # Confidence threshold for problematic content
```

### Default Models by Provider

- **OpenRouter**: `anthropic/claude-3-haiku` (fast, cost-effective)
- **Google Cloud**: `gemini-pro`
- **Anthropic**: `claude-3-haiku-20240307`

## Installation

### Base Installation

```bash
# Already included in bates-labeler
pip install bates-labeler
```

### Provider-Specific Dependencies

```bash
# OpenRouter (uses standard requests)
pip install requests

# Google Cloud
pip install google-cloud-aiplatform

# Anthropic
pip install anthropic
```

## Usage

### Basic Usage

```python
from bates_labeler.ai_analysis import AIAnalyzer, AIAnalysisConfig

# Initialize with configuration
config = AIAnalysisConfig()
analyzer = AIAnalyzer(config)

# Check if enabled
if analyzer.is_enabled():
    # Analyze document
    text = "Your document text here..."

    # Detect discrimination
    result = analyzer.detect_discrimination(text)
    print(f"Has discrimination: {result['has_discrimination']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Categories: {result['categories']}")

    # Identify problematic content
    result = analyzer.identify_problematic_content(text)
    print(f"Has issues: {result['has_issues']}")
    print(f"Severity: {result['severity']}")

    # Extract metadata
    result = analyzer.extract_metadata(text)
    print(f"Document type: {result['document_type']}")
    print(f"Topics: {result['topics']}")
```

### Convenience Functions

```python
from bates_labeler.ai_analysis import (
    detect_discrimination,
    identify_problematic_content,
    extract_metadata,
    is_ai_enabled
)

# Check if AI is enabled
if is_ai_enabled():
    text = "Document text..."

    # Use convenience functions (auto-manages global analyzer)
    discrimination = detect_discrimination(text)
    problematic = identify_problematic_content(text)
    metadata = extract_metadata(text)
```

### Integration with Bates Processing

```python
from bates_labeler.core import BatesNumberer
from bates_labeler.ai_analysis import AIAnalyzer
from pypdf import PdfReader

# Initialize AI analyzer
analyzer = AIAnalyzer()

# Process PDF
pdf_path = "document.pdf"
reader = PdfReader(pdf_path)

# Analyze each page
for page_num, page in enumerate(reader.pages):
    text = page.extract_text()

    if analyzer.is_enabled():
        # Check for discrimination
        disc_result = analyzer.detect_discrimination(text)
        if disc_result.get('has_discrimination'):
            print(f"⚠️ Page {page_num + 1}: Potential discrimination detected")
            print(f"   Confidence: {disc_result['confidence']:.2%}")
            print(f"   Categories: {', '.join(disc_result['categories'])}")

        # Check for problematic content
        prob_result = analyzer.identify_problematic_content(text)
        if prob_result.get('has_issues'):
            print(f"⚠️ Page {page_num + 1}: Problematic content detected")
            print(f"   Severity: {prob_result['severity']}")
            print(f"   Issues: {', '.join(prob_result['issues'])}")
```

## Response Formats

### Discrimination Detection Response

```json
{
  "has_discrimination": true,
  "confidence": 0.85,
  "categories": ["race", "gender"],
  "evidence": [
    "phrase indicating bias",
    "another problematic phrase"
  ],
  "severity": "high",
  "explanation": "Brief explanation of findings",
  "analysis_type": "discrimination",
  "timestamp": "2025-10-27T19:45:00.000Z"
}
```

### Problematic Content Response

```json
{
  "has_issues": true,
  "confidence": 0.75,
  "issues": ["offensive_language", "privacy_violation"],
  "locations": ["paragraph 2", "section 3"],
  "severity": "medium",
  "recommendations": [
    "Review and redact offensive language",
    "Remove personal information"
  ],
  "explanation": "Brief explanation of issues",
  "analysis_type": "problematic_content",
  "timestamp": "2025-10-27T19:45:00.000Z"
}
```

### Metadata Extraction Response

```json
{
  "document_type": "contract",
  "key_entities": ["Company A", "John Doe", "New York"],
  "dates": ["2025-01-15", "2025-12-31"],
  "topics": ["employment", "compensation", "benefits"],
  "language": "en",
  "sentiment": "neutral",
  "summary": "Employment contract between Company A and John Doe",
  "keywords": ["employment", "salary", "benefits", "term"],
  "analysis_type": "metadata",
  "timestamp": "2025-10-27T19:45:00.000Z"
}
```

## Caching Behavior

### Cache Key Generation
- SHA-256 hash of `analysis_type:text`
- Ensures consistent cache keys for identical content

### Cache TTL
- Default: 24 hours
- Configurable via `AI_CACHE_TTL_HOURS`
- Automatically expires old entries

### Cache Management

```python
# Get cache statistics
stats = analyzer.get_cache_stats()
print(f"Cached entries: {stats['total_entries']}")
print(f"Memory size: {stats['memory_size_bytes']} bytes")

# Clear cache manually
analyzer.clear_cache()
```

## Error Handling

### Graceful Degradation
- Returns safe default responses on API failures
- Logs errors for debugging
- Never crashes the main application

### Error Response Format

```json
{
  "error": true,
  "message": "Error description",
  "timestamp": "2025-10-27T19:45:00.000Z"
}
```

### Default Safe Responses
- **Discrimination**: `has_discrimination: false, confidence: 0.0`
- **Problematic**: `has_issues: false, confidence: 0.0`
- **Metadata**: Returns "unknown" for most fields

## Performance Considerations

### API Rate Limits
- Respect provider rate limits
- Use caching to minimize API calls
- Consider batch processing for multiple documents

### Token Usage
- Default: 1000 max tokens per request
- Truncates input text to first 2000 characters
- Adjust `AI_MAX_TOKENS` based on needs

### Cost Optimization
- **Enable caching**: Reduces duplicate API calls by 60-90%
- **Use Haiku models**: Fast and cost-effective for most tasks
- **Adjust temperature**: Lower values (0.1-0.3) for consistent results
- **Batch processing**: Analyze multiple pages in one session

## Security Considerations

### API Key Management
- Never commit API keys to version control
- Use environment variables or secure vaults
- Rotate keys periodically
- Monitor usage for anomalies

### Data Privacy
- Text is sent to third-party AI providers
- Consider data sensitivity before enabling AI analysis
- Review provider privacy policies
- Use on-premise solutions for sensitive documents

### Input Validation
- Text is truncated to prevent token overflow
- No user-provided prompts to prevent injection
- Sanitized JSON parsing with error handling

## Testing

### Unit Testing

```python
import pytest
from bates_labeler.ai_analysis import AIAnalyzer, AIAnalysisConfig, CacheManager

def test_cache_manager():
    cache = CacheManager(ttl_hours=1)

    # Test set and get
    cache.set("test text", "discrimination", {"result": "test"})
    result = cache.get("test text", "discrimination")
    assert result == {"result": "test"}

    # Test cache miss
    result = cache.get("other text", "discrimination")
    assert result is None

def test_config_validation():
    config = AIAnalysisConfig()
    config.enabled = True
    config.provider = "openrouter"
    config.openrouter_api_key = "test_key"
    assert config.validate() is True

def test_analyzer_initialization():
    analyzer = AIAnalyzer()
    # Should work even if disabled
    assert analyzer is not None
```

### Integration Testing

```bash
# Set test environment
export AI_ANALYSIS_ENABLED=true
export AI_PROVIDER=openrouter
export OPENROUTER_API_KEY=your_test_key

# Run test
python -m bates_labeler.ai_analysis
```

## Troubleshooting

### AI Analysis Not Working

1. **Check if enabled**: Verify `AI_ANALYSIS_ENABLED=true`
2. **Verify credentials**: Ensure API key is set correctly
3. **Test connectivity**: Check network access to provider APIs
4. **Review logs**: Check application logs for error messages

### Poor Analysis Quality

1. **Adjust temperature**: Lower for more focused results (0.1-0.3)
2. **Increase max_tokens**: Allow longer, more detailed responses
3. **Try different model**: Some models excel at specific tasks
4. **Provide more context**: Longer text samples improve accuracy

### High API Costs

1. **Enable caching**: Set `AI_CACHE_ENABLED=true`
2. **Increase cache TTL**: Longer cache retention
3. **Use cheaper models**: Haiku/Gemini Flash for basic tasks
4. **Batch similar documents**: Process similar content together

## Roadmap

### Planned Features
- [ ] Support for local/offline models (Ollama, llama.cpp)
- [ ] Batch analysis API for multiple documents
- [ ] Custom prompt templates
- [ ] Fine-tuning support for specialized domains
- [ ] Async/parallel processing
- [ ] Webhook notifications for analysis completion
- [ ] Integration with vector databases for semantic search

## License

Same as Bates-Labeler main project (MIT License)

## Support

- GitHub Issues: https://github.com/bates-labeler/issues
- Documentation: https://github.com/bates-labeler
- Examples: See `/examples` directory
