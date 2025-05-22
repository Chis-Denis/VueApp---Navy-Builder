import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import AlertComponent from '@/components/AlertComponent.vue'
import { Transition } from 'vue'

describe('AlertComponent.vue', () => {
  const createWrapper = (props = {}) => {
    return mount(AlertComponent, {
      props: {
        message: 'Test message',
        type: 'info',
        isConfirm: false,
        ...props
      },
      global: {
        stubs: {
          Transition: false
        }
      }
    })
  }

  describe('Rendering', () => {
    it('renders when message is provided', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.alert').exists()).toBe(true)
      expect(wrapper.find('.alert-content span').text()).toBe('Test message')
    })

    it('does not render when message is empty', () => {
      const wrapper = createWrapper({ message: '' })
      expect(wrapper.find('.alert').exists()).toBe(false)
    })

    it('applies correct CSS class based on type', () => {
      const types = ['success', 'error', 'info', 'warning']
      types.forEach(type => {
        const wrapper = createWrapper({ type })
        expect(wrapper.find(`.alert.${type}`).exists()).toBe(true)
      })
    })

    it('displays correct icon based on type', () => {
      const typeToIcon = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle'
      }

      Object.entries(typeToIcon).forEach(([type, iconClass]) => {
        const wrapper = createWrapper({ type })
        expect(wrapper.find(`.alert i.fas.${iconClass}`).exists()).toBe(true)
      })
    })
  })

  describe('Regular Alert', () => {
    it('shows close button for regular alerts', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.close-btn').exists()).toBe(true)
      expect(wrapper.find('.confirm-btn').exists()).toBe(false)
    })

    it('emits close event when close button is clicked', async () => {
      const wrapper = createWrapper()
      await wrapper.find('.close-btn').trigger('click')
      expect(wrapper.emitted('close')).toBeTruthy()
    })
  })

  describe('Confirmation Alert', () => {
    it('shows confirmation buttons when isConfirm is true', () => {
      const wrapper = createWrapper({ isConfirm: true })
      expect(wrapper.find('.alert-actions').exists()).toBe(true)
      expect(wrapper.findAll('.confirm-btn').length).toBe(2)
    })

    it('emits confirm true and closes when Yes is clicked', async () => {
      const wrapper = createWrapper({ isConfirm: true })
      await wrapper.find('.confirm-btn.confirm').trigger('click')
      
      expect(wrapper.emitted('confirm')).toBeTruthy()
      expect(wrapper.emitted('confirm')[0][0]).toBe(true)
      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('emits confirm false and closes when No is clicked', async () => {
      const wrapper = createWrapper({ isConfirm: true })
      await wrapper.find('.confirm-btn.cancel').trigger('click')
      
      expect(wrapper.emitted('confirm')).toBeTruthy()
      expect(wrapper.emitted('confirm')[0][0]).toBe(false)
      expect(wrapper.emitted('close')).toBeTruthy()
    })
  })

  describe('Props Validation', () => {
    it('validates alert type', () => {
      const validator = AlertComponent.props.type.validator

      // Valid types
      expect(validator('success')).toBe(true)
      expect(validator('error')).toBe(true)
      expect(validator('info')).toBe(true)
      expect(validator('warning')).toBe(true)

      // Invalid type
      expect(validator('invalid-type')).toBe(false)
    })

    it('uses default values when props are not provided', () => {
      const wrapper = mount(AlertComponent, {
        props: {
          message: 'Test'
        }
      })

      expect(wrapper.props('type')).toBe('info')
      expect(wrapper.props('isConfirm')).toBe(false)
    })
  })

  describe('Styling and Animations', () => {
    it('applies correct styling based on type', () => {
      const wrapper = createWrapper({ type: 'success' })
      const alert = wrapper.find('.alert.success')
      
      expect(alert.exists()).toBe(true)
      expect(alert.find('i').classes()).toContain('fa-check-circle')
    })

    it('applies correct styling for confirmation buttons', () => {
      const wrapper = createWrapper({ isConfirm: true })
      
      const confirmBtn = wrapper.find('.confirm-btn.confirm')
      const cancelBtn = wrapper.find('.confirm-btn.cancel')
      
      expect(confirmBtn.exists()).toBe(true)
      expect(cancelBtn.exists()).toBe(true)
      expect(confirmBtn.find('i.fa-check').exists()).toBe(true)
      expect(cancelBtn.find('i.fa-times').exists()).toBe(true)
    })
  })
})
