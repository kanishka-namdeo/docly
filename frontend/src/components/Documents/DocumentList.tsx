import { useState, useEffect, useRef } from 'react'
import { Collection, Document } from '../../types'
import { documentsApi } from '../../services/api'

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
      .catch(err => console.error('Failed to load documents:', err))
      .finally(() => setLoading(false))
  }, [collection.id])

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    try {
      const doc: Document = await documentsApi.upload(collection.id, file)
      setDocuments([doc, ...documents])
    } catch (err) {
      console.error('Upload failed:', err)
      alert(`Upload failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
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
    } catch (err) {
      console.error('Delete failed:', err)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'indexed': return '#28a745'
      case 'pending': return '#ffc107'
      case 'error': return '#dc3545'
      default: return '#6c757d'
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexShrink: 0, gap: '15px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h2 style={{ margin: 0, fontSize: '18px' }}>{collection.name}</h2>
          {collection.description && (
            <p style={{ margin: '5px 0 0', color: '#666', fontSize: '14px' }}>{collection.description}</p>
          )}
        </div>
        <div style={{ flexShrink: 0 }}>
        <div>
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            style={{
              padding: '10px 20px',
              backgroundColor: uploading ? '#ccc' : '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: uploading ? 'not-allowed' : 'pointer',
            }}
          >
            {uploading ? 'Uploading...' : 'Upload Document'}
          </button>
        </div>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>Loading documents...</div>
      ) : documents.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
          <p>No documents in this collection</p>
          <p style={{ fontSize: '14px' }}>Upload a document to get started</p>
        </div>
      ) : (
        <div style={{ flex: 1, overflow: 'auto', minHeight: 0 }}>
          <table style={{ width: '100%', minWidth: '600px', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '2px solid #ddd' }}>
                <th style={{ padding: '12px', textAlign: 'left' }}>File Name</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Type</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Size</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Status</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>Updated</th>
                <th style={{ padding: '12px', textAlign: 'left' }}></th>
              </tr>
            </thead>
            <tbody>
              {documents.map(doc => (
                <tr key={doc.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '12px' }}>
                    <div style={{ maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {doc.file_path.split('/').pop() || doc.file_path}
                    </div>
                  </td>
                  <td style={{ padding: '12px', color: '#666' }}>{doc.file_type}</td>
                  <td style={{ padding: '12px', color: '#666' }}>{formatFileSize(doc.file_size)}</td>
                  <td style={{ padding: '12px' }}>
                    <span
                      style={{
                        display: 'inline-block',
                        padding: '4px 8px',
                        borderRadius: '12px',
                        backgroundColor: getStatusColor(doc.status),
                        color: 'white',
                        fontSize: '12px',
                        textTransform: 'capitalize',
                      }}
                    >
                      {doc.status}
                    </span>
                    {doc.status === 'error' && doc.error_message && (
                      <div style={{ fontSize: '11px', color: '#dc3545', marginTop: '4px' }}>
                        {doc.error_message}
                      </div>
                    )}
                  </td>
                  <td style={{ padding: '12px', color: '#666', fontSize: '12px' }}>
                    {doc.updated_at ? new Date(doc.updated_at).toLocaleDateString() : '-'}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    <button
                      onClick={() => handleDelete(doc.id)}
                      style={{
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        color: '#dc3545',
                        padding: '5px',
                        fontSize: '16px',
                      }}
                    >
                      🗑️
                    </button>
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
