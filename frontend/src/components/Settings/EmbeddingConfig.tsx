import { useState, useEffect } from 'react'
import { LMStudioStatus } from '../../types'
import { settingsApi } from '../../services/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { toast } from 'sonner'

export default function EmbeddingConfig() {
  const [status, setStatus] = useState<LMStudioStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState<string>('')

  const checkStatus = async () => {
    setLoading(true)
    try {
      const s = await settingsApi.checkLMStudio()
      setStatus(s)
      if (s.model) {
        setSelectedModel(s.model)
      }
    } catch (err) {
      console.error('Failed to check LM Studio status:', err)
      toast.error('Failed to check LM Studio status')
      setStatus({ connected: false, url: 'http://localhost:1234', model: null, models: null, error: null })
    } finally {
      setLoading(false)
    }
  }

  const handleModelChange = async (model: string) => {
    try {
      await settingsApi.setEmbeddingModel(model)
      setSelectedModel(model)
      setStatus(prev => prev ? { ...prev, model } : null)
      toast.success('Embedding model updated')
    } catch (err) {
      console.error('Failed to set embedding model:', err)
      toast.error('Failed to change embedding model')
    }
  }

  useEffect(() => {
    checkStatus()
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Embedding Configuration</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-3">
          <h3 className="text-base font-semibold">LM Studio Setup</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            The embedding model runs locally via <strong>LM Studio</strong>. Follow these steps to set it up:
          </p>
          <ol className="text-sm text-foreground space-y-1 list-decimal list-inside">
            <li>Download and install <a href="https://lmstudio.ai" target="_blank" rel="noopener noreferrer" className="text-primary underline">LM Studio</a></li>
            <li>Download an embedding model (e.g., <code className="bg-muted px-1 rounded">nomic-embed-text</code> or <code className="bg-muted px-1 rounded">mxbai-embed-large</code>)</li>
            <li>Start the local inference server (default: <code className="bg-muted px-1 rounded">http://localhost:1234</code>)</li>
            <li>Load your embedding model in LM Studio</li>
          </ol>
        </div>

        <div className="rounded-lg bg-muted p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="font-semibold text-sm">Connection Status</span>
            <Button
              onClick={checkStatus}
              disabled={loading}
              variant={loading ? "secondary" : "default"}
              size="sm"
            >
              {loading ? 'Checking...' : 'Refresh'}
            </Button>
          </div>

          {status ? (
            <div className="flex items-center gap-2.5">
              <span
                className={`inline-block w-3 h-3 rounded-full ${
                  status.connected ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className={status.connected ? 'text-green-600 dark:text-green-400 text-sm' : 'text-red-600 dark:text-red-400 text-sm'}>
                {status.connected ? 'Connected' : 'Not Connected'}
              </span>
              {status.connected && status.models && status.models.length > 0 && (
                <div className="mt-2 w-full">
                  <Label htmlFor="embedding-model" className="text-xs text-muted-foreground mb-1.5 block">
                    Embedding Model
                  </Label>
                  <Select value={selectedModel} onValueChange={handleModelChange}>
                    <SelectTrigger id="embedding-model" className="w-full">
                      <SelectValue placeholder="Select a model" />
                    </SelectTrigger>
                    <SelectContent>
                      {status.models.map((model) => (
                        <SelectItem key={model} value={model}>
                          {model}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          ) : (
            <span className="text-sm text-muted-foreground">Checking...</span>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
