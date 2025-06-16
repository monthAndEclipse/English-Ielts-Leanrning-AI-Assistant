# AI Document Translation Application

## Overview
A powerful document translation system that preserves original formatting while converting content between languages using AI. Maintains layout, styles, and structure of documents during translation.

## Key Features
- Format-preserving translation (keeps original document structure)
- Multi-language support
- Batch processing capabilities
- API integration for automated workflows
- Progress tracking and status monitoring

## Supported Formats
| Format | Description |
|--------|-------------|
| DOCX   | Microsoft Word documents |
| XLSX   | Microsoft Excel spreadsheets |
| PPTX   | Microsoft PowerPoint presentations |
| Markdown | Lightweight markup documents |
| TXT    | Plain text files |
| SRT    | Subtitle files |

## Getting Started

### Prerequisites
- Python 3.8+
- Poetry (for dependency management)
- API credentials

### Installation
```bash
git clone https://github.com/monthAndEclipse/ai-doc-translation-python.git
cd ai-doc-translation-python
poetry install
```

### Basic Usage
```python
from translation_client import translate_document

result = translate_document(
    input_path="document.docx",
    output_path="translated.docx",
    target_language="es"
)
```

## API Documentation
For detailed API specifications and endpoints, see [API Documentation](docs/api.md).

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss proposed changes.

## License
[MIT](LICENSE)