// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

// jsdom's AbortSignal lacks the static timeout()/any() helpers that exist in
// every real runtime we target (browsers, Node 18+ SSR). Polyfill so code
// using AbortSignal.timeout behaves in tests exactly as in production.
if (typeof AbortSignal.timeout !== 'function') {
  AbortSignal.timeout = (ms) => {
    const controller = new AbortController()
    setTimeout(() => controller.abort(new DOMException('TimeoutError', 'TimeoutError')), ms)
    return controller.signal
  }
}
