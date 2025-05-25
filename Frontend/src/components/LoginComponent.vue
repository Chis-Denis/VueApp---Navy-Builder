<template>
  <div class="login-container">
    <div class="background-overlay"></div>
    <div class="login-card">
      <h1 class="login-title">BUILD YOUR OWN NAVY</h1>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input 
            id="username"
            v-model="username"
            type="text"
            required
            placeholder="Enter your username"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input 
            id="password"
            v-model="password"
            type="password"
            required
            placeholder="Enter your password"
          />
        </div>

        <div class="form-actions">
          <button type="submit" class="login-btn" :disabled="isLoading">
            <i class="fas fa-sign-in-alt"></i>
            {{ isLoading ? 'LOGGING IN...' : 'LOGIN' }}
          </button>
        </div>
      </form>

      <div class="register-link">
        <span>Don't have an account?</span>
        <button class="register-btn" @click="showRegister = true">Register</button>
      </div>

      <div v-if="error" class="error-message">
        <i class="fas fa-exclamation-circle"></i>
        {{ error }}
      </div>
    </div>

    <!-- Registration Modal -->
    <div v-if="showRegister" class="modal-overlay">
      <div class="modal-card">
        <h2 class="modal-title">Register</h2>
        <form @submit.prevent="handleRegister" class="register-form">
          <div class="form-group">
            <label for="reg-username">Username</label>
            <input id="reg-username" v-model="regUsername" type="text" required placeholder="Choose a username" />
          </div>
          <div class="form-group">
            <label for="reg-email">Email</label>
            <input id="reg-email" v-model="regEmail" type="email" required placeholder="Enter your email" />
          </div>
          <div class="form-group">
            <label for="reg-password">Password</label>
            <input id="reg-password" v-model="regPassword" type="password" required placeholder="Choose a password" />
          </div>
          <div class="form-group">
            <label for="reg-role">Role</label>
            <select id="reg-role" v-model="regRole" required>
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="submit" class="login-btn" :disabled="isRegistering">
              {{ isRegistering ? 'REGISTERING...' : 'REGISTER' }}
            </button>
            <button type="button" class="cancel-btn" @click="showRegister = false">Cancel</button>
          </div>
        </form>
        <div v-if="registerError" class="error-message">
          <i class="fas fa-exclamation-circle"></i>
          {{ registerError }}
        </div>
        <div v-if="registerSuccess" class="success-message">
          <i class="fas fa-check-circle"></i>
          {{ registerSuccess }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import config from '../config';

export default {
  name: 'LoginComponent',
  data() {
    return {
      username: '',
      password: '',
      error: null,
      isLoading: false,
      showRegister: false,
      regUsername: '',
      regEmail: '',
      regPassword: '',
      regRole: 'user',
      isRegistering: false,
      registerError: null,
      registerSuccess: null
    }
  },
  methods: {
    async handleLogin() {
      this.isLoading = true;
      this.error = null;

      try {
        const formData = new FormData();
        formData.append('username', this.username);
        formData.append('password', this.password);

        const response = await axios.post(`${config.apiBaseUrl}/auth/token`, formData);
        
        // Store the token
        localStorage.setItem('token', response.data.access_token);
        
        // Get user info
        const userResponse = await axios.get(`${config.apiBaseUrl}/auth/users/me`, {
          headers: {
            'Authorization': `Bearer ${response.data.access_token}`
          }
        });

        // Store user info
        localStorage.setItem('user', JSON.stringify(userResponse.data));
        console.log('Logged in user:', userResponse.data);
        if (this.$root && this.$root.checkAuth) {
          this.$root.checkAuth();
        }
        if (userResponse.data.role === 'admin') {
          this.$router.push('/admin');
        } else {
          this.$router.push('/');
        }
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to login. Please try again.';
      } finally {
        this.isLoading = false;
      }
    },
    async handleRegister() {
      this.isRegistering = true;
      this.registerError = null;
      this.registerSuccess = null;
      try {
        await axios.post(`${config.apiBaseUrl}/auth/register`, {
          username: this.regUsername,
          email: this.regEmail,
          password: this.regPassword,
          role: this.regRole
        });
        this.registerSuccess = 'Registration successful! You can now log in.';
        setTimeout(() => {
          this.showRegister = false;
          this.regUsername = '';
          this.regEmail = '';
          this.regPassword = '';
          this.regRole = 'user';
          this.registerSuccess = null;
        }, 1800);
      } catch (err) {
        this.registerError = err.response?.data?.detail || 'Failed to register. Please try again.';
      } finally {
        this.isRegistering = false;
      }
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Share+Tech+Mono&display=swap');

.login-container {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  background: #0d1b2a;
}

.background-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 0;
  background: url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1500&q=80') center center/cover no-repeat;
  filter: brightness(0.35) blur(1.5px);
}

.login-card {
  position: relative;
  z-index: 1;
  background: rgba(18, 32, 47, 0.98);
  border-radius: 18px;
  padding: 48px 38px 38px 38px;
  width: 100%;
  max-width: 410px;
  border: 2px solid rgba(0, 247, 255, 0.22);
  box-shadow: 0 0 40px 8px rgba(0, 247, 255, 0.13), 0 0 0 2px #00f7ff44;
  backdrop-filter: blur(10px);
  animation: cardGlow 2.5s infinite alternate;
}

@keyframes cardGlow {
  from {
    box-shadow: 0 0 40px 8px rgba(0, 247, 255, 0.13), 0 0 0 2px #00f7ff44;
  }
  to {
    box-shadow: 0 0 60px 16px rgba(0, 247, 255, 0.22), 0 0 0 3px #00f7ff77;
  }
}

.login-title {
  color: #fff;
  text-align: center;
  font-size: 2.2em;
  text-transform: uppercase;
  letter-spacing: 2.5px;
  margin-bottom: 38px;
  font-family: 'Orbitron', 'Share Tech Mono', monospace;
  font-weight: 700;
  text-shadow: 0 0 24px #00f7ff99, 0 0 8px #fff;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #00f7ff;
  font-family: 'Orbitron', 'Share Tech Mono', monospace;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  font-size: 1em;
  text-shadow: 0 0 6px #00f7ff44;
}

.form-group input {
  padding: 13px 14px;
  border: 1.5px solid rgba(0, 247, 255, 0.35);
  background: rgba(13, 27, 42, 0.85);
  border-radius: 7px;
  color: #fff;
  font-size: 1.08em;
  font-family: 'Share Tech Mono', monospace;
  transition: all 0.3s cubic-bezier(.4,2,.6,1);
  box-shadow: 0 0 0 rgba(0,247,255,0);
}

.form-group input:focus {
  outline: none;
  border-color: #00f7ff;
  box-shadow: 0 0 12px 2px #00f7ff55;
  background: rgba(13, 27, 42, 0.95);
}

.form-actions {
  margin-top: 10px;
}

.login-btn {
  width: 100%;
  padding: 13px;
  font-size: 1.08em;
  background: linear-gradient(90deg, #00f7ff 0%, #1e90ff 100%);
  border: none;
  color: #0d1b2a;
  border-radius: 7px;
  cursor: pointer;
  transition: all 0.22s cubic-bezier(.4,2,.6,1);
  text-transform: uppercase;
  letter-spacing: 1.2px;
  font-weight: bold;
  font-family: 'Orbitron', 'Share Tech Mono', monospace;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 0 0 rgba(0,247,255,0);
  text-shadow: 0 0 8px #fff, 0 0 2px #00f7ff;
}

.login-btn:hover:not(:disabled) {
  background: linear-gradient(90deg, #1e90ff 0%, #00f7ff 100%);
  color: #fff;
  box-shadow: 0 0 18px 2px #00f7ff77;
  transform: translateY(-2px) scale(1.03);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  margin-top: 22px;
  padding: 13px;
  background: rgba(255, 68, 68, 0.13);
  border: 1.5px solid rgba(255, 68, 68, 0.33);
  border-radius: 7px;
  color: #ff4444;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1em;
  font-family: 'Share Tech Mono', monospace;
  box-shadow: 0 0 8px 1px #ff444455;
}

.error-message i {
  font-size: 1.2em;
}

.register-link {
  margin-top: 18px;
  text-align: center;
  color: #7ffcff;
  font-size: 1em;
  font-family: 'Share Tech Mono', monospace;
}
.register-btn {
  background: none;
  border: none;
  color: #00f7ff;
  font-weight: bold;
  margin-left: 8px;
  cursor: pointer;
  text-decoration: underline;
  font-family: 'Orbitron', 'Share Tech Mono', monospace;
  transition: color 0.2s;
}
.register-btn:hover {
  color: #1e90ff;
}

/* Registration Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(13, 27, 42, 0.85);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-card {
  background: rgba(18, 32, 47, 0.98);
  border-radius: 18px;
  padding: 38px 32px 28px 32px;
  min-width: 340px;
  max-width: 95vw;
  border: 2px solid rgba(0, 247, 255, 0.22);
  box-shadow: 0 0 40px 8px rgba(0, 247, 255, 0.13), 0 0 0 2px #00f7ff44;
  animation: cardGlow 2.5s infinite alternate;
  position: relative;
}
.modal-title {
  color: #00f7ff;
  text-align: center;
  font-size: 1.5em;
  font-family: 'Orbitron', 'Share Tech Mono', monospace;
  margin-bottom: 22px;
  text-shadow: 0 0 12px #00f7ff77;
}
.register-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.cancel-btn {
  margin-left: 12px;
  background: none;
  border: 1.5px solid #ff4444;
  color: #ff4444;
  border-radius: 7px;
  padding: 10px 18px;
  font-family: 'Orbitron', 'Share Tech Mono', monospace;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.cancel-btn:hover {
  background: #ff4444;
  color: #fff;
}
.success-message {
  margin-top: 18px;
  padding: 12px;
  background: rgba(0, 247, 127, 0.13);
  border: 1.5px solid rgba(0, 247, 127, 0.33);
  border-radius: 7px;
  color: #00f77f;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1em;
  font-family: 'Share Tech Mono', monospace;
  box-shadow: 0 0 8px 1px #00f77f55;
}
.success-message i {
  font-size: 1.2em;
}
</style> 