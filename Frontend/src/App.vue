<template>
  <div id="app">
    <!-- Navigation Bar -->
    <nav class="nav-bar" v-if="isAuthenticated">
      <div class="nav-center-group">
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/statistics" class="nav-link" v-if="isAdmin">Statistics</router-link>
        <router-link to="/files" class="nav-link">Files</router-link>
      </div>
      <div class="nav-right-group">
        <button v-if="isAdmin" @click="goToAdmin" class="nav-link admin-link">
          Admin Panel
        </button>
        <button @click="handleLogout" class="nav-link logout-link">
          <i class="fas fa-sign-out-alt"></i>
          Logout
        </button>
      </div>
    </nav>

    <div class="content-container">
    <!-- Global Alert System - Handles all application notifications -->
    <AlertComponent 
      :message="alert.message"
      :type="alert.type"
      @close="clearAlert"
      v-if="alert.message"
    />
    
    <!-- Application Title -->
    <h1 class="main-title" v-if="isAuthenticated">BUILD YOUR OWN NAVY</h1>
    
    <!-- Main Application Content -->
      <router-view />

    <NetworkStatus v-if="isAuthenticated" />
    </div>
  </div>
</template>

<script>
// Component Imports
import AlertComponent from './components/files/AlertComponent.vue'
import NetworkStatus from './components/files/NetworkStatus.vue'
import { ref, onMounted } from 'vue'

// Alert Configuration
const ALERT_DURATION = 3000; // Duration in milliseconds for auto-dismissing alerts

export default {
  name: 'App',
  
  components: {
    AlertComponent,
    NetworkStatus
  },

  setup() {
    const ships = ref([])
    const loading = ref(true)
    const error = ref(null)

    const fetchShips = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/ships', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (!response.ok) {
          throw new Error('Failed to fetch ships')
        }
        ships.value = await response.json()
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchShips()
    })

    return {
      ships,
      loading,
      error
    }
  },

  data() {
    return {
      // Alert state management
      alert: {
        message: '',           // Alert message content
        type: 'info',         // Alert type: 'info', 'success', 'warning', 'error'
        timeout: null         // Timer for auto-dismissing alerts
      },
      isAuthenticated: false,
      isAdmin: false
    }
  },

  created() {
    // Check authentication status
    this.checkAuth();
  },

  methods: {
    checkAuth() {
      const token = localStorage.getItem('token');
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      this.isAuthenticated = !!token;
      this.isAdmin = user.role === 'admin';
    },
    handleLogout() {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      this.isAuthenticated = false;
      this.isAdmin = false;
      this.$router.push('/login');
      this.showAlert('Successfully logged out', 'success');
    },
    goToAdmin() {
      this.$router.push('/admin');
    },
    /**
     * Shows an alert message with specified type
     * @param {string} message - The message to display
     * @param {string} type - The type of alert ('info', 'success', 'warning', 'error')
     */
    showAlert(message, type = 'info') {
      // Clear any existing timeout
      this.clearTimeout();
      
      // Set new alert
      this.alert.message = message;
      this.alert.type = type;
      
      // Auto-dismiss after specified duration
      this.alert.timeout = setTimeout(() => {
        this.clearAlert();
      }, ALERT_DURATION);
    },

    /**
     * Clears the current alert and its timeout
     */
    clearAlert() {
      this.alert.message = '';
      this.clearTimeout();
    },

    /**
     * Helper method to clear alert timeout
     */
    clearTimeout() {
      if (this.alert.timeout) {
        clearTimeout(this.alert.timeout);
        this.alert.timeout = null;
      }
    }
  },

  // Provide alert functionality to child components
  provide() {
    return {
      showAlert: this.showAlert
    }
  }
}
</script>

<style>
/* Font Import */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&display=swap');

/* Root Container */
#app {
  font-family: 'Orbitron', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #00f7ff;
  min-height: 100vh;
}

/* Navigation Bar */
.nav-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0;
  position: relative;
}
.nav-center-group {
  display: flex;
  justify-content: center;
  flex: 1;
  gap: 38px;
}
.nav-right-group {
  display: flex;
  align-items: center;
  gap: 18px;
  position: absolute;
  right: 32px;
  top: 0;
  height: 100%;
}
@media (max-width: 700px) {
  .nav-right-group {
    right: 8px;
  }
  .nav-center-group {
    gap: 16px;
  }
}

.nav-link {
  color: #7ffcff;
  text-decoration: none;
  padding: 4px 14px;
  border-radius: 16px;
  transition: all 0.22s cubic-bezier(.4,2,.6,1);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  font-size: 0.98em;
  box-shadow: 0 0 0 rgba(0,247,255,0);
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
}

.nav-link:hover, .nav-link.router-link-active {
  background: rgba(0, 247, 255, 0.10);
  color: #fff;
  box-shadow: 0 0 8px 0.5px rgba(0,247,255,0.13), 0 1px 4px rgba(0,247,255,0.07);
  text-shadow: 0 0 4px #00f7ff77;
}

.nav-link.router-link-active {
  background: rgba(0, 247, 255, 0.16);
  color: #fff;
  box-shadow: 0 0 10px 1.5px rgba(0,247,255,0.16), 0 1px 6px rgba(0,247,255,0.09);
  text-shadow: 0 0 7px #00f7ffbb;
}

.admin-link {
  color: #ff4444;
}

.admin-link:hover {
  background: rgba(255, 68, 68, 0.1);
  color: #ff4444;
}

.logout-link {
  color: #ff4444;
  display: flex;
  align-items: center;
  gap: 6px;
}

.logout-link:hover {
  background: rgba(255, 68, 68, 0.1);
  color: #ff4444;
}

/* Main Title */
.main-title {
  color: white;
  text-align: center;
  font-size: 3em;
  text-transform: uppercase;
  letter-spacing: 3px;
  margin: 30px 0;
  font-weight: 70;
  text-shadow: 0 0 20px rgba(0, 247, 255, 0.3);
  animation: glow 2s ease-in-out infinite alternate;
}

/* Global Typography */
h1, h2, h3 {
  font-family: 'Orbitron', sans-serif;
  margin: 0;
  padding: 0;
}

/* Global Interactive Elements */
button {
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Orbitron', sans-serif;
}

button:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 247, 255, 0.3);
}

input, select {
  font-family: 'Orbitron', sans-serif;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid rgba(0, 247, 255, 0.3);
  background: rgba(13, 27, 42, 0.7);
  color: white;
  transition: all 0.3s ease;
}

input:focus, select:focus {
  outline: none;
  border-color: rgba(0, 247, 255, 0.5);
  box-shadow: 0 0 10px rgba(0, 247, 255, 0.2);
}

/* Title Glow Animation */
@keyframes glow {
  from {
    text-shadow: 0 0 10px rgba(0, 247, 255, 0.3);
  }
  to {
    text-shadow: 0 0 20px rgba(0, 247, 255, 0.5),
                 0 0 30px rgba(0, 247, 255, 0.3);
  }
}

.content-container {
  margin-top: 20px;
}
</style>
