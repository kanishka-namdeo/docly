import { useState, useEffect } from 'react'
import { ProviderConfig } from '../../types'
import { settingsApi } from '../../services/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { toast } from 'sonner'
import { Pencil, X, Star } from 'lucide-react'

const BUILTIN_PROVIDERS = [
  { value: 'anthropic', label: 'Anthropic (Claude)' },
  { value: 'openai', label: 'OpenAI (GPT)' },
  { value: 'google', label: 'Google (Gemini)' },
]

export default function ModelConfig() {
  const [providers, setProviders] = useState<ProviderConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [editingProviderId, setEditingProviderId] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    type: 'builtin' as 'builtin' | 'custom',
    provider_name: 'anthropic',
    model: 'claude-sonnet-4-20250514',
    base_url: '',
    api_key_ref: '',
  })
  const [testingConnection, setTestingConnection] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; error: string | null } | null>(null)
  const [showForm, setShowForm] = useState(false)

  useEffect(() => {
    settingsApi.listProviders()
      .then(setProviders)
      .catch(err => console.error('Failed to load providers:', err))
      .finally(() => setLoading(false))
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingProviderId) {
        // Update existing provider
        const updatedProvider = await settingsApi.updateProvider(editingProviderId, {
          name: formData.name,
          type: formData.type,
          provider_name: formData.provider_name,
          model: formData.model,
          base_url: formData.type === 'custom' ? formData.base_url : undefined,
          api_key: formData.api_key_ref || undefined,
        })
        setProviders(providers.map(p => p.id === editingProviderId ? updatedProvider : p))
        toast.success('Provider updated successfully')
      } else {
        // Create new provider
        const newProvider = await settingsApi.createProvider({
          name: formData.name,
          type: formData.type,
          provider_name: formData.provider_name,
          model: formData.model,
          base_url: formData.type === 'custom' ? formData.base_url : undefined,
          api_key_ref: formData.api_key_ref || undefined,
        })
        setProviders([...providers, newProvider])
        toast.success('Provider added successfully')
      }
      setShowForm(false)
      setEditingProviderId(null)
      setFormData({
        name: '',
        type: 'builtin',
        provider_name: 'anthropic',
        model: 'claude-sonnet-4-20250514',
        base_url: '',
        api_key_ref: '',
      })
      setTestResult(null)
    } catch (err) {
      console.error('Failed to save provider:', err)
      toast.error('Failed to save provider')
    }
  }

  const handleEdit = (provider: ProviderConfig) => {
    setEditingProviderId(provider.id)
    setFormData({
      name: provider.name,
      type: provider.type as 'builtin' | 'custom',
      provider_name: provider.provider_name,
      model: provider.model,
      base_url: provider.base_url || '',
      api_key_ref: '',
    })
    setShowForm(true)
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this provider configuration?')) return
    try {
      await settingsApi.deleteProvider(id)
      setProviders(providers.filter(p => p.id !== id))
      toast.success('Provider deleted')
    } catch (err) {
      console.error('Failed to delete provider:', err)
      toast.error('Failed to delete provider')
    }
  }

  const handleSetDefault = async (id: string) => {
    try {
      await settingsApi.setDefaultProvider(id)
      const updatedProviders = await settingsApi.listProviders()
      setProviders(updatedProviders)
      toast.success('Default provider updated')
    } catch (err) {
      console.error('Failed to set default provider:', err)
      toast.error('Failed to set default provider')
    }
  }

  const handleTestConnection = async () => {
    setTestingConnection(true)
    setTestResult(null)
    try {
      const result = await settingsApi.testProvider({
        name: formData.name,
        type: formData.type,
        provider_name: formData.provider_name,
        model: formData.model,
        base_url: formData.type === 'custom' ? formData.base_url : undefined,
        api_key: formData.api_key_ref || undefined,
      })
      setTestResult(result)
      if (result.success) {
        toast.success('Connection test successful!')
      } else {
        toast.error(`Connection failed: ${result.error}`)
      }
    } catch (err) {
      setTestResult({ success: false, error: err instanceof Error ? err.message : 'Unknown error' })
      toast.error('Connection test failed')
    } finally {
      setTestingConnection(false)
    }
  }

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading...</div>

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <CardTitle className="text-xl font-semibold">Model Configuration</CardTitle>
        <Button
          variant="secondary"
          onClick={() => {
            setShowForm(!showForm)
            if (showForm) {
              setEditingProviderId(null)
              setFormData({
                name: '',
                type: 'builtin',
                provider_name: 'anthropic',
                model: 'claude-sonnet-4-20250514',
                base_url: '',
                api_key_ref: '',
              })
              setTestResult(null)
            }
          }}
        >
          {showForm ? 'Cancel' : '+ Add Provider'}
        </Button>
      </CardHeader>
      <CardContent>
        {showForm && (
          <form onSubmit={handleSubmit} className="mb-6 p-4 bg-muted rounded-md space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="My Claude Config"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="type">Type</Label>
              <Select
                value={formData.type}
                onValueChange={(value) => setFormData({ ...formData, type: value as 'builtin' | 'custom' })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="builtin">Builtin</SelectItem>
                  <SelectItem value="custom">Custom (OpenAI-compatible)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {formData.type === 'builtin' ? (
              <div className="space-y-2">
                <Label htmlFor="provider">Provider</Label>
                <Select
                  value={formData.provider_name}
                  onValueChange={(value) => setFormData({ ...formData, provider_name: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select provider" />
                  </SelectTrigger>
                  <SelectContent>
                    {BUILTIN_PROVIDERS.map(p => (
                      <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            ) : (
              <div className="space-y-2">
                <Label htmlFor="base_url">Base URL</Label>
                <Input
                  id="base_url"
                  type="url"
                  value={formData.base_url}
                  onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
                  placeholder="https://api.example.com/v1"
                  required
                />
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="model">Model</Label>
              <Input
                id="model"
                type="text"
                value={formData.model}
                onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                placeholder="claude-sonnet-4-20250514"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="api_key">API Key (optional)</Label>
              <Input
                id="api_key"
                type="password"
                value={formData.api_key_ref}
                onChange={(e) => setFormData({ ...formData, api_key_ref: e.target.value })}
                placeholder="sk-..."
              />
            </div>

            {testResult && (
              <div className={`p-2 mb-2 rounded border ${
                testResult.success
                  ? 'bg-green-100 border-green-400 text-green-800 dark:bg-green-900 dark:border-green-700 dark:text-green-200'
                  : 'bg-red-100 border-red-400 text-red-800 dark:bg-red-900 dark:border-red-700 dark:text-red-200'
              }`}>
                {testResult.success ? '✓ Connection successful!' : `✗ Connection failed: ${testResult.error}`}
              </div>
            )}

            <div className="flex gap-2">
              <Button
                type="button"
                variant={testResult?.success ? "default" : "secondary"}
                onClick={handleTestConnection}
                disabled={testingConnection}
              >
                {testingConnection ? 'Testing...' : 'Test Connection'}
              </Button>
            </div>

            <Button type="submit">
              {editingProviderId ? 'Update Provider' : 'Add Provider'}
            </Button>
          </form>
        )}

        {providers.length === 0 ? (
          <p className="text-muted-foreground text-center py-8">
            No provider configurations. Add one to get started.
          </p>
        ) : (
          <div className="space-y-2">
            {providers.map(provider => (
              <div
                key={provider.id}
                className="p-4 border rounded-md flex justify-between items-center"
              >
                <div className="flex-1">
                  <div className="font-semibold">{provider.name}</div>
                  <div className="text-sm text-muted-foreground">
                    {provider.provider_name} — {provider.model}
                    {provider.base_url && ` (${provider.base_url})`}
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleSetDefault(provider.id)}
                    title={provider.is_default ? 'Default provider' : 'Set as default'}
                    className={provider.is_default ? 'text-yellow-500 hover:text-yellow-600' : 'text-muted-foreground'}
                  >
                    <Star className="h-4 w-4" fill={provider.is_default ? 'currentColor' : 'none'} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleEdit(provider)}
                    title="Edit provider"
                  >
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDelete(provider.id)}
                    title="Delete provider"
                    className="text-destructive hover:text-destructive"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
