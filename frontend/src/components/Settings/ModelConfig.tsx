import { useState, useEffect } from 'react'
import { ProviderConfig } from '../../types'
import { settingsApi } from '../../services/api'

const BUILTIN_PROVIDERS = [
  { value: 'anthropic', label: 'Anthropic (Claude)' },
  { value: 'openai', label: 'OpenAI (GPT)' },
  { value: 'google', label: 'Google (Gemini)' },
]

export default function ModelConfig() {
  const [providers, setProviders] = useState<ProviderConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    type: 'builtin' as 'builtin' | 'custom',
    provider_name: 'anthropic',
    model: 'claude-sonnet-4-20250514',
    base_url: '',
    api_key_ref: '',
  })

  useEffect(() => {
    settingsApi.listProviders()
      .then(setProviders)
      .catch(err => console.error('Failed to load providers:', err))
      .finally(() => setLoading(false))
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const newProvider = await settingsApi.createProvider({
        name: formData.name,
        type: formData.type,
        provider_name: formData.provider_name,
        model: formData.model,
        base_url: formData.type === 'custom' ? formData.base_url : undefined,
        api_key_ref: formData.api_key_ref || undefined,
      })
      setProviders([...providers, newProvider])
      setShowForm(false)
      setFormData({
        name: '',
        type: 'builtin',
        provider_name: 'anthropic',
        model: 'claude-sonnet-4-20250514',
        base_url: '',
        api_key_ref: '',
      })
    } catch (err) {
      console.error('Failed to create provider:', err)
      alert('Failed to create provider')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this provider configuration?')) return
    try {
      await settingsApi.deleteProvider(id)
      setProviders(providers.filter(p => p.id !== id))
    } catch (err) {
      console.error('Failed to delete provider:', err)
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0 }}>Model Configuration</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          style={{
            padding: '8px 16px',
            backgroundColor: '#0066cc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          {showForm ? 'Cancel' : '+ Add Provider'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="My Claude Config"
              style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
              required
            />
          </div>

          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Type</label>
            <select
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value as 'builtin' | 'custom' })}
              style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
            >
              <option value="builtin">Builtin</option>
              <option value="custom">Custom (OpenAI-compatible)</option>
            </select>
          </div>

          {formData.type === 'builtin' ? (
            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Provider</label>
              <select
                value={formData.provider_name}
                onChange={(e) => setFormData({ ...formData, provider_name: e.target.value })}
                style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
              >
                {BUILTIN_PROVIDERS.map(p => (
                  <option key={p.value} value={p.value}>{p.label}</option>
                ))}
              </select>
            </div>
          ) : (
            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Base URL</label>
              <input
                type="url"
                value={formData.base_url}
                onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
                placeholder="https://api.example.com/v1"
                style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                required
              />
            </div>
          )}

          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Model</label>
            <input
              type="text"
              value={formData.model}
              onChange={(e) => setFormData({ ...formData, model: e.target.value })}
              placeholder="claude-sonnet-4-20250514"
              style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
              required
            />
          </div>

          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>API Key (optional)</label>
            <input
              type="password"
              value={formData.api_key_ref}
              onChange={(e) => setFormData({ ...formData, api_key_ref: e.target.value })}
              placeholder="sk-..."
              style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
            />
          </div>

          <button
            type="submit"
            style={{
              padding: '10px 20px',
              backgroundColor: '#0066cc',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Add Provider
          </button>
        </form>
      )}

      {providers.length === 0 ? (
        <p style={{ color: '#999', textAlign: 'center', padding: '20px' }}>
          No provider configurations. Add one to get started.
        </p>
      ) : (
        <div>
          {providers.map(provider => (
            <div
              key={provider.id}
              style={{
                padding: '15px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                marginBottom: '10px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <div style={{ fontWeight: 'bold' }}>{provider.name}</div>
                <div style={{ fontSize: '13px', color: '#666' }}>
                  {provider.provider_name} — {provider.model}
                  {provider.base_url && ` (${provider.base_url})`}
                </div>
              </div>
              <button
                onClick={() => handleDelete(provider.id)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: '#dc3545',
                  fontSize: '18px',
                  padding: '5px',
                }}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
