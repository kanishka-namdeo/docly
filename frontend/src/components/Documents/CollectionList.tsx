import { useState } from 'react'
import { Collection } from '../../types'

interface CollectionListProps {
  collections: Collection[]
  selectedId?: string
  onSelect: (collection: Collection) => void
  onDelete: (id: string) => void
  onCreate: (name: string, description?: string) => void
}

export default function CollectionList({
  collections,
  selectedId,
  onSelect,
  onDelete,
  onCreate,
}: CollectionListProps) {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newName, setNewName] = useState('')
  const [newDescription, setNewDescription] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newName.trim()) return
    onCreate(newName.trim(), newDescription.trim())
    setNewName('')
    setNewDescription('')
    setShowCreateForm(false)
  }

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '10px' }}>
      <button
        onClick={() => setShowCreateForm(!showCreateForm)}
        style={{
          width: '100%',
          padding: '10px',
          marginBottom: '10px',
          backgroundColor: '#28a745',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
        }}
      >
        + New Collection
      </button>

      {showCreateForm && (
        <form onSubmit={handleSubmit} style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Collection name"
            style={{ width: '100%', padding: '8px', marginBottom: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
          />
          <textarea
            value={newDescription}
            onChange={(e) => setNewDescription(e.target.value)}
            placeholder="Description (optional)"
            rows={2}
            style={{ width: '100%', padding: '8px', marginBottom: '8px', border: '1px solid #ddd', borderRadius: '4px', resize: 'none' }}
          />
          <div style={{ display: 'flex', gap: '5px' }}>
            <button type="submit" style={{ flex: 1, padding: '8px', backgroundColor: '#0066cc', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Create
            </button>
            <button
              type="button"
              onClick={() => { setShowCreateForm(false); setNewName(''); setNewDescription('') }}
              style={{ flex: 1, padding: '8px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {collections.length === 0 ? (
        <p style={{ color: '#999', textAlign: 'center', padding: '20px' }}>No collections yet</p>
      ) : (
        collections.map(collection => (
          <div
            key={collection.id}
            onClick={() => onSelect(collection)}
            style={{
              padding: '12px',
              marginBottom: '5px',
              backgroundColor: selectedId === collection.id ? '#e6f0ff' : '#fff',
              border: selectedId === collection.id ? '2px solid #0066cc' : '1px solid #ddd',
              borderRadius: '4px',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
            }}
          >
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{collection.name}</div>
              {collection.description && (
                <div style={{ fontSize: '12px', color: '#666', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {collection.description}
                </div>
              )}
            </div>
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(collection.id) }}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: '#dc3545',
                fontSize: '18px',
                padding: '0 5px',
              }}
            >
              ×
            </button>
          </div>
        ))
      )}
    </div>
  )
}
