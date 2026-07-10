import ModelConfig from '../components/Settings/ModelConfig'
import EmbeddingConfig from '../components/Settings/EmbeddingConfig'

export default function Settings() {
  return (
    <div style={{ padding: '30px', maxWidth: '900px', margin: '0 auto', height: '100%', overflow: 'auto' }}>
      <h1 style={{ marginBottom: '30px' }}>Settings</h1>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
        <ModelConfig />
        <EmbeddingConfig />
      </div>
    </div>
  )
}
