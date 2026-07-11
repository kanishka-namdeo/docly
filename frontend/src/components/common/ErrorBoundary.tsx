import { Component, ReactNode } from 'react'
import { Button } from '@/components/ui/button'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo)
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center p-10 max-w-[600px] mx-auto text-center">
          <h2 className="text-destructive mb-4 text-lg font-semibold">Something went wrong</h2>
          <p className="text-muted-foreground mb-5">
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <Button
            onClick={() => { this.setState({ hasError: false, error: null }); window.location.reload() }}
          >
            Reload App
          </Button>
        </div>
      )
    }
    return this.props.children
  }
}
