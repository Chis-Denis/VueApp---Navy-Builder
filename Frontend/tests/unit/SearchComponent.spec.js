import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import SearchComponent from '@/components/SearchComponent.vue'
import axios from 'axios'

// Mock axios
vi.mock('axios')

describe('SearchComponent.vue', () => {
  let wrapper
  const mockShowAlert = vi.fn()

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks()
    
    // Create wrapper with required props and injections
    wrapper = mount(SearchComponent, {
      props: {
        show: true
      },
      global: {
        provide: {
          showAlert: mockShowAlert
        }
      }
    })
  })

  it('renders properly when show prop is true', () => {
    expect(wrapper.find('.modal-overlay').exists()).toBe(true)
    expect(wrapper.find('h2').text()).toBe('Search Ships')
  })

  it('does not render when show prop is false', async () => {
    await wrapper.setProps({ show: false })
    expect(wrapper.find('.modal-overlay').exists()).toBe(false)
  })

  it('initializes with empty search query', () => {
    expect(wrapper.vm.searchQuery).toBe('')
    expect(wrapper.vm.hasSearchResults).toBe(false)
  })

  it('emits close event when close button is clicked', async () => {
    await wrapper.find('.close-btn').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
    expect(wrapper.vm.searchQuery).toBe('')
  })

  describe('Search Functionality', () => {
    it('shows warning when search query is empty', async () => {
      await wrapper.find('.search-action-btn').trigger('click')
      expect(mockShowAlert).toHaveBeenCalledWith('Please enter a search term', 'warning')
    })

    it('successfully searches ships', async () => {
      const searchResults = [
        { id: 1, name: 'USS Enterprise' },
        { id: 2, name: 'USS Voyager' }
      ]
      
      axios.get.mockResolvedValueOnce({ data: searchResults })

      await wrapper.setData({ searchQuery: 'USS' })
      await wrapper.find('.search-action-btn').trigger('click')

      expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/ships/search/?query=USS')
      expect(wrapper.emitted('search-results')).toBeTruthy()
      expect(wrapper.emitted('search-results')[0][0]).toEqual(searchResults)
      expect(mockShowAlert).toHaveBeenCalledWith('Search completed successfully', 'success')
      expect(wrapper.vm.hasSearchResults).toBe(true)
    })

    it('handles no results found', async () => {
      axios.get.mockResolvedValueOnce({ data: [] })

      await wrapper.setData({ searchQuery: 'NonexistentShip' })
      await wrapper.find('.search-action-btn').trigger('click')

      expect(mockShowAlert).toHaveBeenCalledWith('No ships found matching your search.', 'warning')
      expect(wrapper.emitted('search-results')).toBeFalsy()
    })

    it('handles API errors', async () => {
      const error = new Error('API Error')
      error.response = { data: { detail: 'Server error' } }
      axios.get.mockRejectedValueOnce(error)

      await wrapper.setData({ searchQuery: 'USS' })
      await wrapper.find('.search-action-btn').trigger('click')

      expect(mockShowAlert).toHaveBeenCalledWith('Server error', 'error')
    })

    it('triggers search on enter key', async () => {
      const searchResults = [{ id: 1, name: 'USS Enterprise' }]
      axios.get.mockResolvedValueOnce({ data: searchResults })

      await wrapper.setData({ searchQuery: 'USS' })
      await wrapper.find('input').trigger('keyup.enter')

      expect(axios.get).toHaveBeenCalled()
      expect(wrapper.emitted('search-results')).toBeTruthy()
    })
  })

  describe('Clear Search Functionality', () => {
    beforeEach(async () => {
      await wrapper.setData({
        searchQuery: 'USS',
        hasSearchResults: true
      })
    })

    it('shows clear button when there are search results', () => {
      expect(wrapper.find('.clear-button').exists()).toBe(true)
    })

    it('hides clear button when there are no search results', async () => {
      await wrapper.setData({ hasSearchResults: false })
      expect(wrapper.find('.clear-button').exists()).toBe(false)
    })

    it('clears search when clear button is clicked', async () => {
      await wrapper.find('.clear-button').trigger('click')

      expect(wrapper.vm.searchQuery).toBe('')
      expect(wrapper.vm.hasSearchResults).toBe(false)
      expect(wrapper.emitted('clear-search')).toBeTruthy()
      expect(mockShowAlert).toHaveBeenCalledWith('Search cleared', 'info')
    })
  })

  describe('Input Handling', () => {
    it('trims whitespace from search query', async () => {
      await wrapper.find('input').setValue('  USS Enterprise  ')
      expect(wrapper.vm.searchQuery).toBe('USS Enterprise')
    })
  })
})
