import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import FilterComponent from '@/components/FilterComponent.vue'
import axios from 'axios'

// Mock axios
vi.mock('axios')

describe('FilterComponent.vue', () => {
  let wrapper
  const mockShowAlert = vi.fn()

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks()
    
    // Create wrapper with required props and injections
    wrapper = mount(FilterComponent, {
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
    expect(wrapper.find('h2').text()).toBe('Filter Ships')
  })

  it('does not render when show prop is false', async () => {
    await wrapper.setProps({ show: false })
    expect(wrapper.find('.modal-overlay').exists()).toBe(false)
  })

  it('initializes with empty filter values', () => {
    const { filters } = wrapper.vm
    expect(filters.yearFrom).toBeNull()
    expect(filters.yearTo).toBeNull()
    expect(filters.commissionedFrom).toBeNull()
    expect(filters.commissionedTo).toBeNull()
    expect(filters.country).toBe('')
  })

  it('emits close event when close button is clicked', async () => {
    await wrapper.find('.close-btn').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  describe('Filter Controls', () => {
    it('renders all filter inputs', () => {
      expect(wrapper.find('#yearFrom').exists()).toBe(true)
      expect(wrapper.find('#yearTo').exists()).toBe(true)
      expect(wrapper.find('#commissionedFrom').exists()).toBe(true)
      expect(wrapper.find('#commissionedTo').exists()).toBe(true)
      expect(wrapper.find('#country').exists()).toBe(true)
    })

    it('renders all available countries', () => {
      const options = wrapper.findAll('select option')
      // +1 for the "All Countries" option
      expect(options.length).toBe(17)
    })

    it('updates year range inputs', async () => {
      await wrapper.find('#yearFrom').setValue(1940)
      await wrapper.find('#yearTo').setValue(1945)
      
      expect(wrapper.vm.filters.yearFrom).toBe(1940)
      expect(wrapper.vm.filters.yearTo).toBe(1945)
    })

    it('updates commissioned date range inputs', async () => {
      await wrapper.find('#commissionedFrom').setValue(1941)
      await wrapper.find('#commissionedTo').setValue(1946)
      
      expect(wrapper.vm.filters.commissionedFrom).toBe(1941)
      expect(wrapper.vm.filters.commissionedTo).toBe(1946)
    })

    it('updates country selection', async () => {
      await wrapper.find('#country').setValue('USA')
      expect(wrapper.vm.filters.country).toBe('USA')
    })
  })

  describe('Filter Validation', () => {
    it('validates year range', async () => {
      await wrapper.setData({
        filters: {
          yearFrom: 1945,
          yearTo: 1940
        }
      })

      await wrapper.find('.filter-action-btn.apply').trigger('click')
      expect(mockShowAlert).toHaveBeenCalledWith('End year cannot be less than start year', 'warning')
      expect(wrapper.emitted('filter-results')).toBeFalsy()
    })

    it('validates commissioned date range', async () => {
      await wrapper.setData({
        filters: {
          commissionedFrom: 1945,
          commissionedTo: 1940
        }
      })

      await wrapper.find('.filter-action-btn.apply').trigger('click')
      expect(mockShowAlert).toHaveBeenCalledWith(
        'End commissioned date cannot be less than start commissioned date',
        'warning'
      )
      expect(wrapper.emitted('filter-results')).toBeFalsy()
    })
  })

  describe('Filter Application', () => {
    it('successfully applies filters', async () => {
      const filterResults = [
        { id: 1, name: 'USS Enterprise', year_built: 1942 },
        { id: 2, name: 'USS Voyager', year_built: 1943 }
      ]
      
      axios.get.mockResolvedValueOnce({ data: filterResults })

      await wrapper.setData({
        filters: {
          yearFrom: 1940,
          yearTo: 1945,
          country: 'USA'
        }
      })

      await wrapper.find('.filter-action-btn.apply').trigger('click')

      expect(axios.get).toHaveBeenCalledWith(
        'http://localhost:8000/ships/filter/?year_from=1940&year_to=1945&country=USA'
      )
      expect(wrapper.emitted('filter-results')).toBeTruthy()
      expect(wrapper.emitted('filter-results')[0][0]).toEqual(filterResults)
      expect(mockShowAlert).toHaveBeenCalledWith('Filters applied successfully', 'success')
    })

    it('handles no results found', async () => {
      axios.get.mockResolvedValueOnce({ data: [] })

      await wrapper.setData({
        filters: {
          yearFrom: 1940,
          yearTo: 1945
        }
      })

      await wrapper.find('.filter-action-btn.apply').trigger('click')
      expect(mockShowAlert).toHaveBeenCalledWith('No ships found matching these filters.', 'warning')
      expect(wrapper.emitted('filter-results')).toBeFalsy()
    })

    it('handles API errors', async () => {
      const error = new Error('API Error')
      error.response = { data: { detail: 'Server error' } }
      axios.get.mockRejectedValueOnce(error)

      await wrapper.find('.filter-action-btn.apply').trigger('click')
      expect(mockShowAlert).toHaveBeenCalledWith('Server error', 'error')
    })
  })

  describe('Clear Filters', () => {
    beforeEach(async () => {
      await wrapper.setData({
        filters: {
          yearFrom: 1940,
          yearTo: 1945,
          commissionedFrom: 1941,
          commissionedTo: 1946,
          country: 'USA'
        }
      })
    })

    it('clears all filter values', async () => {
      await wrapper.find('.filter-action-btn.clear').trigger('click')

      const { filters } = wrapper.vm
      expect(filters.yearFrom).toBeNull()
      expect(filters.yearTo).toBeNull()
      expect(filters.commissionedFrom).toBeNull()
      expect(filters.commissionedTo).toBeNull()
      expect(filters.country).toBe('')
    })

    it('emits clear-filter event when clearing filters', async () => {
      await wrapper.find('.filter-action-btn.clear').trigger('click')
      expect(wrapper.emitted('clear-filter')).toBeTruthy()
      expect(mockShowAlert).toHaveBeenCalledWith('Filters cleared', 'info')
    })
  })
})
