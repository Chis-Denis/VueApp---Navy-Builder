<template>
  <div class="modal-overlay" v-if="show" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Filter Ships</h2>
        <button class="close-btn" @click="closeModal" aria-label="Close modal">×</button>
      </div>
      <div class="modal-body">
        <!-- Year Built Range -->
        <div class="filter-group">
          <label for="yearFrom">Year Built Range</label>
          <div class="range-inputs">
            <input 
              id="yearFrom"
              v-model.number="filters.yearFrom" 
              type="number" 
              placeholder="From year"
            />
            <span>to</span>
            <input 
              id="yearTo"
              v-model.number="filters.yearTo" 
              type="number" 
              placeholder="To year"
            />
          </div>
        </div>
        
        <!-- Commissioned Date Range -->
        <div class="filter-group">
          <label for="commissionedFrom">Commissioned Date Range</label>
          <div class="range-inputs">
            <input 
              id="commissionedFrom"
              v-model.number="filters.commissionedFrom" 
              type="number" 
              placeholder="From year"
            />
            <span>to</span>
            <input 
              id="commissionedTo"
              v-model.number="filters.commissionedTo" 
              type="number" 
              placeholder="To year"
            />
          </div>
        </div>
        
        <!-- Country Selection -->
        <div class="filter-group">
          <label for="country">Country of Origin</label>
          <select id="country" v-model="filters.country">
            <option value="">All Countries</option>
            <option v-for="country in countries" :key="country.value" :value="country.value">
              {{ country.label }}
            </option>
          </select>
        </div>

        <!-- Action Buttons -->
        <div class="filter-actions">
          <button class="filter-action-btn clear" @click="clearFilters" aria-label="Clear filters">
            <i class="fas fa-times"></i>
            Clear
          </button>
          <button class="filter-action-btn apply" @click="applyFilters" aria-label="Apply filters">
            <i class="fas fa-check"></i>
            Apply
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
const COUNTRIES = [
  { value: 'USA', label: 'United States' },
  { value: 'UK', label: 'United Kingdom' },
  { value: 'Germany', label: 'Germany' },
  { value: 'Japan', label: 'Japan' },
  { value: 'France', label: 'France' },
  { value: 'Italy', label: 'Italy' },
  { value: 'Spain', label: 'Spain' },
  { value: 'Australia', label: 'Australia' },
  { value: 'Canada', label: 'Canada' },
  { value: 'New Zealand', label: 'New Zealand' },
  { value: 'Russia', label: 'Russia' },
  { value: 'China', label: 'China' },
  { value: 'Brazil', label: 'Brazil' },
  { value: 'India', label: 'India' },
  { value: 'South Korea', label: 'South Korea' },
  { value: 'South Africa', label: 'South Africa' }
  
];

export default {
  name: 'FilterComponent',
  inject: ['showAlert'],
  props: {
    show: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      filters: {
        yearFrom: null,
        yearTo: null,
        commissionedFrom: null,
        commissionedTo: null,
        country: ''
      },
      countries: COUNTRIES
    }
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },

    clearFilters() {
      this.filters = {
        yearFrom: null,
        yearTo: null,
        commissionedFrom: null,
        commissionedTo: null,
        country: ''
      };
      this.$emit('clear-filter');
      this.closeModal();
      this.showAlert('Filters cleared', 'info');
    },

    async applyFilters() {
      try {
        const params = new URLSearchParams();
        
        if (this.filters.yearFrom && this.filters.yearTo) {
          if (this.filters.yearTo < this.filters.yearFrom) {
            this.showAlert('End year cannot be less than start year', 'warning');
            return;
          }
        }
        
        if (this.filters.yearFrom) {
          params.append('year_from', this.filters.yearFrom);
        }
        
        if (this.filters.yearTo) {
          params.append('year_to', this.filters.yearTo);
        }
        
        if (this.filters.commissionedFrom && this.filters.commissionedTo) {
          if (this.filters.commissionedTo < this.filters.commissionedFrom) {
            this.showAlert('End commissioned date cannot be less than start commissioned date', 'warning');
            return;
          }
        }

        if (this.filters.commissionedFrom) {
          params.append('commissioned_from', this.filters.commissionedFrom);
        }

        if (this.filters.commissionedTo) {
          params.append('commissioned_to', this.filters.commissionedTo);
        }
        
        if (this.filters.country) {
          params.append('country', this.filters.country);
        }

        console.log('Filter params:', Object.fromEntries(params));
        const response = await axios.get(`${API_URL}/filter/?${params.toString()}`);
        console.log('Filter response:', response.data);

        if (response.data.length === 0) {
          this.showAlert('No ships found matching these filters.', 'warning');
          return;
        }

        this.$emit('filter-results', response.data);
        this.closeModal();
        this.showAlert('Filters applied successfully', 'success');
      } catch (error) {
        console.error('Error filtering ships:', error);
        console.error('Error details:', error.response?.data);
        const errorMessage = error.response?.data?.detail || 'Error filtering ships. Please try again.';
        this.showAlert(errorMessage, 'error');
      }
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

/* Filter Form */
.modal-body {
  padding: 20px;
}

.filter-group {
  margin-bottom: 20px;
}

.filter-group label {
  display: block;
  color: #00f7ff;
  margin-bottom: 8px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.9em;
}

.range-inputs {
  display: flex;
  gap: 10px;
  align-items: center;
}

.range-inputs span {
  color: #00f7ff;
}

/* Form Controls */
input, select {
  padding: 12px;
  border: 1px solid rgba(0, 247, 255, 0.3);
  background: rgba(13, 27, 42, 0.7);
  border-radius: 6px;
  color: white;
  font-size: 1em;
  width: 100%;
}

input:focus, select:focus {
  outline: none;
  border-color: rgba(0, 247, 255, 0.5);
  box-shadow: 0 0 10px rgba(0, 247, 255, 0.2);
}

/* Action Buttons */
.filter-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.filter-action-btn {
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

.filter-action-btn:hover {
  background: linear-gradient(to bottom, rgba(0, 247, 255, 0.1), rgba(0, 247, 255, 0.05));
  border-color: rgba(0, 247, 255, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 0 15px rgba(0, 247, 255, 0.2);
}

.filter-action-btn.clear {
  background: rgba(13, 27, 42, 0.95);
  border: 1px solid rgba(255, 68, 68, 0.3);
  color: #ff4444;
}

.filter-action-btn.clear:hover {
  border-color: rgba(255, 68, 68, 0.5);
  box-shadow: 0 0 10px rgba(255, 68, 68, 0.2);
}
</style> 