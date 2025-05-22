<template>
  <!-- Alert Animation Wrapper -->
  <transition name="alert-fade">
    <div v-if="message" class="alert-container">
      <div class="alert" :class="type">
        <div class="alert-content">
          <i :class="iconClass"></i>
          <span>{{ message }}</span>
        </div>
        <div class="alert-actions" v-if="isConfirm">
          <button class="confirm-btn confirm" @click="handleConfirm(true)" aria-label="Confirm action">
            <i class="fas fa-check"></i> Yes
          </button>
          <button class="confirm-btn cancel" @click="handleConfirm(false)" aria-label="Cancel action">
            <i class="fas fa-times"></i> No
          </button>
        </div>
        <button v-else class="close-btn" @click="close" aria-label="Close alert">×</button>
      </div>
    </div>
  </transition>
</template>

<script>
// Define valid alert types
const ALERT_TYPES = ['success', 'error', 'info', 'warning'];

// Map alert types to their corresponding icons
const ALERT_ICONS = {
  success: 'fas fa-check-circle',
  error: 'fas fa-exclamation-circle',
  info: 'fas fa-info-circle',
  warning: 'fas fa-exclamation-triangle'
};

export default {
  name: 'AlertComponent',
  
  props: {
    // Alert message content
    message: {
      type: String,
      default: '',
      required: true
    },
    // Alert type (success, error, info, warning)
    type: {
      type: String,
      default: 'info',
      validator: value => ALERT_TYPES.includes(value)
    },
    // Whether this is a confirmation alert
    isConfirm: {
      type: Boolean,
      default: false
    }
  },

  computed: {
    // Get the appropriate icon class based on alert type
    iconClass() {
      return ALERT_ICONS[this.type];
    }
  },

  methods: {
    // Close the alert
    close() {
      this.$emit('close');
    },
    
    // Handle confirmation response
    handleConfirm(confirmed) {
      this.$emit('confirm', confirmed);
      this.close();
    }
  }
}
</script>

<style scoped>
/* Alert Container */
.alert-container {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  min-width: 300px;
  max-width: 600px;
  width: auto;
}

/* Alert Box */
.alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  border-radius: 8px;
  background: rgba(13, 27, 42, 0.95);
  box-shadow: 0 0 20px rgba(0, 247, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 247, 255, 0.3);
}

/* Alert Content */
.alert-content {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #00f7ff;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 1px;
}

.alert i {
  font-size: 1.2em;
}

/* Alert Type Variations */
.alert.success {
  border-color: rgba(72, 187, 120, 0.5);
}

.alert.success i,
.alert.success .alert-content {
  color: #48bb78;
}

.alert.error {
  border-color: rgba(255, 68, 68, 0.5);
}

.alert.error i,
.alert.error .alert-content {
  color: #ff4444;
}

.alert.warning {
  border-color: rgba(247, 174, 0, 0.5);
}

.alert.warning i,
.alert.warning .alert-content {
  color: #f7ae00;
}

.alert.info {
  border-color: rgba(0, 247, 255, 0.5);
}

.alert.info i,
.alert.info .alert-content {
  color: #00f7ff;
}

/* Close Button */
.close-btn {
  background: none;
  border: none;
  color: inherit;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  margin-left: 15px;
  opacity: 0.7;
  transition: all 0.3s ease;
}

.close-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}

/* Alert Animation */
.alert-fade-enter-active,
.alert-fade-leave-active {
  transition: all 0.3s ease;
}

.alert-fade-enter-from,
.alert-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -20px);
}

/* Confirmation Buttons */
.alert-actions {
  display: flex;
  gap: 10px;
  margin-left: 15px;
}

.confirm-btn {
  padding: 5px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.9em;
  text-transform: uppercase;
  transition: all 0.3s ease;
  background: none;
  border: 1px solid;
  display: flex;
  align-items: center;
  gap: 6px;
}

.confirm-btn.confirm {
  color: #48bb78;
  border-color: rgba(72, 187, 120, 0.5);
}

.confirm-btn.confirm:hover {
  background: rgba(72, 187, 120, 0.1);
}

.confirm-btn.cancel {
  color: #ff4444;
  border-color: rgba(255, 68, 68, 0.5);
}

.confirm-btn.cancel:hover {
  background: rgba(255, 68, 68, 0.1);
}
</style> 