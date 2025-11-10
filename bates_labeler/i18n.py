"""
Multi-Language Support (i18n) Module

Provides internationalization support for the Bates-Labeler application,
enabling translation of UI elements, messages, and documentation into
multiple languages.

Features:
- Support for multiple languages (English, Spanish, French, German, Chinese, Japanese)
- Dynamic language switching
- Translation management
- Locale-specific formatting (dates, numbers)
- RTL language support
- Translation file management (JSON-based)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Any
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages."""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE_SIMPLIFIED = "zh-CN"
    JAPANESE = "ja"
    PORTUGUESE = "pt"
    ITALIAN = "it"
    RUSSIAN = "ru"
    KOREAN = "ko"


class TextDirection(Enum):
    """Text direction for UI rendering."""
    LTR = "ltr"  # Left-to-right
    RTL = "rtl"  # Right-to-left


@dataclass
class LocaleInfo:
    """Locale-specific configuration."""
    language: Language
    display_name: str
    native_name: str
    text_direction: TextDirection
    date_format: str
    number_format: str
    decimal_separator: str
    thousands_separator: str


# Locale configurations
LOCALES: Dict[Language, LocaleInfo] = {
    Language.ENGLISH: LocaleInfo(
        language=Language.ENGLISH,
        display_name="English",
        native_name="English",
        text_direction=TextDirection.LTR,
        date_format="%Y-%m-%d",
        number_format="{:,.2f}",
        decimal_separator=".",
        thousands_separator=","
    ),
    Language.SPANISH: LocaleInfo(
        language=Language.SPANISH,
        display_name="Spanish",
        native_name="Español",
        text_direction=TextDirection.LTR,
        date_format="%d/%m/%Y",
        number_format="{:,.2f}",
        decimal_separator=",",
        thousands_separator="."
    ),
    Language.FRENCH: LocaleInfo(
        language=Language.FRENCH,
        display_name="French",
        native_name="Français",
        text_direction=TextDirection.LTR,
        date_format="%d/%m/%Y",
        number_format="{:,.2f}",
        decimal_separator=",",
        thousands_separator=" "
    ),
    Language.GERMAN: LocaleInfo(
        language=Language.GERMAN,
        display_name="German",
        native_name="Deutsch",
        text_direction=TextDirection.LTR,
        date_format="%d.%m.%Y",
        number_format="{:,.2f}",
        decimal_separator=",",
        thousands_separator="."
    ),
    Language.CHINESE_SIMPLIFIED: LocaleInfo(
        language=Language.CHINESE_SIMPLIFIED,
        display_name="Chinese (Simplified)",
        native_name="简体中文",
        text_direction=TextDirection.LTR,
        date_format="%Y年%m月%d日",
        number_format="{:,.2f}",
        decimal_separator=".",
        thousands_separator=","
    ),
    Language.JAPANESE: LocaleInfo(
        language=Language.JAPANESE,
        display_name="Japanese",
        native_name="日本語",
        text_direction=TextDirection.LTR,
        date_format="%Y年%m月%d日",
        number_format="{:,.2f}",
        decimal_separator=".",
        thousands_separator=","
    ),
    Language.PORTUGUESE: LocaleInfo(
        language=Language.PORTUGUESE,
        display_name="Portuguese",
        native_name="Português",
        text_direction=TextDirection.LTR,
        date_format="%d/%m/%Y",
        number_format="{:,.2f}",
        decimal_separator=",",
        thousands_separator="."
    ),
}


# Default translation strings (English)
DEFAULT_TRANSLATIONS = {
    "en": {
        # App title and navigation
        "app_title": "Bates Numbering Tool",
        "app_subtitle": "Professional Bates numbering for legal documents",

        # Sidebar
        "configuration": "Configuration",
        "basic_settings": "Basic Settings",
        "output_options": "Output Options",
        "position_appearance": "Position & Appearance",
        "advanced_options": "Advanced Options",

        # Input fields
        "bates_prefix": "Bates Prefix",
        "bates_suffix": "Bates Suffix",
        "start_number": "Start Number",
        "padding": "Padding",
        "position": "Position",
        "font": "Font",
        "font_size": "Font Size",
        "color": "Color",

        # Buttons
        "process": "Process PDF(s)",
        "download": "Download",
        "cancel": "Cancel",
        "clear": "Clear",
        "upload": "Upload",
        "export": "Export",
        "import": "Import",
        "save": "Save",
        "load": "Load",

        # Messages
        "success": "Success!",
        "error": "Error",
        "warning": "Warning",
        "processing": "Processing...",
        "complete": "Complete",
        "failed": "Failed",

        # File operations
        "upload_files": "Upload PDF Files",
        "choose_files": "Choose PDF file(s)",
        "files_uploaded": "file(s) uploaded",
        "download_all": "Download All Files as ZIP",

        # Features
        "add_separator": "Add Separator Page",
        "combine_pdfs": "Combine All PDFs into Single File",
        "use_bates_filenames": "Use Bates Number as Filename",
        "enable_qr": "Enable QR Codes",
        "enable_watermark": "Enable Watermark",
        "enable_border": "Enable Border on Separator Page",

        # Validation
        "pdf_is_valid": "PDF is valid",
        "pdf_is_invalid": "PDF is invalid",
        "repairing": "Repairing PDF...",
        "repair_successful": "PDF repaired successfully",
        "repair_failed": "Repair failed",

        # Redaction
        "redaction": "Redaction",
        "enable_redaction": "Enable Automatic Redaction",
        "redaction_types": "Redaction Types",
        "ssn": "Social Security Numbers",
        "credit_card": "Credit Card Numbers",
        "email": "Email Addresses",
        "phone": "Phone Numbers",
        "redact_preview": "Preview Redactions",
        "apply_redactions": "Apply Redactions",

        # Help text
        "help_prefix": "Text to appear before the number (e.g., 'CASE123-')",
        "help_suffix": "Text to appear after the number (e.g., '-CONF')",
        "help_start_number": "First Bates number to use",
        "help_padding": "Number of digits (e.g., 4 = '0001')",
        "help_position": "Where to place the Bates number on the page",

        # Language selector
        "language": "Language",
        "select_language": "Select Language",
    },

    "es": {
        # Spanish translations
        "app_title": "Herramienta de Numeración Bates",
        "app_subtitle": "Numeración Bates profesional para documentos legales",
        "configuration": "Configuración",
        "basic_settings": "Configuración Básica",
        "output_options": "Opciones de Salida",
        "position_appearance": "Posición y Apariencia",
        "advanced_options": "Opciones Avanzadas",
        "bates_prefix": "Prefijo Bates",
        "bates_suffix": "Sufijo Bates",
        "start_number": "Número Inicial",
        "padding": "Relleno",
        "position": "Posición",
        "font": "Fuente",
        "font_size": "Tamaño de Fuente",
        "color": "Color",
        "process": "Procesar PDF(s)",
        "download": "Descargar",
        "cancel": "Cancelar",
        "clear": "Limpiar",
        "upload": "Subir",
        "export": "Exportar",
        "import": "Importar",
        "save": "Guardar",
        "load": "Cargar",
        "success": "¡Éxito!",
        "error": "Error",
        "warning": "Advertencia",
        "processing": "Procesando...",
        "complete": "Completo",
        "failed": "Fallido",
        "upload_files": "Subir Archivos PDF",
        "choose_files": "Elegir archivo(s) PDF",
        "files_uploaded": "archivo(s) subido(s)",
        "download_all": "Descargar Todos los Archivos como ZIP",
        "add_separator": "Agregar Página Separadora",
        "combine_pdfs": "Combinar Todos los PDFs en un Solo Archivo",
        "use_bates_filenames": "Usar Número Bates como Nombre de Archivo",
        "enable_qr": "Habilitar Códigos QR",
        "enable_watermark": "Habilitar Marca de Agua",
        "enable_border": "Habilitar Borde en Página Separadora",
        "language": "Idioma",
        "select_language": "Seleccionar Idioma",
    },

    "fr": {
        # French translations
        "app_title": "Outil de Numérotation Bates",
        "app_subtitle": "Numérotation Bates professionnelle pour documents juridiques",
        "configuration": "Configuration",
        "basic_settings": "Paramètres de Base",
        "output_options": "Options de Sortie",
        "position_appearance": "Position et Apparence",
        "advanced_options": "Options Avancées",
        "bates_prefix": "Préfixe Bates",
        "bates_suffix": "Suffixe Bates",
        "start_number": "Numéro de Départ",
        "padding": "Remplissage",
        "position": "Position",
        "font": "Police",
        "font_size": "Taille de Police",
        "color": "Couleur",
        "process": "Traiter PDF(s)",
        "download": "Télécharger",
        "cancel": "Annuler",
        "clear": "Effacer",
        "upload": "Téléverser",
        "export": "Exporter",
        "import": "Importer",
        "save": "Enregistrer",
        "load": "Charger",
        "success": "Succès !",
        "error": "Erreur",
        "warning": "Avertissement",
        "processing": "Traitement en cours...",
        "complete": "Terminé",
        "failed": "Échoué",
        "upload_files": "Téléverser Fichiers PDF",
        "choose_files": "Choisir fichier(s) PDF",
        "files_uploaded": "fichier(s) téléversé(s)",
        "download_all": "Télécharger Tous les Fichiers en ZIP",
        "language": "Langue",
        "select_language": "Sélectionner la Langue",
    },

    "de": {
        # German translations
        "app_title": "Bates-Nummerierungstool",
        "app_subtitle": "Professionelle Bates-Nummerierung für juristische Dokumente",
        "configuration": "Konfiguration",
        "basic_settings": "Grundeinstellungen",
        "output_options": "Ausgabeoptionen",
        "position_appearance": "Position und Aussehen",
        "advanced_options": "Erweiterte Optionen",
        "bates_prefix": "Bates-Präfix",
        "bates_suffix": "Bates-Suffix",
        "start_number": "Startnummer",
        "padding": "Auffüllung",
        "position": "Position",
        "font": "Schriftart",
        "font_size": "Schriftgröße",
        "color": "Farbe",
        "process": "PDF(s) Verarbeiten",
        "download": "Herunterladen",
        "cancel": "Abbrechen",
        "clear": "Löschen",
        "upload": "Hochladen",
        "export": "Exportieren",
        "import": "Importieren",
        "save": "Speichern",
        "load": "Laden",
        "success": "Erfolg!",
        "error": "Fehler",
        "warning": "Warnung",
        "processing": "Verarbeitung läuft...",
        "complete": "Abgeschlossen",
        "failed": "Fehlgeschlagen",
        "upload_files": "PDF-Dateien Hochladen",
        "choose_files": "PDF-Datei(en) Auswählen",
        "files_uploaded": "Datei(en) hochgeladen",
        "download_all": "Alle Dateien als ZIP Herunterladen",
        "language": "Sprache",
        "select_language": "Sprache Auswählen",
    },
}


class I18nManager:
    """
    Internationalization manager for Bates-Labeler.

    Handles translation loading, language switching, and locale-specific formatting.
    """

    def __init__(self, default_language: Language = Language.ENGLISH, translations_dir: Optional[str] = None):
        """
        Initialize the i18n manager.

        Args:
            default_language: Default language to use
            translations_dir: Directory containing translation files (optional)
        """
        self.current_language = default_language
        self.translations = DEFAULT_TRANSLATIONS.copy()
        self.translations_dir = translations_dir

        # Load custom translations if directory provided
        if translations_dir and os.path.exists(translations_dir):
            self._load_translations_from_directory(translations_dir)

    def _load_translations_from_directory(self, directory: str) -> None:
        """Load translation files from directory."""
        path = Path(directory)
        for json_file in path.glob("*.json"):
            lang_code = json_file.stem
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                    self.translations[lang_code] = translations
                    logger.info(f"Loaded translations for {lang_code}")
            except Exception as e:
                logger.error(f"Failed to load translations from {json_file}: {e}")

    def set_language(self, language: Language) -> None:
        """Set the current language."""
        self.current_language = language
        logger.info(f"Language set to: {language.value}")

    def get_language(self) -> Language:
        """Get the current language."""
        return self.current_language

    def get_locale(self) -> LocaleInfo:
        """Get locale info for current language."""
        return LOCALES.get(self.current_language, LOCALES[Language.ENGLISH])

    def translate(self, key: str, **kwargs) -> str:
        """
        Get translation for a key in the current language.

        Args:
            key: Translation key
            **kwargs: Format arguments for string interpolation

        Returns:
            Translated string (falls back to English if not found)
        """
        lang_code = self.current_language.value

        # Try current language
        if lang_code in self.translations:
            if key in self.translations[lang_code]:
                translation = self.translations[lang_code][key]
                return translation.format(**kwargs) if kwargs else translation

        # Fallback to English
        if "en" in self.translations and key in self.translations["en"]:
            translation = self.translations["en"][key]
            return translation.format(**kwargs) if kwargs else translation

        # Return key if not found
        return key

    def t(self, key: str, **kwargs) -> str:
        """Shorthand for translate()."""
        return self.translate(key, **kwargs)

    def get_available_languages(self) -> Dict[Language, str]:
        """Get all available languages with their native names."""
        return {
            lang: info.native_name
            for lang, info in LOCALES.items()
            if lang.value in self.translations
        }

    def export_translations(self, output_dir: str, language: Optional[Language] = None) -> None:
        """
        Export translations to JSON files.

        Args:
            output_dir: Directory to save translation files
            language: Specific language to export (None = all)
        """
        os.makedirs(output_dir, exist_ok=True)

        languages_to_export = [language] if language else self.translations.keys()

        for lang_code in languages_to_export:
            if lang_code in self.translations:
                output_file = os.path.join(output_dir, f"{lang_code}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.translations[lang_code], f, ensure_ascii=False, indent=2)
                logger.info(f"Exported translations for {lang_code} to {output_file}")

    def import_translations(self, json_file: str) -> bool:
        """
        Import translations from a JSON file.

        Args:
            json_file: Path to JSON file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)

            # Detect language from filename
            lang_code = Path(json_file).stem

            # Merge with existing translations
            if lang_code in self.translations:
                self.translations[lang_code].update(translations)
            else:
                self.translations[lang_code] = translations

            logger.info(f"Imported translations from {json_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to import translations from {json_file}: {e}")
            return False

    def format_number(self, number: float) -> str:
        """Format number according to current locale."""
        locale = self.get_locale()
        formatted = locale.number_format.format(number)

        # Replace separators
        if locale.decimal_separator != ".":
            formatted = formatted.replace(".", locale.decimal_separator)
        if locale.thousands_separator != ",":
            formatted = formatted.replace(",", locale.thousands_separator)

        return formatted

    def format_date(self, date_obj) -> str:
        """Format date according to current locale."""
        locale = self.get_locale()
        return date_obj.strftime(locale.date_format)


# Global i18n instance
_global_i18n = None


def get_i18n() -> I18nManager:
    """Get or create global i18n manager instance."""
    global _global_i18n
    if _global_i18n is None:
        _global_i18n = I18nManager()
    return _global_i18n


def init_i18n(language: Language = Language.ENGLISH, translations_dir: Optional[str] = None) -> I18nManager:
    """
    Initialize global i18n manager.

    Args:
        language: Default language
        translations_dir: Custom translations directory

    Returns:
        I18nManager instance
    """
    global _global_i18n
    _global_i18n = I18nManager(language, translations_dir)
    return _global_i18n


# Convenience function
def t(key: str, **kwargs) -> str:
    """
    Quick translation function.

    Args:
        key: Translation key
        **kwargs: Format arguments

    Returns:
        Translated string
    """
    return get_i18n().translate(key, **kwargs)


__all__ = [
    'I18nManager',
    'Language',
    'LocaleInfo',
    'TextDirection',
    'LOCALES',
    'get_i18n',
    'init_i18n',
    't',
]
