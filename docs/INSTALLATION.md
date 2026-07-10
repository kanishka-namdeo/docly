# Doc Assistant Installation Guide

## Prerequisites

Before installing Doc Assistant, ensure you have:

1. **LM Studio** (required for embeddings)
   - Download from https://lmstudio.ai
   - Install and launch the application
   - Download an embedding model (recommended: `nomic-embed-text-v1.5`)
   - Start the server on port 1234 (default)

2. **LLM Provider API Key** (choose one)
   - OpenAI API key (https://platform.openai.com)
   - Anthropic API key (https://console.anthropic.com)
   - Google AI API key (https://makersuite.google.com)
   - Or any OpenAI-compatible API endpoint

## Installation

### Windows

1. Download the Windows installer (`DocAssistant-Setup.exe`) from the releases page
2. Run the installer and follow the prompts
3. Launch Doc Assistant from the Start Menu

### macOS

1. Download the macOS disk image (`DocAssistant.dmg`) from the releases page
2. Open the disk image and drag Doc Assistant to Applications
3. Launch from Applications folder
4. If prompted about security, go to System Preferences → Security & Privacy → Allow

### Linux

#### Debian/Ubuntu
```bash
sudo dpkg -i doc-assistant_*.deb
```

#### Fedora/RHEL
```bash
sudo rpm -i doc-assistant-*.rpm
```

#### Arch Linux
```bash
yay -S doc-assistant
```

## Post-Installation Setup

### 1. Configure LM Studio

1. Open LM Studio
2. Go to the "Models" tab
3. Search for and download `nomic-embed-text-v1.5`
4. Go to the "Server" tab
5. Select the embedding model
6. Click "Start Server"
7. Verify the server is running on `http://localhost:1234`

### 2. Configure LLM Provider

1. Launch Doc Assistant
2. Navigate to Settings (gear icon)
3. Click "Add Provider"
4. Select provider type:
   - **Anthropic**: Enter your Anthropic API key
   - **OpenAI**: Enter your OpenAI API key
   - **Google**: Enter your Google AI API key
   - **Custom**: Enter base URL and API key for OpenAI-compatible endpoints
5. Click "Save"

### 3. Verify Installation

1. In Doc Assistant, go to Settings
2. Check "Embeddings Status" - should show "Connected"
3. Create a test collection:
   - Go to Documents tab
   - Click "New Collection"
   - Name it "Test"
4. Upload a test document (PDF, DOCX, or MD)
5. Wait for indexing to complete (status shows "indexed")
6. Go to Chat tab
7. Ask a question about the document
8. Verify you receive an answer with citations

## Troubleshooting Installation

### LM Studio Not Connecting

**Problem**: Embeddings status shows "Disconnected"

**Solutions**:
1. Verify LM Studio server is running (not just the app)
2. Check port 1234 is not blocked by firewall
3. Try accessing `http://localhost:1234/v1/models` in browser
4. Restart LM Studio and try again

### Backend Not Starting

**Problem**: Application shows "Backend Error" or fails to start

**Solutions**:
1. Check Python 3.11+ is installed: `python --version`
2. Verify virtual environment exists: `backend/venv/`
3. Check port 8000 is not in use
4. Review logs: `~/.doc-assistant/logs/backend.log`

### Frontend Not Loading

**Problem**: Blank screen or frontend errors

**Solutions**:
1. Clear browser cache
2. Check Node.js 18+ is installed: `node --version`
3. Verify frontend is running on port 1420
4. Check browser console for errors (F12)

### Documents Not Indexing

**Problem**: Documents stuck in "pending" status

**Solutions**:
1. Verify LM Studio embedding model is loaded
2. Check file format is supported (PDF, DOCX, XLSX, MD, HTML)
3. Review backend logs for parsing errors
4. Try re-uploading the document

## System Requirements

- **OS**: Windows 10+, macOS 10.15+, or Linux (64-bit)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB for application + document storage
- **Network**: Internet connection for LLM API calls

## Next Steps

After successful installation:
1. Read the [User Guide](USER_GUIDE.md) for feature overview
2. Check [Troubleshooting](TROUBLESHOOTING.md) for common issues
3. Explore the [API Reference](API_REFERENCE.md) for advanced usage
