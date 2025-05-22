import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import StatisticsComponent from '@/components/StatisticsComponent.vue'
import axios from 'axios'
import { Chart } from 'chart.js'

// Mock Chart.js
vi.mock('chart.js', () => {
  const Chart = vi.fn(() => ({
    destroy: vi.fn()
  }))
  Chart.register = vi.fn()
  return {
    Chart,
    registerables: []
  }
})

// Mock axios
vi.mock('axios')

describe('StatisticsComponent.vue', () => {
  let wrapper

  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks()
    
    // Create wrapper
    wrapper = mount(StatisticsComponent, {
      global: {
        stubs: {
          canvas: true
        }
      }
    })
  })

  it('renders the component', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.ship-visualization').exists()).toBe(true)
  })

  it('initializes with default data', () => {
    expect(wrapper.vm.totalShips).toBe(0)
    expect(wrapper.vm.averageYearBuilt).toBe(0)
    expect(wrapper.vm.mostCommonCountry).toBe('N/A')
    expect(wrapper.vm.activeShips).toBe(0)
    expect(wrapper.vm.isExpanded).toBe(false)
  })

  it('toggles expanded state', async () => {
    const shipContainer = wrapper.find('.ship-container')
    expect(wrapper.vm.isExpanded).toBe(false)
    
    await shipContainer.trigger('click')
    expect(wrapper.vm.isExpanded).toBe(true)
  })

  it('fetches statistics on mount', async () => {
    const mockShips = [
      { id: 1, name: 'USS Enterprise', year_built: 1960, commissioned_date: 1961, stricken_date: 2003, country_of_origin: 'USA' },
      { id: 2, name: 'USS Voyager', year_built: 1970, commissioned_date: 1971, stricken_date: null, country_of_origin: 'USA' },
      { id: 3, name: 'HMS Victory', year_built: 1765, commissioned_date: 1778, stricken_date: null, country_of_origin: 'United Kingdom' }
    ]
    
    axios.get.mockResolvedValueOnce({ data: mockShips })
    
    await wrapper.vm.fetchStatistics()
    
    expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/ships/')
    expect(wrapper.vm.totalShips).toBe(3)
    expect(wrapper.vm.averageYearBuilt).toBe(1898)
    expect(wrapper.vm.mostCommonCountry).toBe('USA')
    expect(wrapper.vm.activeShips).toBe(2)
  })

  it('handles API errors when fetching statistics', async () => {
    const error = new Error('API Error')
    error.response = { data: { detail: 'Server error' } }
    axios.get.mockRejectedValueOnce(error)
    
    await wrapper.vm.fetchStatistics()
    
    expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/ships/')
    expect(wrapper.vm.totalShips).toBe(0)
    expect(wrapper.vm.averageYearBuilt).toBe(0)
    expect(wrapper.vm.mostCommonCountry).toBe('N/A')
    expect(wrapper.vm.activeShips).toBe(0)
  })
}) 