<template>
  <div class="modal-overlay" v-if="show" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Search Ships</h2>
        <button class="close-btn" @click="closeModal" aria-label="Close modal">×</button>
      </div>
      <div class="modal-body">
        <div class="search-input">
          <input 
            v-model.trim="searchQuery" 
            placeholder="Enter ship name..."
            @keyup.enter="searchShips"
            aria-label="Search ships"
          />
          <button class="search-action-btn" @click="searchShips">
            <i class="fas fa-search"></i>
            Search
          </button>
          <button 
            v-if="hasSearchResults" 
            @click="clearSearch" 
            class="clear-button"
            aria-label="Clear search"
          >
            <i class="fas fa-times"></i> CLEAR
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import config from '../../config';

const API_URL = config.apiBaseUrl + '/ships';

export default {
  name: 'SearchComponent',
  props: {
    show: {
      type: Boolean,
      required: true
    }
  },
  inject: ['showAlert'],
  data() {
    return {
      searchQuery: '',
      hasSearchResults: false
    }
  },
  methods: {
    closeModal() {
      this.searchQuery = '';
      this.$emit('close');
    },
    
    async searchShips() {
      const query = this.searchQuery.trim();
      if (!query) {
        this.showAlert('Please enter a search term', 'warning');
        return;
      }

      try {
        const response = await axios.get(`${API_URL}/search/?query=${encodeURIComponent(query)}`);
        const ships = response.data;
        
        if (ships.length === 0) {
          this.showAlert('No ships found matching your search.', 'warning');
          return;
        }
        
        this.hasSearchResults = true;
        this.$emit('search-results', ships);
        this.showAlert('Search completed successfully', 'success');
      } catch (error) {
        console.error('Error searching ships:', error);
        const errorMessage = error.response?.data?.detail || 'An error occurred while searching';
        this.showAlert(errorMessage, 'error');
      }
    },
    
    clearSearch() {
      this.searchQuery = '';
      this.hasSearchResults = false;
      this.$emit('clear-search');
      this.showAlert('Search cleared', 'info');
    }
  }
}
</script>

<style scoped>
/* Modal Layout */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(13, 27, 42, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: rgba(15, 23, 42, 0.95);
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  border: 1px solid rgba(0, 247, 255, 0.2);
  box-shadow: 0 0 20px rgba(0, 247, 255, 0.1);
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(0, 247, 255, 0.2);
}

.modal-header h2 {
  color: white;
  margin: 0;
  font-family: 'Orbitron', sans-serif;
  text-transform: uppercase;
  letter-spacing: 2px;
}

/* Close Button */
.close-btn {
  background: none;
  border: none;
  color: #00f7ff;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(0, 247, 255, 0.1);
  transform: rotate(90deg);
}

/* Search Form */
.modal-body {
  padding: 20px;
}

.search-input {
  display: flex;
  gap: 10px;
}

.search-input input {
  flex: 1;
  padding: 12px;
  border: 1px solid rgba(0, 247, 255, 0.3);
  background: rgba(13, 27, 42, 0.7);
  border-radius: 6px;
  color: white;
  font-size: 1em;
}

.search-input input:focus {
  outline: none;
  border-color: rgba(0, 247, 255, 0.5);
  box-shadow: 0 0 10px rgba(0, 247, 255, 0.2);
}

/* Action Buttons */
.search-action-btn {
  padding: 12px 24px;
  background: linear-gradient(to bottom, rgba(13, 27, 42, 0.9), rgba(13, 27, 42, 0.7));
  border: 1px solid rgba(0, 247, 255, 0.3);
  color: #00f7ff;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s ease;
}

.search-action-btn:hover {
  background: linear-gradient(to bottom, rgba(0, 247, 255, 0.1), rgba(0, 247, 255, 0.05));
  border-color: rgba(0, 247, 255, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 0 15px rgba(0, 247, 255, 0.2);
}

.clear-button {
  padding: 12px 24px;
  background: rgba(13, 27, 42, 0.95);
  border: 1px solid rgba(255, 68, 68, 0.3);
  color: #ff4444;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s ease;
}

.clear-button:hover {
  background: rgba(13, 27, 42, 0.85);
  border-color: rgba(255, 68, 68, 0.5);
  box-shadow: 0 0 10px rgba(255, 68, 68, 0.2);
}

.clear-button i {
  font-size: 0.9em;
}
</style> 