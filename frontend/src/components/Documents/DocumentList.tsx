import { useState, useEffect, useRef } from 'react'
import { Collection, Document } from '../../types'
import { documentsApi } from '../../services/api'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { toast } from 'sonner'

interface DocumentListProps {
  collection: Collection
}

export default function DocumentList({ collection }: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    setLoading(true)
    documentsApi.list(collection.id)
      .then(setDocuments)
      .catch(err => {
        console.error('Failed to load documents:', err)
        toast.error('Failed to load documents')
      })
      .finally(() => setLoading(false))
  }, [collection.id])

  // Poll for status updates when documents are pending
  useEffect(() => {
    const hasPending = documents.some(d => d.status === 'pending')
    if (!hasPending) return

    const interval = setInterval(async () => {
      try {
        const updated = await documentsApi.list(collection.id)
        setDocuments(updated)
      } catch (err) {
        console.error('Poll failed:', err)
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [collection.id, documents.some(d => d.status === 'pending')])

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    try {
      const doc: Document = await documentsApi.upload(collection.id, file)
      setDocuments([doc, ...documents])
      toast.success('Document uploaded successfully')
    } catch (err) {
      console.error('Upload failed:', err)
      toast.error(`Upload failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this document?')) return
    try {
      await documentsApi.delete(id)
      setDocuments(documents.filter(d => d.id !== id))
      toast.success('Document deleted')
    } catch (err) {
      console.error('Delete failed:', err)
      toast.error('Failed to delete document')
    }
  }

  const getStatusBadgeVariant = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
    switch (status) {
      case 'indexed': return 'default'
      case 'pending': return 'secondary'
      case 'error': return 'destructive'
      default: return 'outline'
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="flex flex-col h-full p-5 min-h-0">
      <div className="flex items-start justify-between mb-5 shrink-0 gap-4 flex-wrap">
        <div className="flex-1 min-w-0">
          <h2 className="text-lg font-semibold m-0">{collection.name}</h2>
          {collection.description && (
            <p className="text-sm text-muted-foreground mt-1 mb-0">{collection.description}</p>
          )}
        </div>
        <div className="shrink-0">
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileSelect}
            className="hidden"
          />
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? 'Uploading...' : 'Upload Document'}
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-10">Loading documents...</div>
      ) : documents.length === 0 ? (
        <div className="text-center py-10 text-muted-foreground">
          <p className="mb-2">No documents in this collection</p>
          <p className="text-sm">Upload a document to get started</p>
        </div>
      ) : (
        <div className="flex-1 overflow-auto min-h-0">
          <table className="w-full min-w-[600px]">
            <thead>
              <tr className="bg-muted border-b-2 border-border">
                <th className="p-3 text-left font-medium">File Name</th>
                <th className="p-3 text-left font-medium">Type</th>
                <th className="p-3 text-left font-medium">Size</th>
                <th className="p-3 text-left font-medium">Status</th>
                <th className="p-3 text-left font-medium">Updated</th>
                <th className="p-3"></th>
              </tr>
            </thead>
            <tbody>
              {documents.map(doc => (
                <tr key={doc.id} className="border-b border-border">
                  <td className="p-3">
                    <div className="max-w-[250px] overflow-hidden text-ellipsis whitespace-nowrap">
                      {doc.file_path.split('/').pop() || doc.file_path}
                    </div>
                  </td>
                  <td className="p-3 text-muted-foreground">{doc.file_type}</td>
                  <td className="p-3 text-muted-foreground">{formatFileSize(doc.file_size)}</td>
                  <td className="p-3">
                    <Badge variant={getStatusBadgeVariant(doc.status)} className="capitalize">
                      {doc.status}
                    </Badge>
                    {doc.status === 'error' && doc.error_message && (
                      <div className="text-xs text-destructive mt-1">
                        {doc.error_message}
                      </div>
                    )}
                  </td>
                  <td className="p-3 text-muted-foreground text-xs">
                    {doc.updated_at ? new Date(doc.updated_at).toLocaleDateString() : '-'}
                  </td>
                  <td className="p-3 text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(doc.id)}
                      className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    >
                      🗑️
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
