<template>
  <div class="admin-container">
    <h1 class="admin-title">Admin Dashboard</h1>
    
    <div class="admin-content">
      <div class="admin-card">
        <h2>User Management</h2>
        <div class="user-list-header">
          <div>Username</div>
          <div>Email</div>
          <div>Role</div>
          <div>Actions</div>
        </div>
        <div class="user-list" v-if="users.length">
          <template v-for="user in users" :key="user.id">
            <div class="username">{{ user.username }}</div>
            <div class="email">{{ user.email }}</div>
            <div class="role" :class="user.role">{{ user.role }}</div>
            <div class="user-actions">
              <button 
                class="action-btn"
                :class="{ 'monitored': user.is_monitored }"
                @click="toggleMonitoring(user)"
              >
                {{ user.is_monitored ? 'Unmonitor' : 'Monitor' }}
              </button>
            </div>
          </template>
        </div>
        <div v-else class="no-users">
          No users found
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import config from '../config';

export default {
  name: 'AdminComponent',
  data() {
    return {
      users: []
    }
  },
  async mounted() {
    await this.fetchUsers();
  },
  methods: {
    async fetchUsers() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${config.apiBaseUrl}/auth/admin/users`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        this.users = response.data;
      } catch (error) {
        console.error('Failed to fetch users:', error);
      }
    },
    async toggleMonitoring(user) {
      try {
        const token = localStorage.getItem('token');
        await axios.post(`${config.apiBaseUrl}/auth/admin/users/${user.id}/toggle-monitoring`, {}, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        user.is_monitored = !user.is_monitored;
      } catch (error) {
        console.error('Failed to toggle monitoring:', error);
      }
    }
  }
}
</script>

<style scoped>
.admin-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.admin-title {
  color: white;
  text-align: center;
  font-size: 2.5em;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 40px;
  font-weight: 700;
  text-shadow: 0 0 20px rgba(0, 247, 255, 0.3);
}

.admin-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.admin-card {
  background: rgba(15, 23, 42, 0.95);
  border-radius: 12px;
  padding: 30px;
  border: 1px solid rgba(0, 247, 255, 0.2);
  box-shadow: 0 0 30px rgba(0, 247, 255, 0.1);
}

.admin-card h2 {
  color: #00f7ff;
  margin-bottom: 20px;
  font-size: 1.5em;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.user-list {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr 1fr;
  gap: 0;
}

.user-item {
  display: contents;
}

.user-info {
  display: contents;
}

.username, .email, .role {
  display: flex;
  align-items: center;
  padding: 15px;
  background: rgba(13, 27, 42, 0.7);
  border-bottom: 1px solid rgba(0, 247, 255, 0.08);
  font-size: 1.1em;
  min-width: 0;
  word-break: break-all;
}

.role {
  justify-content: center;
}

.user-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 15px;
  background: rgba(13, 27, 42, 0.7);
  border-bottom: 1px solid rgba(0, 247, 255, 0.08);
}

/* Header row for alignment */
.admin-card h2 {
  margin-bottom: 0;
}
.admin-card .user-list-header {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr 1fr;
  font-weight: bold;
  color: #00f7ff;
  background: rgba(13, 27, 42, 0.9);
  padding: 10px 0;
  border-bottom: 2px solid #00f7ff44;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 1em;
}

.action-btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: 1px solid rgba(0, 247, 255, 0.3);
  background: transparent;
  color: #00f7ff;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  font-size: 0.9em;
  letter-spacing: 1px;
}

.action-btn:hover {
  background: rgba(0, 247, 255, 0.1);
  border-color: rgba(0, 247, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(0, 247, 255, 0.2);
}

.action-btn.monitored {
  background: rgba(255, 68, 68, 0.1);
  border-color: rgba(255, 68, 68, 0.3);
  color: #ff4444;
}

.action-btn.monitored:hover {
  background: rgba(255, 68, 68, 0.2);
  border-color: rgba(255, 68, 68, 0.5);
  box-shadow: 0 0 15px rgba(255, 68, 68, 0.2);
}

.no-users {
  text-align: center;
  color: #7ffcff;
  padding: 20px;
  font-style: italic;
}
</style> 