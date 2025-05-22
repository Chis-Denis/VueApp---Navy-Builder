<template>
  <div class="network-status" :class="statusClass">
    <div class="status-indicator"></div>
    <span class="status-text">{{ statusText }}</span>
  </div>
</template>

<script>
import NetworkService from '../../services/NetworkService';

export default {
  name: 'NetworkStatus',
  data() {
    return {
      isOnline: NetworkService.isOnline,
      isServerAvailable: NetworkService.isServerAvailable
    };
  },
  computed: {
    statusClass() {
      if (!this.isOnline) return 'offline';
      if (!this.isServerAvailable) return 'server-offline';
      return 'online';
    },
    statusText() {
      if (!this.isOnline) return 'Offline - Changes will be saved locally';
      if (!this.isServerAvailable) return 'Server Unavailable - Changes will be saved locally';
      return 'Online';
    }
  },
  created() {
    // Update status when network or server status changes
    const updateStatus = () => {
      this.isOnline = NetworkService.isOnline;
      this.isServerAvailable = NetworkService.isServerAvailable;
    };
    
    window.addEventListener('online', updateStatus);
    window.addEventListener('offline', updateStatus);
    
    // Check server status periodically
    this.interval = setInterval(updateStatus, 30000);
  },
  beforeUnmount() {
    window.removeEventListener('online', this.updateStatus);
    window.removeEventListener('offline', this.updateStatus);
    clearInterval(this.interval);
  }
};
</script>

<style scoped>
.network-status {
  position: fixed;
  bottom: 20px;
  left: 20px;
  right: auto;
  top: auto;
  padding: 8px 16px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  z-index: 1000;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.online {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.online .status-indicator {
  background-color: #4caf50;
}

.offline {
  background-color: #ffebee;
  color: #c62828;
}

.offline .status-indicator {
  background-color: #f44336;
}

.server-offline {
  background-color: #fff3e0;
  color: #ef6c00;
}

.server-offline .status-indicator {
  background-color: #ff9800;
}
</style> 