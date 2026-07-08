/**
 * Sentry configuration for error tracking and monitoring.
 * 
 * To enable Sentry:
 * 1. Set NEXT_PUBLIC_SENTRY_DSN environment variable
 * 2. Install @sentry/nextjs: npm install @sentry/nextjs
 * 3. Uncomment the code below
 */

/*
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  
  // Adjust this value in production, or use tracesSampler for greater control
  tracesSampleRate: 1.0,
  
  // Setting this option to true will print useful information to the console while you're setting up Sentry.
  debug: false,
  
  // Replay can be used to capture user sessions
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  
  // Filter out sensitive data
  beforeSend(event, hint) {
    // Remove sensitive data from errors
    if (event.request) {
      delete event.request.headers?.['authorization'];
      delete event.request.cookies?.['session'];
    }
    return event;
  },
  
  // Environment
  environment: process.env.NODE_ENV || 'development',
  
  // Release tracking
  release: process.env.NEXT_PUBLIC_APP_VERSION || 'unknown',
});
*/

// Placeholder export for when Sentry is not configured
export const captureException = (error: Error, context?: Record<string, unknown>) => {
  if (process.env.NODE_ENV === 'development') {
    console.error('Error captured:', error, context);
  }
  // Sentry.captureException(error, { extra: context });
};

export const captureMessage = (message: string, level: 'info' | 'warning' | 'error' = 'info') => {
  if (process.env.NODE_ENV === 'development') {
    console.log(`[${level.toUpperCase()}]`, message);
  }
  // Sentry.captureMessage(message, level);
};

export const setUser = (user: { id: string; email?: string }) => {
  // Sentry.setUser(user);
};

export const clearUser = () => {
  // Sentry.setUser(null);
};

