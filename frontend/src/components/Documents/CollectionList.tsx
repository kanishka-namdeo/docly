import { useState } from 'react'
import { Collection } from '../../types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Pencil, Trash2, Plus } from 'lucide-react'

interface CollectionListProps {
  collections: Collection[]
  selectedId?: string
  onSelect: (collection: Collection) => void
  onDelete: (id: string) => void
  onCreate: (name: string, description?: string) => void
  onRename: (id: string, name: string) => void
}

export default function CollectionList({
  collections,
  selectedId,
  onSelect,
  onDelete,
  onCreate,
  onRename,
}: CollectionListProps) {
  const [createOpen, setCreateOpen] = useState(false)
  const [newName, setNewName] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [renameOpen, setRenameOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editName, setEditName] = useState('')
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newName.trim()) return
    onCreate(newName.trim(), newDescription.trim())
    setNewName('')
    setNewDescription('')
    setCreateOpen(false)
  }

  const handleRenameSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (editName.trim() && editName.trim() !== collections.find(c => c.id === editingId)?.name) {
      onRename(editingId!, editName.trim())
    }
    setEditingId(null)
    setRenameOpen(false)
  }

  const handleDeleteConfirm = () => {
    if (deletingId) {
      onDelete(deletingId)
      setDeleteOpen(false)
      setDeletingId(null)
    }
  }

  const openRenameDialog = (collection: Collection) => {
    setEditingId(collection.id)
    setEditName(collection.name)
    setRenameOpen(true)
  }

  const openDeleteDialog = (id: string) => {
    setDeletingId(id)
    setDeleteOpen(true)
  }

  return (
    <ScrollArea className="h-full w-full">
      <div className="p-3 space-y-3">
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button className="w-full" size="default">
              <Plus className="mr-2 h-4 w-4" />
              New Collection
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Collection</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateSubmit}>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="create-name">Name</Label>
                  <Input
                    id="create-name"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder="Collection name"
                    autoFocus
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="create-description">Description (optional)</Label>
                  <Textarea
                    id="create-description"
                    value={newDescription}
                    onChange={(e) => setNewDescription(e.target.value)}
                    placeholder="Description (optional)"
                    rows={2}
                    className="resize-none"
                  />
                </div>
              </div>
              <DialogFooter>
                <DialogClose asChild>
                  <Button type="button" variant="outline" onClick={() => { setNewName(''); setNewDescription('') }}>
                    Cancel
                  </Button>
                </DialogClose>
                <Button type="submit">Create</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {collections.length === 0 ? (
          <p className="text-muted-foreground text-center py-5">No collections yet</p>
        ) : (
          collections.map((collection) => (
            <div
              key={collection.id}
              onClick={() => onSelect(collection)}
              className={`
                p-3 mb-1 rounded-md cursor-pointer flex justify-between items-start gap-2
                ${
                  selectedId === collection.id
                    ? 'bg-primary/10 border-2 border-primary'
                    : 'bg-card border border-border hover:bg-accent/50'
                }
              `}
            >
              <div className="flex-1 overflow-hidden min-w-0">
                <div
                  className="font-semibold mb-1 cursor-text"
                  onDoubleClick={(e) => {
                    e.stopPropagation()
                    openRenameDialog(collection)
                  }}
                  title="Double-click to rename"
                >
                  {collection.name}
                </div>
                {collection.description && (
                  <div className="text-sm text-muted-foreground overflow-hidden text-ellipsis whitespace-nowrap">
                    {collection.description}
                  </div>
                )}
              </div>
              <div className="flex gap-1 shrink-0">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={(e) => {
                    e.stopPropagation()
                    openRenameDialog(collection)
                  }}
                  title="Rename"
                >
                  <Pencil className="h-4 w-4" />
                </Button>
                <AlertDialog open={deleteOpen && deletingId === collection.id} onOpenChange={setDeleteOpen}>
                  <AlertDialogTrigger>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={(e) => {
                        e.stopPropagation()
                        openDeleteDialog(collection.id)
                      }}
                      title="Delete"
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete Collection</AlertDialogTitle>
                      <AlertDialogDescription>
                        Are you sure you want to delete "{collection.name}"? This action cannot be undone.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={handleDeleteConfirm}>Delete</AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </div>
          ))
        )}

        <Dialog open={renameOpen} onOpenChange={setRenameOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Rename Collection</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleRenameSubmit}>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="rename-name">New Name</Label>
                  <Input
                    id="rename-name"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    placeholder="Collection name"
                    autoFocus
                  />
                </div>
              </div>
              <DialogFooter>
                <DialogClose asChild>
                  <Button type="button" variant="outline" onClick={() => setEditingId(null)}>
                    Cancel
                  </Button>
                </DialogClose>
                <Button type="submit">Rename</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </ScrollArea>
  )
}
