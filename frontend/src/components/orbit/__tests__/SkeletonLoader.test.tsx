import { render, screen } from '@testing-library/react'
import { SkeletonLoader } from '../SkeletonLoader'

describe('SkeletonLoader', () => {
  it('renders skeleton loader', () => {
    render(<SkeletonLoader />)
    const skeleton = screen.getByLabelText('Loading content')
    expect(skeleton).toBeInTheDocument()
  })

  it('renders multiple lines', () => {
    render(<SkeletonLoader lines={3} />)
    const skeletons = screen.getAllByLabelText('Loading content')
    expect(skeletons).toHaveLength(3)
  })

  it('applies custom width and height', () => {
    render(<SkeletonLoader width="200px" height="20px" />)
    const skeleton = screen.getByLabelText('Loading content')
    expect(skeleton).toHaveStyle({ width: '200px', height: '20px' })
  })
})

