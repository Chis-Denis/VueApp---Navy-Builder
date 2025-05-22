import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import AddComponent from '@/components/AddComponent.vue'
import axios from 'axios'

// Mock axios
vi.mock('axios')

describe('AddComponent.vue', () => {
  let wrapper
  const mockShowAlert = vi.fn()

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks()
    
    // Create wrapper with required props and injections
    wrapper = mount(AddComponent, {
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
    expect(wrapper.find('h2').text()).toBe('Add New Ship')
  })

  it('does not render when show prop is false', async () => {
    await wrapper.setProps({ show: false })
    expect(wrapper.find('.modal-overlay').exists()).toBe(false)
  })

  it('initializes with empty form data', () => {
    const { newShip } = wrapper.vm
    expect(newShip.name).toBe('')
    expect(newShip.year_built).toBeNull()
    expect(newShip.commissioned_date).toBeNull()
    expect(newShip.stricken_date).toBeNull()
    expect(newShip.country_of_origin).toBe('')
  })

  it('emits close event when close button is clicked', async () => {
    await wrapper.find('.close-btn').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('clears form when clear button is clicked', async () => {
    // Set some form data
    await wrapper.setData({
      newShip: {
        name: 'Test Ship',
        year_built: 2000,
        commissioned_date: 2001,
        stricken_date: 2020,
        country_of_origin: 'USA'
      }
    })

    // Click clear button
    await wrapper.find('.form-action-btn.clear').trigger('click')

    // Check if form is cleared
    const { newShip } = wrapper.vm
    expect(newShip.name).toBe('')
    expect(newShip.year_built).toBeNull()
    expect(newShip.commissioned_date).toBeNull()
    expect(newShip.stricken_date).toBeNull()
    expect(newShip.country_of_origin).toBe('')
  })

  describe('Form Validation', () => {
    it('shows warning when required fields are missing', async () => {
      await wrapper.find('form').trigger('submit')
      expect(mockShowAlert).toHaveBeenCalledWith(
        'Please fill in all required fields (Name and Year Built).',
        'warning'
      )
    })

    it('validates ship name length', async () => {
      await wrapper.setData({
        newShip: {
          name: 'A', // Too short
          year_built: 2000,
          country_of_origin: 'USA'
        }
      })

      await wrapper.find('form').trigger('submit')
      expect(mockShowAlert).toHaveBeenCalledWith(
        'Ship name must be between 2 and 100 characters',
        'warning'
      )
    })

    it('validates commissioned date logic', async () => {
      await wrapper.setData({
        newShip: {
          name: 'Test Ship',
          year_built: 2000,
          commissioned_date: 1999, // Earlier than year built
          country_of_origin: 'USA'
        }
      })

      await wrapper.find('form').trigger('submit')
      expect(mockShowAlert).toHaveBeenCalledWith(
        'Commissioned date cannot be earlier than year built',
        'warning'
      )
    })

    it('validates stricken date logic', async () => {
      await wrapper.setData({
        newShip: {
          name: 'Test Ship',
          year_built: 2000,
          commissioned_date: 2001,
          stricken_date: 1999, // Earlier than commissioned date
          country_of_origin: 'USA'
        }
      })

      await wrapper.find('form').trigger('submit')
      expect(mockShowAlert).toHaveBeenCalledWith(
        'Stricken date cannot be earlier than commissioned date or year built',
        'warning'
      )
    })
  })

  describe('API Integration', () => {
    it('successfully adds a ship', async () => {
      const newShip = {
        name: 'USS Enterprise',
        year_built: 2000,
        commissioned_date: 2001,
        stricken_date: 2020,
        country_of_origin: 'USA'
      }

      const responseData = { ...newShip, id: 1 }
      axios.post.mockResolvedValueOnce({ data: responseData })

      await wrapper.setData({ newShip })
      await wrapper.find('form').trigger('submit')

      expect(axios.post).toHaveBeenCalledWith('http://localhost:8000/ships', newShip)
      expect(wrapper.emitted('ship-added')).toBeTruthy()
      expect(wrapper.emitted('ship-added')[0][0]).toEqual(responseData)
      expect(mockShowAlert).toHaveBeenCalledWith('Ship added successfully!', 'success')
    })

    it('handles API errors', async () => {
      const error = new Error('API Error')
      error.response = { data: { detail: 'Server error' } }
      axios.post.mockRejectedValueOnce(error)

      await wrapper.setData({
        newShip: {
          name: 'USS Enterprise',
          year_built: 2000,
          country_of_origin: 'USA'
        }
      })

      await wrapper.find('form').trigger('submit')
      expect(mockShowAlert).toHaveBeenCalledWith('Server error', 'error')
    })
  })

  describe('Country Selection', () => {
    it('renders all available countries', () => {
      const options = wrapper.findAll('select option')
      // +1 for the default "Select country" option
      expect(options.length).toBe(17)
    })

    it('updates country selection', async () => {
      const select = wrapper.find('select')
      await select.setValue('USA')
      expect(wrapper.vm.newShip.country_of_origin).toBe('USA')
    })
  })
})
