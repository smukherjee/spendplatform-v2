import React from 'react';
import { ErrorBoundary as ReactErrorBoundary } from 'react-error-boundary';
import * as Sentry from '@sentry/react';
import Bugsnag from 'bugsnag-react-native';
import firebase from 'firebase/app';

// Initialize Sentry (replace with your DSN)
Sentry.init({ dsn: process.env.SENTRY_DSN || '' });

// Initialize Bugsnag (replace with your API key)
Bugsnag.start({ apiKey: process.env.BUGSNAG_API_KEY || '' });

// Initialize Firebase (replace with your config)
if (!firebase.apps.length) {
  firebase.initializeApp({
    apiKey: process.env.FIREBASE_API_KEY || '',
    authDomain: process.env.FIREBASE_AUTH_DOMAIN || '',
    projectId: process.env.FIREBASE_PROJECT_ID || '',
    appId: process.env.FIREBASE_APP_ID || '',
  });
}

function logErrorToServices(error: Error, info: { componentStack: string }) {
  Sentry.captureException(error);
  Bugsnag.notify(error);
  firebase.analytics?.().logEvent('error', { message: error.message, stack: info.componentStack });
}

function FallbackComponent({ error }: { error: Error }) {
  return (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre>{error.message}</pre>
    </div>
  );
}

export default function ErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ReactErrorBoundary FallbackComponent={FallbackComponent} onError={logErrorToServices}>
      {children}
    </ReactErrorBoundary>
  );
}
