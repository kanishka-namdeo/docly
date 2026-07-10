import { useState } from 'react'
import { Citation } from '../../types'

interface CitationCardProps {
  citation: Citation
  index: number
}

export default function CitationCard({ citation, index }: CitationCardProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div
      style={{
        border: '1px solid #ddd',
        borderRadius: '6px',
        padding: '8px',
        maxWidth: '200px',
        backgroundColor: expanded ? '#fff' : '#fafafa',
        cursor: 'pointer',
      }}
      onClick={() => setExpanded(!expanded)}
    >
      <div style={{ fontSize: '11px', color: '#666', marginBottom: '4px' }}>
        [{index}] {citation.file_path.split('/').pop()}
      </div>
      {expanded && (
        <div style={{ fontSize: '12px', color: '#333', marginTop: '4px' }}>
          <div style={{ marginBottom: '4px', fontStyle: 'italic', color: '#888' }}>
            Score: {(citation.score * 100).toFixed(1)}%
          </div>
          <div style={{ maxHeight: '100px', overflow: 'auto', lineHeight: '1.4' }}>
            {citation.text}
          </div>
        </div>
      )}
      {!expanded && (
        <div style={{ fontSize: '10px', color: '#999' }}>
          Click to expand
        </div>
      )}
    </div>
  )
}
