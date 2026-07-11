import { useState, useEffect } from 'react'
import { settingsApi } from '../../services/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

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
    <Card>
      <CardHeader>
        <CardTitle>Preferences</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="theme-select">Theme</Label>
          <Select value={theme} onValueChange={handleThemeChange}>
            <SelectTrigger id="theme-select">
              <SelectValue placeholder="Select theme" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="light">Light</SelectItem>
              <SelectItem value="dark">Dark</SelectItem>
              <SelectItem value="system">System</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-sm text-muted-foreground">
            Choose how the app looks. System follows your device settings.
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="language-select">Language</Label>
          <Select value={language} onValueChange={handleLanguageChange}>
            <SelectTrigger id="language-select">
              <SelectValue placeholder="Select language" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="en">English</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-sm text-muted-foreground">
            More languages coming soon.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
