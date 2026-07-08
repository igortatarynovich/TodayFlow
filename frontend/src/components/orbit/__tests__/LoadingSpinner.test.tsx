import { render, screen } from '@testing-library/react'
import { LoadingSpinner } from '../LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders loading spinner', () => {
    render(<LoadingSpinner />)
    const spinner = screen.getByLabelText('Loading')
    expect(spinner).toBeInTheDocument()
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<LoadingSpinner size="sm" />)
    expect(screen.getByLabelText('Loading')).toBeInTheDocument()

    rerender(<LoadingSpinner size="md" />)
    expect(screen.getByLabelText('Loading')).toBeInTheDocument()

    rerender(<LoadingSpinner size="lg" />)
    expect(screen.getByLabelText('Loading')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<LoadingSpinner className="custom-class" />)
    const spinner = screen.getByLabelText('Loading')
    expect(spinner).toHaveClass('custom-class')
  })
})

