import React from 'react';

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class UserTableErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('UserTable Error:', error, errorInfo);
    
    // Log to monitoring service in production
    if (process.env.NODE_ENV === 'production') {
      // Add your error reporting service here
      // e.g., Sentry, LogRocket, etc.
    }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-4 border border-red-300 rounded-md bg-red-50">
          <div className="flex">
            <div className="flex-shrink-0">
              <i className="pi pi-exclamation-triangle text-red-400"></i>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Something went wrong with the user table
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <p>Please refresh the page to try again.</p>
                {process.env.NODE_ENV === 'development' && this.state.error && (
                  <details className="mt-2">
                    <summary className="cursor-pointer">Error details</summary>
                    <pre className="mt-2 text-xs bg-red-100 p-2 rounded">
                      {this.state.error.stack}
                    </pre>
                  </details>
                )}
              </div>
              <div className="mt-4">
                <button
                  type="button"
                  className="bg-red-100 px-2 py-1 text-sm text-red-800 rounded hover:bg-red-200"
                  onClick={() => window.location.reload()}
                >
                  Refresh Page
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}