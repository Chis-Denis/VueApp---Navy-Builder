import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import UpdateComponent from '@/components/UpdateComponent.vue'
import axios from 'axios'

// Mock axios
vi.mock('axios')

describe('UpdateComponent.vue', () => {
  let wrapper
  const mockShowAlert = vi.fn()
  const mockShip = {
    id: 1,
    name: 'USS Enterprise',
    year_built: 1960,
    commissioned_date: 1961,
    stricken_date: 2003,
    country_of_origin: 'USA'
  }

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks()
    
    // Create wrapper with required props and injections
    wrapper = mount(UpdateComponent, {
      props: {
        show: true,
        ship: mockShip
      },
      global: {
        provide: {
          showAlert: mockShowAlert
        }
      }
    })
  })

  describe('Rendering', () => {
    it('renders properly when show prop is true', () => {
      expect(wrapper.find('.modal-overlay').exists()).toBe(true)
      expect(wrapper.find('h2').text()).toBe('Update Ship')
    })

    it('does not render when show prop is false', async () => {
      await wrapper.setProps({ show: false })
      expect(wrapper.find('.modal-overlay').exists()).toBe(false)
    })

    it('populates form with ship data', () => {
      expect(wrapper.find('#name').element.value).toBe(mockShip.name)
      expect(wrapper.find('#yearBuilt').element.value).toBe(mockShip.year_built.toString())
      expect(wrapper.find('#commissionedDate').element.value).toBe(mockShip.commissioned_date.toString())
      expect(wrapper.find('#strickenDate').element.value).toBe(mockShip.stricken_date.toString())
      expect(wrapper.find('#country').element.value).toBe(mockShip.country_of_origin)
    })

    it('renders all form fields', () => {
      expect(wrapper.find('#name').exists()).toBe(true)
      expect(wrapper.find('#yearBuilt').exists()).toBe(true)
      expect(wrapper.find('#commissionedDate').exists()).toBe(true)
      expect(wrapper.find('#strickenDate').exists()).toBe(true)
      expect(wrapper.find('#country').exists()).toBe(true)
    })

    it('renders all available countries', () => {
      const options = wrapper.findAll('select option')
      // +1 for the "Select Country" option
      expect(options.length).toBe(17)
    })
  })

  describe('Form Interactions', () => {
    it('updates ship name', async () => {
      await wrapper.find('#name').setValue('USS Voyager')
      expect(wrapper.vm.updatedShip.name).toBe('USS Voyager')
    })

    it('updates year built', async () => {
      await wrapper.find('#yearBuilt').setValue(1970)
      expect(wrapper.vm.updatedShip.year_built).toBe(1970)
    })

    it('updates commissioned date', async () => {
      await wrapper.find('#commissionedDate').setValue(1971)
      expect(wrapper.vm.updatedShip.commissioned_date).toBe(1971)
    })

    it('updates stricken date', async () => {
      await wrapper.find('#strickenDate').setValue(2010)
      expect(wrapper.vm.updatedShip.stricken_date).toBe(2010)
    })

    it('updates country selection', async () => {
      await wrapper.find('#country').setValue('UK')
      expect(wrapper.vm.updatedShip.country_of_origin).toBe('UK')
    })
  })

  describe('Form Validation', () => {
    it('validates commissioned date is not earlier than year built', async () => {
      await wrapper.setData({
        updatedShip: {
          ...mockShip,
          year_built: 1960,
          commissioned_date: 1959
        }
      })

      await wrapper.find('form').trigger('submit')
      expect(mockShowAlert).toHaveBeenCalledWith(
        'Commissioned date cannot be earlier than year built',
        'warning'
      )
    })

    it('validates stricken date is not earlier than commissioned date', async () => {
      await wrapper.setData({
        updatedShip: {
          ...mockShip,
          commissioned_date: 1960,
          stricken_date: 1959
        }
      })

      await wrapper.find('form').trigger('submit')
      expect(mockShowAlert).toHaveBeenCalledWith(
        'Stricken date cannot be earlier than commissioned date or year built',
        'warning'
      )
    })

    it('validates stricken date is not earlier than year built when no commissioned date', async () => {
      await wrapper.setData({
        updatedShip: {
          ...mockShip,
          year_built: 1960,
          commissioned_date: null,
          stricken_date: 1959
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
    it('successfully updates ship', async () => {
      const updatedShipData = {
        ...mockShip,
        name: 'USS Voyager'
      }

      axios.put.mockResolvedValueOnce({ status: 200, data: updatedShipData })

      await wrapper.setData({ updatedShip: updatedShipData })
      await wrapper.find('form').trigger('submit')

      expect(axios.put).toHaveBeenCalledWith(
        `http://localhost:8000/ships/${mockShip.id}`,
        updatedShipData
      )
      expect(wrapper.emitted('ship-updated')).toBeTruthy()
      expect(wrapper.emitted('close')).toBeTruthy()
      expect(mockShowAlert).toHaveBeenCalledWith('Ship updated successfully', 'success')
    })

    it('handles API errors', async () => {
      const error = new Error('API Error')
      error.response = { data: { detail: 'Server error' } }
      axios.put.mockRejectedValueOnce(error)

      await wrapper.find('form').trigger('submit')
      expect(mockShowAlert).toHaveBeenCalledWith('Server error', 'error')
    })

    it('handles API errors without detail', async () => {
      axios.put.mockRejectedValueOnce(new Error('API Error'))

      await wrapper.find('form').trigger('submit')
      expect(mockShowAlert).toHaveBeenCalledWith('Error updating ship. Please try again.', 'error')
    })
  })

  describe('Modal Interactions', () => {
    it('emits close event when close button is clicked', async () => {
      await wrapper.find('.close-btn').trigger('click')
      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('closes modal when clicking overlay', async () => {
      await wrapper.find('.modal-overlay').trigger('click')
      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('does not close modal when clicking modal content', async () => {
      await wrapper.find('.modal-content').trigger('click')
      expect(wrapper.emitted('close')).toBeFalsy()
    })
  })

  describe('Watch Behavior', () => {
    it('updates form data when ship prop changes', async () => {
      const newShip = {
        ...mockShip,
        name: 'USS Defiant',
        year_built: 1980
      }

      await wrapper.setProps({ ship: newShip })
      expect(wrapper.vm.updatedShip.name).toBe('USS Defiant')
      expect(wrapper.vm.updatedShip.year_built).toBe(1980)
    })
  })
})
