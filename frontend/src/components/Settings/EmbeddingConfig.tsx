import { useState, useEffect } from 'react'
import { LMStudioStatus } from '../../types'
import { settingsApi } from '../../services/api'

export default function EmbeddingConfig() {
  const [status, setStatus] = useState<LMStudioStatus | null>(null)
  const [loading, setLoading] = useState(false)

  const checkStatus = async () => {
    setLoading(true)
    try {
      const s = await settingsApi.checkLMStudio()
      setStatus(s)
    } catch (err) {
      console.error('Failed to check LM Studio status:', err)
      setStatus({ connected: false, url: 'http://localhost:1234', models: null, error: null })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkStatus()
  }, [])

  return (
    <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px' }}>
      <h2 style={{ margin: '0 0 20px' }}>Embedding Configuration</h2>

      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ fontSize: '16px', marginBottom: '10px' }}>LM Studio Setup</h3>
        <p style={{ color: '#666', fontSize: '14px', lineHeight: '1.6' }}>
          The embedding model runs locally via <strong>LM Studio</strong>. Follow these steps to set it up:
        </p>
        <ol style={{ fontSize: '14px', color: '#333', lineHeight: '1.8' }}>
          <li>Download and install <a href="https://lmstudio.ai" target="_blank" rel="noopener noreferrer">LM Studio</a></li>
          <li>Download an embedding model (e.g., <code>nomic-embed-text</code> or <code>mxbai-embed-large</code>)</li>
          <li>Start the local inference server (default: <code>http://localhost:1234</code>)</li>
          <li>Load your embedding model in LM Studio</li>
        </ol>
      </div>

      <div style={{ padding: '15px', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <span style={{ fontWeight: 'bold' }}>Connection Status</span>
          <button
            onClick={checkStatus}
            disabled={loading}
            style={{
              padding: '6px 12px',
              backgroundColor: loading ? '#ccc' : '#0066cc',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '13px',
            }}
          >
            {loading ? 'Checking...' : 'Refresh'}
          </button>
        </div>

        {status ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span
              style={{
                display: 'inline-block',
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: status.connected ? '#28a745' : '#dc3545',
              }}
            />
            <span style={{ color: status.connected ? '#28a745' : '#dc3545' }}>
              {status.connected ? 'Connected' : 'Not Connected'}
            </span>
            {status.connected && status.models && status.models.length > 0 && (
              <span style={{ color: '#666', fontSize: '13px' }}>— {status.models[0]}</span>
            )}
          </div>
        ) : (
          <span style={{ color: '#999' }}>Checking...</span>
        )}
      </div>
    </div>
  )
}
