"""AI-powered document analysis module for Bates-Labeler.

This module provides AI-based document analysis capabilities including:
- Discrimination detection
- Problematic content identification
- Metadata extraction
- Multi-provider support (OpenRouter, Google Cloud, Anthropic)
- Caching layer for cost optimization
- Graceful degradation and error handling
"""

import os
import json
import hashlib
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List
from functools import lru_cache
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAnalysisConfig:
    """Configuration management for AI analysis."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self.enabled = self._get_bool_env('AI_ANALYSIS_ENABLED', False)
        self.provider = os.getenv('AI_PROVIDER', 'openrouter').lower()

        # Provider-specific API keys
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.google_cloud_project = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.google_app_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

        # Model configuration
        self.default_model = os.getenv('AI_MODEL', self._get_default_model())
        self.max_tokens = int(os.getenv('AI_MAX_TOKENS', '1000'))
        self.temperature = float(os.getenv('AI_TEMPERATURE', '0.3'))

        # Caching configuration
        self.cache_enabled = self._get_bool_env('AI_CACHE_ENABLED', True)
        self.cache_ttl_hours = int(os.getenv('AI_CACHE_TTL_HOURS', '24'))

        # Analysis thresholds
        self.discrimination_threshold = float(os.getenv('AI_DISCRIMINATION_THRESHOLD', '0.7'))
        self.problematic_threshold = float(os.getenv('AI_PROBLEMATIC_THRESHOLD', '0.6'))

    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')

    def _get_default_model(self) -> str:
        """Get default model based on provider."""
        defaults = {
            'openrouter': 'anthropic/claude-3-haiku',
            'google': 'gemini-pro',
            'anthropic': 'claude-3-haiku-20240307'
        }
        return defaults.get(self.provider, 'anthropic/claude-3-haiku')

    def validate(self) -> bool:
        """Validate configuration has required credentials."""
        if not self.enabled:
            return True

        if self.provider == 'openrouter' and not self.openrouter_api_key:
            logger.warning("OpenRouter API key not configured")
            return False
        elif self.provider == 'google' and not (self.google_cloud_project or self.google_app_credentials):
            logger.warning("Google Cloud credentials not configured")
            return False
        elif self.provider == 'anthropic' and not self.anthropic_api_key:
            logger.warning("Anthropic API key not configured")
            return False

        return True


class CacheManager:
    """Simple in-memory cache with TTL support."""

    def __init__(self, ttl_hours: int = 24):
        """Initialize cache manager.

        Args:
            ttl_hours: Time-to-live for cache entries in hours
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = timedelta(hours=ttl_hours)

    def _generate_key(self, text: str, analysis_type: str) -> str:
        """Generate cache key from text and analysis type."""
        content = f"{analysis_type}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, text: str, analysis_type: str) -> Optional[Dict]:
        """Retrieve cached result if available and not expired."""
        key = self._generate_key(text, analysis_type)

        if key not in self._cache:
            return None

        entry = self._cache[key]
        if datetime.now() - entry['timestamp'] > self._ttl:
            del self._cache[key]
            return None

        logger.debug(f"Cache hit for {analysis_type}")
        return entry['result']

    def set(self, text: str, analysis_type: str, result: Dict) -> None:
        """Store result in cache."""
        key = self._generate_key(text, analysis_type)
        self._cache[key] = {
            'result': result,
            'timestamp': datetime.now()
        }
        logger.debug(f"Cached result for {analysis_type}")

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            'total_entries': len(self._cache),
            'memory_size_bytes': len(str(self._cache))
        }


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, config: AIAnalysisConfig, cache: CacheManager):
        """Initialize provider with configuration and cache.

        Args:
            config: AI analysis configuration
            cache: Cache manager instance
        """
        self.config = config
        self.cache = cache

    @abstractmethod
    def _call_api(self, prompt: str, **kwargs) -> str:
        """Call the provider's API with the given prompt.

        Args:
            prompt: The prompt to send to the AI
            **kwargs: Additional provider-specific parameters

        Returns:
            The AI's response text
        """
        pass

    def analyze_document(self, text: str, analysis_type: str) -> Dict:
        """Analyze document with caching support.

        Args:
            text: Document text to analyze
            analysis_type: Type of analysis to perform

        Returns:
            Analysis results dictionary
        """
        # Check cache first
        if self.config.cache_enabled:
            cached_result = self.cache.get(text, analysis_type)
            if cached_result:
                return cached_result

        try:
            # Perform analysis
            if analysis_type == 'discrimination':
                result = self.detect_discrimination(text)
            elif analysis_type == 'problematic':
                result = self.identify_problematic_content(text)
            elif analysis_type == 'metadata':
                result = self.extract_metadata(text)
            else:
                result = self._generic_analysis(text, analysis_type)

            # Cache the result
            if self.config.cache_enabled:
                self.cache.set(text, analysis_type, result)

            return result

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return self._error_response(str(e))

    def detect_discrimination(self, text: str) -> Dict:
        """Detect potential discrimination in document text.

        Args:
            text: Document text to analyze

        Returns:
            Dictionary with discrimination analysis results
        """
        prompt = f"""Analyze the following text for potential discrimination based on:
- Race, ethnicity, or national origin
- Gender or sexual orientation
- Age
- Disability
- Religion
- Other protected characteristics

Text to analyze:
{text[:2000]}

Provide a JSON response with:
- "has_discrimination": boolean
- "confidence": float (0-1)
- "categories": list of discrimination types found
- "evidence": list of specific phrases or patterns
- "severity": string (low/medium/high)
- "explanation": brief explanation

Return ONLY valid JSON, no additional text."""

        try:
            response = self._call_api(prompt)
            result = json.loads(response)
            result['analysis_type'] = 'discrimination'
            result['timestamp'] = datetime.now().isoformat()
            return result
        except json.JSONDecodeError:
            logger.error("Failed to parse discrimination analysis response")
            return self._default_discrimination_response()
        except Exception as e:
            logger.error(f"Discrimination detection failed: {e}")
            return self._error_response(str(e))

    def identify_problematic_content(self, text: str) -> Dict:
        """Identify problematic content in document.

        Args:
            text: Document text to analyze

        Returns:
            Dictionary with problematic content analysis
        """
        prompt = f"""Analyze the following text for problematic content including:
- Offensive or inflammatory language
- Potential harassment or threats
- Confidential information exposure
- Misleading or fraudulent statements
- Privacy violations
- Ethical concerns

Text to analyze:
{text[:2000]}

Provide a JSON response with:
- "has_issues": boolean
- "confidence": float (0-1)
- "issues": list of issue types found
- "locations": list of problematic sections
- "severity": string (low/medium/high/critical)
- "recommendations": list of suggested actions
- "explanation": brief explanation

Return ONLY valid JSON, no additional text."""

        try:
            response = self._call_api(prompt)
            result = json.loads(response)
            result['analysis_type'] = 'problematic_content'
            result['timestamp'] = datetime.now().isoformat()
            return result
        except json.JSONDecodeError:
            logger.error("Failed to parse problematic content analysis response")
            return self._default_problematic_response()
        except Exception as e:
            logger.error(f"Problematic content identification failed: {e}")
            return self._error_response(str(e))

    def extract_metadata(self, text: str) -> Dict:
        """Extract document metadata using AI.

        Args:
            text: Document text to analyze

        Returns:
            Dictionary with extracted metadata
        """
        prompt = f"""Extract structured metadata from the following document:

{text[:2000]}

Provide a JSON response with:
- "document_type": string (contract/email/memo/report/legal/other)
- "key_entities": list of important people, organizations, places
- "dates": list of significant dates mentioned
- "topics": list of main topics or subjects
- "language": detected language
- "sentiment": string (positive/negative/neutral)
- "summary": brief 1-2 sentence summary
- "keywords": list of important keywords

Return ONLY valid JSON, no additional text."""

        try:
            response = self._call_api(prompt)
            result = json.loads(response)
            result['analysis_type'] = 'metadata'
            result['timestamp'] = datetime.now().isoformat()
            return result
        except json.JSONDecodeError:
            logger.error("Failed to parse metadata extraction response")
            return self._default_metadata_response()
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return self._error_response(str(e))

    def _generic_analysis(self, text: str, analysis_type: str) -> Dict:
        """Perform generic analysis for custom analysis types."""
        prompt = f"""Analyze the following text for: {analysis_type}

Text:
{text[:2000]}

Provide a JSON response with your analysis results.
Return ONLY valid JSON, no additional text."""

        try:
            response = self._call_api(prompt)
            result = json.loads(response)
            result['analysis_type'] = analysis_type
            result['timestamp'] = datetime.now().isoformat()
            return result
        except Exception as e:
            logger.error(f"Generic analysis failed: {e}")
            return self._error_response(str(e))

    def _error_response(self, error_msg: str) -> Dict:
        """Generate error response."""
        return {
            'error': True,
            'message': error_msg,
            'timestamp': datetime.now().isoformat()
        }

    def _default_discrimination_response(self) -> Dict:
        """Default response when discrimination analysis fails."""
        return {
            'has_discrimination': False,
            'confidence': 0.0,
            'categories': [],
            'evidence': [],
            'severity': 'unknown',
            'explanation': 'Analysis failed or could not be completed',
            'analysis_type': 'discrimination',
            'timestamp': datetime.now().isoformat()
        }

    def _default_problematic_response(self) -> Dict:
        """Default response when problematic content analysis fails."""
        return {
            'has_issues': False,
            'confidence': 0.0,
            'issues': [],
            'locations': [],
            'severity': 'unknown',
            'recommendations': [],
            'explanation': 'Analysis failed or could not be completed',
            'analysis_type': 'problematic_content',
            'timestamp': datetime.now().isoformat()
        }

    def _default_metadata_response(self) -> Dict:
        """Default response when metadata extraction fails."""
        return {
            'document_type': 'unknown',
            'key_entities': [],
            'dates': [],
            'topics': [],
            'language': 'unknown',
            'sentiment': 'neutral',
            'summary': 'Unable to extract summary',
            'keywords': [],
            'analysis_type': 'metadata',
            'timestamp': datetime.now().isoformat()
        }


class OpenRouterProvider(AIProvider):
    """OpenRouter API provider supporting multiple models."""

    def _call_api(self, prompt: str, **kwargs) -> str:
        """Call OpenRouter API.

        Args:
            prompt: The prompt to send
            **kwargs: Additional parameters

        Returns:
            API response text
        """
        try:
            import requests
        except ImportError:
            raise ImportError("requests library required for OpenRouter. Install with: pip install requests")

        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.config.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/bates-labeler",
            "X-Title": "Bates-Labeler AI Analysis"
        }

        data = {
            "model": kwargs.get('model', self.config.default_model),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
            "temperature": kwargs.get('temperature', self.config.temperature)
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']


class GoogleCloudProvider(AIProvider):
    """Google Cloud Vertex AI / Gemini provider."""

    def _call_api(self, prompt: str, **kwargs) -> str:
        """Call Google Cloud Vertex AI API.

        Args:
            prompt: The prompt to send
            **kwargs: Additional parameters

        Returns:
            API response text
        """
        try:
            from google.cloud import aiplatform
            from vertexai.preview.generative_models import GenerativeModel
        except ImportError:
            raise ImportError(
                "Google Cloud AI Platform libraries required. "
                "Install with: pip install google-cloud-aiplatform"
            )

        # Initialize Vertex AI
        aiplatform.init(project=self.config.google_cloud_project)

        # Use Gemini model
        model = GenerativeModel(kwargs.get('model', self.config.default_model))

        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                "temperature": kwargs.get('temperature', self.config.temperature)
            }
        )

        return response.text


class AnthropicProvider(AIProvider):
    """Anthropic Claude API provider."""

    def _call_api(self, prompt: str, **kwargs) -> str:
        """Call Anthropic Claude API.

        Args:
            prompt: The prompt to send
            **kwargs: Additional parameters

        Returns:
            API response text
        """
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic library required. Install with: pip install anthropic")

        client = anthropic.Anthropic(api_key=self.config.anthropic_api_key)

        message = client.messages.create(
            model=kwargs.get('model', self.config.default_model),
            max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
            temperature=kwargs.get('temperature', self.config.temperature),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text


class AIAnalyzer:
    """Main AI analyzer class with provider management."""

    def __init__(self, config: Optional[AIAnalysisConfig] = None):
        """Initialize AI analyzer.

        Args:
            config: Optional configuration object. Creates default if not provided.
        """
        self.config = config or AIAnalysisConfig()
        self.cache = CacheManager(ttl_hours=self.config.cache_ttl_hours)
        self.provider = self._initialize_provider()

    def _initialize_provider(self) -> Optional[AIProvider]:
        """Initialize the appropriate AI provider based on configuration."""
        if not self.config.enabled:
            logger.info("AI analysis disabled")
            return None

        if not self.config.validate():
            logger.warning("AI analysis configuration invalid, disabled")
            return None

        try:
            if self.config.provider == 'openrouter':
                logger.info("Initializing OpenRouter provider")
                return OpenRouterProvider(self.config, self.cache)
            elif self.config.provider == 'google':
                logger.info("Initializing Google Cloud provider")
                return GoogleCloudProvider(self.config, self.cache)
            elif self.config.provider == 'anthropic':
                logger.info("Initializing Anthropic provider")
                return AnthropicProvider(self.config, self.cache)
            else:
                logger.error(f"Unknown provider: {self.config.provider}")
                return None
        except Exception as e:
            logger.error(f"Failed to initialize provider: {e}")
            return None

    def is_enabled(self) -> bool:
        """Check if AI analysis is enabled and available."""
        return self.provider is not None

    def analyze_document(self, text: str, analysis_type: str = 'discrimination') -> Dict:
        """Analyze document text.

        Args:
            text: Document text to analyze
            analysis_type: Type of analysis (discrimination/problematic/metadata)

        Returns:
            Analysis results dictionary
        """
        if not self.is_enabled():
            return {
                'error': True,
                'message': 'AI analysis not enabled or configured',
                'timestamp': datetime.now().isoformat()
            }

        if not text or not text.strip():
            return {
                'error': True,
                'message': 'No text provided for analysis',
                'timestamp': datetime.now().isoformat()
            }

        return self.provider.analyze_document(text, analysis_type)

    def detect_discrimination(self, text: str) -> Dict:
        """Detect discrimination in text.

        Args:
            text: Text to analyze

        Returns:
            Discrimination analysis results
        """
        return self.analyze_document(text, 'discrimination')

    def identify_problematic_content(self, text: str) -> Dict:
        """Identify problematic content in text.

        Args:
            text: Text to analyze

        Returns:
            Problematic content analysis results
        """
        return self.analyze_document(text, 'problematic')

    def extract_metadata(self, text: str) -> Dict:
        """Extract metadata from text.

        Args:
            text: Text to analyze

        Returns:
            Extracted metadata
        """
        return self.analyze_document(text, 'metadata')

    def get_cache_stats(self) -> Dict:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return self.cache.get_stats()

    def clear_cache(self) -> None:
        """Clear the analysis cache."""
        self.cache.clear()


# Convenience functions for direct usage
_global_analyzer: Optional[AIAnalyzer] = None


def get_analyzer() -> AIAnalyzer:
    """Get or create global analyzer instance."""
    global _global_analyzer
    if _global_analyzer is None:
        _global_analyzer = AIAnalyzer()
    return _global_analyzer


def analyze_document(text: str, analysis_type: str = 'discrimination') -> Dict:
    """Convenience function for document analysis."""
    return get_analyzer().analyze_document(text, analysis_type)


def detect_discrimination(text: str) -> Dict:
    """Convenience function for discrimination detection."""
    return get_analyzer().detect_discrimination(text)


def identify_problematic_content(text: str) -> Dict:
    """Convenience function for problematic content identification."""
    return get_analyzer().identify_problematic_content(text)


def extract_metadata(text: str) -> Dict:
    """Convenience function for metadata extraction."""
    return get_analyzer().extract_metadata(text)


def is_ai_enabled() -> bool:
    """Check if AI analysis is enabled."""
    return get_analyzer().is_enabled()


# Example usage and testing
if __name__ == "__main__":
    # Test configuration
    config = AIAnalysisConfig()
    print(f"AI Analysis Enabled: {config.enabled}")
    print(f"Provider: {config.provider}")
    print(f"Configuration Valid: {config.validate()}")

    # Test analyzer
    analyzer = AIAnalyzer(config)
    print(f"Analyzer Ready: {analyzer.is_enabled()}")

    # Test cache
    print(f"Cache Stats: {analyzer.get_cache_stats()}")

    # Example analysis (only runs if enabled)
    if analyzer.is_enabled():
        sample_text = "This is a sample document for testing AI analysis capabilities."
        result = analyzer.extract_metadata(sample_text)
        print(f"Analysis Result: {json.dumps(result, indent=2)}")
