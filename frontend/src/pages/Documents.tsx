import { useState, useEffect } from 'react'
import { Collection } from '../types'
import { collectionsApi } from '../services/api'
import CollectionList from '../components/Documents/CollectionList'
import DocumentList from '../components/Documents/DocumentList'

export default function Documents() {
  const [collections, setCollections] = useState<Collection[]>([])
  const [selectedCollection, setSelectedCollection] = useState<Collection | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    collectionsApi.list()
      .then(setCollections)
      .catch(err => console.error('Failed to load collections:', err))
      .finally(() => setLoading(false))
  }, [])

  const handleCreateCollection = async (name: string, description?: string) => {
    try {
      const newCollection = await collectionsApi.create({ name, description })
      setCollections([newCollection, ...collections])
      if (!selectedCollection) {
        setSelectedCollection(newCollection)
      }
    } catch (err) {
      console.error('Failed to create collection:', err)
    }
  }

  const handleDeleteCollection = async (id: string) => {
    try {
      await collectionsApi.delete(id)
      setCollections(collections.filter(c => c.id !== id))
      if (selectedCollection?.id === id) {
        setSelectedCollection(null)
      }
    } catch (err) {
      console.error('Failed to delete collection:', err)
    }
  }

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading...</div>
  }

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Collection Sidebar */}
      <div style={{ width: '280px', borderRight: '1px solid #ddd', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '15px', borderBottom: '1px solid #ddd' }}>
          <h2 style={{ margin: 0, fontSize: '18px' }}>Collections</h2>
        </div>
        <CollectionList
          collections={collections}
          selectedId={selectedCollection?.id}
          onSelect={setSelectedCollection}
          onDelete={handleDeleteCollection}
          onCreate={handleCreateCollection}
        />
      </div>

      {/* Document List */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        {selectedCollection ? (
          <DocumentList collection={selectedCollection} />
        ) : (
          <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
            <p>Select a collection to view documents</p>
            <p style={{ fontSize: '14px', marginTop: '10px' }}>
              Or create a new collection from the left panel
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
