import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import ModelConfig from '../components/Settings/ModelConfig'
import EmbeddingConfig from '../components/Settings/EmbeddingConfig'
import PreferencesConfig from '../components/Settings/PreferencesConfig'

export default function Settings() {
  return (
    <div className="p-6 max-w-[900px] mx-auto h-full overflow-auto">
      <h1 className="mb-6 text-2xl font-semibold">Settings</h1>

      <Tabs defaultValue="model" className="w-full">
        <TabsList>
          <TabsTrigger value="model">Model</TabsTrigger>
          <TabsTrigger value="embedding">Embedding</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
        </TabsList>
        <TabsContent value="model">
          <ModelConfig />
        </TabsContent>
        <TabsContent value="embedding">
          <EmbeddingConfig />
        </TabsContent>
        <TabsContent value="preferences">
          <PreferencesConfig />
        </TabsContent>
      </Tabs>
    </div>
  )
}
