import { useState, useEffect } from 'react'
import { settingsApi } from '../../services/api'

export default function PreferencesConfig() {
  const [theme, setTheme] = useState<string>('system')
  const [language, setLanguage] = useState<string>('en')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadPreferences()
  }, [])

  const loadPreferences = async () => {
    try {
      const prefs = await settingsApi.getPreferences()
      setTheme(prefs.theme)
      setLanguage(prefs.language)
    } catch (err) {
      console.error('Failed to load preferences:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleThemeChange = async (newTheme: string) => {
    try {
      await settingsApi.updatePreferences({ theme: newTheme })
      setTheme(newTheme)
      applyTheme(newTheme)
    } catch (err) {
      console.error('Failed to update theme:', err)
    }
  }

  const handleLanguageChange = async (newLanguage: string) => {
    try {
      await settingsApi.updatePreferences({ language: newLanguage })
      setLanguage(newLanguage)
    } catch (err) {
      console.error('Failed to update language:', err)
    }
  }

  const applyTheme = (themeValue: string) => {
    const root = document.documentElement
    
    if (themeValue === 'dark') {
      root.setAttribute('data-theme', 'dark')
    } else if (themeValue === 'light') {
      root.setAttribute('data-theme', 'light')
    } else {
      // system
      root.removeAttribute('data-theme')
    }
  }

  useEffect(() => {
    applyTheme(theme)
  }, [])

  if (loading) return <div>Loading...</div>

  return (
    <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px' }}>
      <h2 style={{ margin: '0 0 20px' }}>Preferences</h2>

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          Theme
        </label>
        <select
          value={theme}
          onChange={(e) => handleThemeChange(e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '14px',
          }}
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
          <option value="system">System</option>
        </select>
        <p style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
          Choose how the app looks. System follows your device settings.
        </p>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          Language
        </label>
        <select
          value={language}
          onChange={(e) => handleLanguageChange(e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '14px',
          }}
        >
          <option value="en">English</option>
        </select>
        <p style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
          More languages coming soon.
        </p>
      </div>
    </div>
  )
}
