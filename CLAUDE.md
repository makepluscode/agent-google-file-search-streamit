# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gemini File Search 챗봇 - A document-based Q&A web application using Google Gemini File Search API (RAG system without requiring a separate vector database).

**Tech Stack:** Python 3.9+, Streamlit, Google Gemini 2.5 Flash, google-genai SDK, uv (package manager)

## Development Commands

### Setup and Installation
```bash
# Install uv package manager (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install with dev dependencies
uv sync --extra dev
```

### Running the Application

#### Development Mode (Direct Run)
```bash
# Run the Streamlit app directly
uv run streamlit run app.py

# The app will be available at http://localhost:8501
```

#### Production Mode (systemd Service)
```bash
# Register, enable, and start the service
sudo ./service.sh start

# Check service status
./service.sh status

# Stop the service
sudo ./service.sh stop

# Restart the service
sudo ./service.sh restart

# View service logs
./service.sh logs

# Completely remove the service
sudo ./service.sh disable
```

The systemd service provides:
- Auto-start on system boot
- Auto-restart on crash
- Background execution
- Centralized management via systemd

### Code Quality
```bash
# Format code
uv run black .

# Lint code
uv run ruff check .
```

### Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_api_key_here
```

Get API key from: https://aistudio.google.com/apikey

## Architecture

### Core Design Pattern

This is a **modular Streamlit application** with clear separation of concerns:

1. **app.py** - Main entry point, orchestrates UI layout and user interactions
2. **gemini_api.py** - All Gemini API interactions (client initialization, file upload, querying)
3. **ui_components.py** - Reusable UI rendering functions
4. **config.py** - Centralized configuration and constants
5. **styles.py** - CSS styling definitions
6. **utils.py** - Utility functions

### Session State Architecture

The app uses Streamlit's session state to maintain data across reruns:

```python
st.session_state = {
    "client": genai.Client,                    # Gemini API client
    "store": FileSearchStore,                  # Active file search store
    "chat_history": [                          # Conversation history
        {
            "question": str,
            "answer": str,
            "citations": list,
            "debug_info": {
                "has_grounding": bool,
                "grounding_chunks": [...],     # Retrieved document chunks
                "grounding_supports": [...],   # Answer-to-chunk mappings
                "citations": [...]
            }
        }
    ],
    "uploaded_files_metadata": [               # Detailed file metadata
        {
            "filename": str,
            "file_size_mb": float,
            "estimated_tokens": int,
            "estimated_chunks": int,
            "upload_duration_seconds": float,
            "chunking_config": {...}
        }
    ]
}
```

### RAG Implementation

**Chunking Strategy:** White space chunking with 400 tokens per chunk and 40 token overlap (configured in config.py:CHUNKING_CONFIG).

**Grounding Process:**
1. Files are uploaded to Gemini File Search Store with automatic indexing
2. Queries use the File Search tool to retrieve relevant chunks
3. Response includes grounding_metadata with:
   - `grounding_chunks`: Document fragments used in the response
   - `grounding_supports`: Maps answer segments to source chunks
   - `citations`: Structured citation data

**Key Implementation Detail in gemini_api.py:query_store():**
- Grounding metadata is accessed via `response.candidates[0].grounding_metadata`
- The function includes extensive debug logging to track the full RAG process
- Retrieved contexts include title, URI, and text from source documents

### File Upload Flow

1. User selects files in Streamlit file uploader (app.py:231-236)
2. For each file, `upload_file()` in gemini_api.py:
   - Creates temporary file with unique UUID
   - Collects metadata (size, character count, word count, estimated tokens)
   - Uploads to Gemini File Search Store with chunking config
   - Waits for async operation completion
   - Cleans up temporary file
   - Returns detailed metadata
3. Metadata is stored in session state and displayed in UI

### UI Layout Structure

**Sidebar:**
- Client initialization status
- Store management (create/switch stores)
- Uploaded files list with metadata
- Statistics (file count, total size, total tokens)
- Chat history clear button

**Main Area (Tabs):**
1. **질의응답 Tab**: Chat interface with message history, source citations, and debug info
2. **파일 업로드 Tab**: File uploader with progress tracking and detailed metadata display

## Important Configuration

### Model Settings (config.py)
- **Model**: gemini-2.5-flash
- **Temperature**: 0.2 (for consistent, accurate responses)
- **Accepted file types**: PDF, TXT, DOCX, MD, CSV

### Chunking Configuration (config.py)
```python
CHUNKING_CONFIG = {
    "max_tokens_per_chunk": 400,
    "max_overlap_tokens": 40,
    "chunking_method": "white_space"
}
```

### Color Palette (config.py)
The UI uses a dark theme with indigo accent color (#6366f1). All colors are centralized in COLORS dict.

## Common Patterns

### Error Handling
All API functions in gemini_api.py return tuples: `(result, error)` or `(success, data, error)`. Always check for errors before proceeding.

### Metadata Collection
File uploads collect extensive metadata for transparency (see gemini_api.py:36-131). This includes token estimation, chunk estimation, and upload timing.

### Debug Logging
The `query_store()` function includes comprehensive debug output to console (lines 169-373) for troubleshooting RAG behavior. This is intentional for development transparency.

### UI Component Reusability
All UI rendering is extracted to ui_components.py. When adding new UI elements, follow this pattern and create dedicated rendering functions.

## Working with This Codebase

### Adding New File Types
1. Update `UPLOAD_CONFIG['accepted_types']` in config.py
2. If it's a text format, add extension to `UPLOAD_CONFIG['text_extensions']`
3. Test file upload and metadata collection

### Modifying Chunking Strategy
Edit `CHUNKING_CONFIG` in config.py. The configuration is applied in gemini_api.py:74-86.

### Changing UI Styling
All styles are in styles.py using the COLORS dict from config.py. Use the get_custom_css() function which returns CSS as a string injected via st.markdown().

### Session State Management
- Always initialize new session state keys in app.py (lines 33-40)
- Use `st.rerun()` after state changes that should trigger UI updates
- Be cautious with state persistence - clearing store also clears chat history and file metadata (app.py:96-100)

### Testing Grounding
The debug info expander in the chat (ui_components.py:51-101) shows the full grounding process. Use this to verify that File Search is working correctly.

## Known Limitations

- Store is session-based (not persisted between app restarts)
- No file deletion capability (would need to use store's delete_file API)
- Gemini API free tier rate limits apply
- PDF text extraction quality depends on PDF structure
- Large files may take significant time to upload and index
