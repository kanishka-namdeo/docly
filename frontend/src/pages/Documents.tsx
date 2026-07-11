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
  const handleRenameCollection = async (id: string, name: string) => {
    try {
      const updated = await collectionsApi.update(id, { name })
      setCollections(collections.map(c => c.id === id ? updated : c))
      if (selectedCollection?.id === id) {
        setSelectedCollection(updated)
      }
    } catch (err) {
      console.error('Failed to rename collection:', err)
    }
  }

  if (loading) {
    return <div className="p-6">Loading...</div>
  }

  return (
    <div className="flex h-full min-h-0">
      {/* Collection Sidebar */}
      <div className="w-[280px] flex-shrink-0 border-r border-border flex flex-col h-full">
        <div className="p-4 border-b border-border">
          <h2 className="m-0 text-lg font-semibold">Collections</h2>
        </div>
        <CollectionList
          collections={collections}
          selectedId={selectedCollection?.id}
          onSelect={setSelectedCollection}
          onDelete={handleDeleteCollection}
          onCreate={handleCreateCollection}
          onRename={handleRenameCollection}
        />
      </div>

      {/* Document List */}
      <div className="flex-1 min-w-0 overflow-auto">
        {selectedCollection ? (
          <DocumentList collection={selectedCollection} />
        ) : (
          <div className="p-8 text-center text-muted-foreground">
            <p>Select a collection to view documents</p>
            <p className="text-sm mt-2">
              Or create a new collection from the left panel
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
