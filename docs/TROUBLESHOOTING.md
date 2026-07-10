# Troubleshooting Guide

## Common Issues

### LM Studio Not Connected

**Symptoms**: Embeddings status shows "Disconnected" or "Error"

**Causes**:
1. LM Studio server is not running
2. Wrong port configured (default: 1234)
3. Firewall blocking localhost connections
4. Embedding model not loaded

**Solutions**:
1. Open LM Studio and verify server is running (not just the app)
2. Check the server port in LM Studio matches the configured URL
3. Try accessing `http://localhost:1234/v1/models` in a browser
4. In LM Studio, ensure an embedding model is loaded (e.g., `nomic-embed-text-v1.5`)
5. Restart LM Studio and try again

---

### Documents Not Indexing

**Symptoms**: Documents stuck in "pending" or "error" status

**Causes**:
1. LM Studio embedding model not loaded
2. Unsupported file format
3. File is corrupted or password-protected
4. Backend parsing error

**Solutions**:
1. Verify LM Studio has an embedding model loaded
2. Check file format is supported: PDF, DOCX, XLSX, MD, HTML
3. Try opening the file in its native application to verify it's not corrupted
4. Check backend logs: `~/.doc-assistant/logs/backend.log`
5. Delete and re-upload the document

---

### No Citations in Answer

**Symptoms**: Assistant responds but shows no source citations

**Causes**:
1. No documents indexed in the collection
2. Query doesn't match any document content
3. Retrieval confidence too low
4. Wrong collection selected

**Solutions**:
1. Verify documents are indexed (status shows "indexed")
2. Check you're querying the correct collection
3. Try rephrasing your question with keywords from the documents
4. Upload additional relevant documents
5. Check backend logs for retrieval errors

---

### API Error: 401 Unauthorized

**Symptoms**: Chat fails with authentication error

**Causes**:
1. Invalid API key
2. API key expired
3. Wrong provider selected
4. Network connectivity issues

**Solutions**:
1. Go to Settings → LLM Provider
2. Verify API key is correct (copy-paste carefully)
3. Test the API key in the provider's dashboard
4. Check your account has active subscription/credits
5. Save and retry

---

### Backend Not Starting

**Symptoms**: Application fails to start or shows "Backend Error"

**Causes**:
1. Python not installed or wrong version
2. Virtual environment corrupted
3. Port 8000 already in use
4. Missing dependencies

**Solutions**:
1. Check Python 3.11+ is installed: `python --version`
2. Verify virtual environment exists: `backend/venv/`
3. Check if port 8000 is in use: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (Linux/Mac)
4. Reinstall dependencies:
   ```bash
   cd backend
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
5. Review logs: `~/.doc-assistant/logs/backend.log`

---

### Frontend Not Loading

**Symptoms**: Blank screen or frontend errors in browser

**Causes**:
1. Node.js not installed or wrong version
2. Frontend build failed
3. Port 1420 already in use
4. Browser cache issues

**Solutions**:
1. Check Node.js 18+ is installed: `node --version`
2. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
3. Check if port 1420 is in use
4. Rebuild frontend:
   ```bash
   cd frontend
   rm -rf node_modules
   npm install
   npm run build
   ```
5. Check browser console for errors (F12 → Console tab)

---

### Slow Response Times

**Symptoms**: Chat responses take more than 10-15 seconds

**Causes**:
1. Large document collection
2. Slow internet connection (for LLM API calls)
3. LM Studio not using GPU acceleration
4. Complex query requiring multiple retrieval iterations

**Solutions**:
1. Reduce collection size (split into multiple collections)
2. Check internet speed and stability
3. In LM Studio, ensure GPU acceleration is enabled
4. Use a faster LLM model (e.g., GPT-4o-mini instead of GPT-4o)
5. Enable semantic caching in settings
6. Simplify your query

---

### Out of Memory Errors

**Symptoms**: Application crashes or shows "Out of Memory" error

**Causes**:
1. Too many documents in collection
2. Very large files
3. Insufficient system RAM
4. Memory leak in backend

**Solutions**:
1. Reduce number of documents in collection
2. Split large documents into smaller chunks
3. Close other applications to free RAM
4. Restart the application
5. Consider upgrading system RAM (16GB+ recommended)

---

### Collection Deletion Fails

**Symptoms**: Cannot delete collection, error message appears

**Causes**:
1. Collection has active conversations
2. Database locked
3. Permission issues

**Solutions**:
1. Delete or move all conversations from the collection first
2. Restart the application
3. Check database file permissions: `~/.doc-assistant/app.db`
4. Try deleting documents first, then the collection

---

### File Watcher Not Working

**Symptoms**: Changes to indexed files not detected automatically

**Causes**:
1. File watcher not enabled
2. Permission issues on watched directory
3. Too many files being watched
4. File system doesn't support watching (network drives)

**Solutions**:
1. Verify file watching is enabled in settings
2. Check application has read permissions for the directory
3. Reduce number of watched files
4. Avoid network drives or cloud-synced folders
5. Manually re-index documents after changes

---

## Getting Help

If you're still experiencing issues:

1. **Check logs**:
   - Backend: `~/.doc-assistant/logs/backend.log`
   - Frontend: Browser console (F12)
   - Tauri: Platform-specific application logs

2. **Verify prerequisites**:
   - Python 3.11+
   - Node.js 18+
   - LM Studio with embedding model
   - Valid LLM API key

3. **Reset data** (WARNING: loses all data):
   ```bash
   # Reset database
   rm ~/.doc-assistant/app.db
   
   # Reset vector index
   rm -rf ~/.doc-assistant/qdrant
   
   # Full reset
   rm -rf ~/.doc-assistant
   ```

4. **Report bugs**:
   - Open an issue on GitHub
   - Include error messages, steps to reproduce, system info
   - Attach logs if possible

## Diagnostic Commands

```bash
# Check Python version
python --version

# Check Node.js version
node --version

# Check if LM Studio is running
curl http://localhost:1234/v1/models

# Check if backend is running
curl http://localhost:8000/health

# Check if frontend is running
curl http://localhost:1420

# List running processes (Windows)
tasklist | findstr python
tasklist | findstr node

# List running processes (Linux/Mac)
ps aux | grep python
ps aux | grep node
```

## Performance Tuning

### For Better Indexing Speed
- Use SSD storage for `~/.doc-assistant/`
- Ensure LM Studio is using GPU acceleration
- Index documents in smaller batches
- Use simpler embedding models

### For Better Query Speed
- Enable semantic caching
- Use faster LLM models
- Reduce max retrieval iterations
- Keep collections focused and small

### For Better Memory Usage
- Limit concurrent conversations
- Clear old conversations regularly
- Use smaller chunk sizes
- Reduce embedding dimensions if possible
