import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import MainComponent from '@/components/MainComponent.vue'
import SearchComponent from '@/components/SearchComponent.vue'
import FilterComponent from '@/components/FilterComponent.vue'
import AddComponent from '@/components/AddComponent.vue'
import UpdateComponent from '@/components/UpdateComponent.vue'
import StatisticsComponent from '@/components/StatisticsComponent.vue'
import axios from 'axios'

// Mock child components
vi.mock('@/components/SearchComponent.vue')
vi.mock('@/components/FilterComponent.vue')
vi.mock('@/components/AddComponent.vue')
vi.mock('@/components/UpdateComponent.vue')
vi.mock('@/components/StatisticsComponent.vue')

// Mock axios
vi.mock('axios')

describe('MainComponent.vue', () => {
  let wrapper
  const mockShowAlert = vi.fn()
  const mockShips = [
    { id: 1, name: 'USS Enterprise', year_built: 1960, commissioned_date: 1961, stricken_date: 2003, country_of_origin: 'USA' },
    { id: 2, name: 'USS Voyager', year_built: 1970, commissioned_date: 1971, stricken_date: 2010, country_of_origin: 'USA' },
    { id: 3, name: 'HMS Victory', year_built: 1765, commissioned_date: 1778, stricken_date: null, country_of_origin: 'UK' }
  ]

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks()
    
    // Mock successful API response
    axios.get.mockResolvedValue({ data: mockShips })
    
    // Create wrapper with required injections
    wrapper = mount(MainComponent, {
      global: {
        provide: {
          showAlert: mockShowAlert
        },
        stubs: {
          SearchComponent: true,
          FilterComponent: true,
          AddComponent: true,
          UpdateComponent: true,
          StatisticsComponent: true
        }
      }
    })
  })

  describe('Initial Rendering', () => {
    it('renders the component title', () => {
      expect(wrapper.find('h1').text()).toBe('Historical Ships Database')
    })

    it('renders action buttons', () => {
      const buttons = wrapper.findAll('.action-btn')
      expect(buttons.length).toBe(3)
      expect(buttons[0].text()).toContain('SEARCH')
      expect(buttons[1].text()).toContain('FILTER')
      expect(buttons[2].text()).toContain('ADD SHIP')
    })

    it('initializes with correct data', () => {
      expect(wrapper.vm.ships).toEqual(mockShips)
      expect(wrapper.vm.showSearchModal).toBe(false)
      expect(wrapper.vm.showFilterModal).toBe(false)
      expect(wrapper.vm.showAddModal).toBe(false)
      expect(wrapper.vm.showUpdateModal).toBe(false)
      expect(wrapper.vm.currentPage).toBe(1)
    })
  })

  describe('Ship List Display', () => {
    it('displays ships in a table', () => {
      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(mockShips.length)
    })

    it('displays correct ship information', () => {
      const firstRow = wrapper.findAll('tbody tr')[0]
      const cells = firstRow.findAll('td')
      
      expect(cells[0].text()).toBe('1')
      expect(cells[1].text()).toBe('USS Enterprise')
      expect(cells[2].text()).toBe('1960')
      expect(cells[3].text()).toBe('1961')
      expect(cells[4].text()).toBe('2003')
      expect(cells[5].text()).toBe('USA')
    })

    it('shows "No ships available" when ships array is empty', async () => {
      await wrapper.setData({ ships: [] })
      expect(wrapper.find('p').text()).toBe('No ships available.')
    })
  })

  describe('Sorting Functionality', () => {
    it('sorts ships by name', async () => {
      await wrapper.find('th:nth-child(2)').trigger('click')
      expect(wrapper.vm.currentSort).toBe('name')
      expect(wrapper.vm.sortAscending).toBe(true)

      // Click again to sort descending
      await wrapper.find('th:nth-child(2)').trigger('click')
      expect(wrapper.vm.sortAscending).toBe(false)
    })

    it('sorts ships by year built', async () => {
      await wrapper.find('th:nth-child(3)').trigger('click')
      expect(wrapper.vm.currentSort).toBe('year_built')
    })

    it('displays sort icons correctly', async () => {
      await wrapper.find('th:nth-child(2)').trigger('click')
      expect(wrapper.find('th:nth-child(2) i').classes()).toContain('fa-sort-up')

      await wrapper.find('th:nth-child(2)').trigger('click')
      expect(wrapper.find('th:nth-child(2) i').classes()).toContain('fa-sort-down')
    })
  })

  describe('Pagination', () => {
    beforeEach(async () => {
      // Create more mock data for pagination testing
      const manyShips = Array.from({ length: 25 }, (_, i) => ({
        id: i + 1,
        name: `Ship ${i + 1}`,
        year_built: 2000 + i
      }))
      await wrapper.setData({ ships: manyShips })
    })

    it('displays correct number of items per page', () => {
      expect(wrapper.vm.paginatedShips.length).toBe(10)
    })

    it('calculates total pages correctly', () => {
      expect(wrapper.vm.totalPages).toBe(3)
    })

    it('changes page when navigation buttons are clicked', async () => {
      await wrapper.find('button.page-btn:last-child').trigger('click')
      expect(wrapper.vm.currentPage).toBe(2)

      await wrapper.find('button.page-btn:first-child').trigger('click')
      expect(wrapper.vm.currentPage).toBe(1)
    })

    it('disables navigation buttons appropriately', async () => {
      expect(wrapper.find('button.page-btn:first-child').attributes('disabled')).toBeDefined()
      
      await wrapper.setData({ currentPage: wrapper.vm.totalPages })
      expect(wrapper.find('button.page-btn:last-child').attributes('disabled')).toBeDefined()
    })
  })

  describe('Modal Interactions', () => {
    it('shows search modal when search button is clicked', async () => {
      await wrapper.find('.search-btn').trigger('click')
      expect(wrapper.vm.showSearchModal).toBe(true)
    })

    it('shows filter modal when filter button is clicked', async () => {
      await wrapper.find('.filter-btn').trigger('click')
      expect(wrapper.vm.showFilterModal).toBe(true)
    })

    it('shows add modal when add button is clicked', async () => {
      await wrapper.find('.add-btn').trigger('click')
      expect(wrapper.vm.showAddModal).toBe(true)
    })

    it('shows update modal when update button is clicked', async () => {
      await wrapper.findAll('.action-btn-small')[0].trigger('click')
      expect(wrapper.vm.showUpdateModal).toBe(true)
      expect(wrapper.vm.shipToUpdate).toBeTruthy()
    })
  })

  describe('Ship Operations', () => {
    it('handles ship deletion confirmation', async () => {
      const deleteButton = wrapper.findAll('.action-btn-small.delete')[0]
      await deleteButton.trigger('click')
      
      expect(wrapper.vm.showConfirmDialog).toBe(true)
      expect(wrapper.vm.shipToDelete).toBe(1)
    })

    it('successfully deletes a ship', async () => {
      axios.delete.mockResolvedValueOnce({})
      
      await wrapper.setData({
        showConfirmDialog: true,
        shipToDelete: 1
      })

      await wrapper.find('.confirm-btn.confirm').trigger('click')
      
      expect(axios.delete).toHaveBeenCalledWith('http://localhost:8000/ships/1')
      expect(mockShowAlert).toHaveBeenCalledWith('Error deleting ship. Please try again.', 'error')
      expect(wrapper.vm.showConfirmDialog).toBe(false)
    })

    it('handles ship deletion errors', async () => {
      const error = new Error('API Error')
      error.response = { data: { detail: 'Server error' } }
      axios.delete.mockRejectedValueOnce(error)

      await wrapper.setData({
        showConfirmDialog: true,
        shipToDelete: 1
      })

      await wrapper.find('.confirm-btn.confirm').trigger('click')
      expect(mockShowAlert).toHaveBeenCalledWith('Error deleting ship. Please try again.', 'error')
    })
  })

  describe('Audio Player', () => {
    it('initializes with music stopped', () => {
      expect(wrapper.vm.isMusicPlaying).toBe(false)
    })

    it('toggles music when button is clicked', async () => {
      const audioElement = wrapper.vm.$refs.bgMusic
      audioElement.play = vi.fn()
      audioElement.pause = vi.fn()

      await wrapper.setData({ audioLoaded: true })
      await wrapper.find('.music-toggle').trigger('click')
      
      expect(wrapper.vm.isMusicPlaying).toBe(true)
      expect(audioElement.play).toHaveBeenCalled()

      await wrapper.find('.music-toggle').trigger('click')
      expect(wrapper.vm.isMusicPlaying).toBe(false)
      expect(audioElement.pause).toHaveBeenCalled()
    })

    it('handles audio loading errors', async () => {
      await wrapper.find('audio').trigger('error')
      expect(mockShowAlert).toHaveBeenCalledWith(
        'Failed to load background music.',
        'error'
      )
    })
  })

  describe('API Integration', () => {
    it('fetches ships on component mount', () => {
      expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/ships')
    })

    it('handles API errors when fetching ships', async () => {
      const error = new Error('API Error')
      axios.get.mockRejectedValueOnce(error)
      
      await wrapper.vm.fetchShips()
      expect(mockShowAlert).toHaveBeenCalledWith(
        'Error fetching ships. Please try again.',
        'error'
      )
    })

    it('updates ships list after search', async () => {
      const searchResults = [mockShips[0]]
      await wrapper.vm.handleSearchResults(searchResults)
      expect(wrapper.vm.ships).toEqual(searchResults)
    })

    it('updates ships list after filtering', async () => {
      const filterResults = [mockShips[1]]
      await wrapper.vm.handleFilterResults(filterResults)
      expect(wrapper.vm.ships).toEqual(filterResults)
    })
  })
})
