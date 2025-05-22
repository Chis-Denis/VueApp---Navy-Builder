<template>
  <div class="modal-overlay" v-if="show" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Add New Ship</h2>
        <button class="close-btn" @click="closeModal" aria-label="Close modal">×</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="addShip" class="add-ship-form">
          <!-- Ship Name -->
          <div class="form-group">
            <label for="shipName">Ship Name *</label>
            <input 
              id="shipName"
              v-model.trim="newShip.name" 
              placeholder="Enter ship name"
              required
              minlength="2"
              maxlength="100"
            />
          </div>

          <!-- Year Built -->
          <div class="form-group">
            <label for="yearBuilt">Year Built *</label>
            <input 
              id="yearBuilt"
              v-model.number="newShip.year_built" 
              type="number"
              placeholder="Enter year built"
              required
            />
          </div>

          <!-- Commissioned Date -->
          <div class="form-group">
            <label for="commissionedDate">Commissioned Date</label>
            <input 
              id="commissionedDate"
              v-model.number="newShip.commissioned_date" 
              type="number"
              placeholder="Enter commissioned year"
            />
          </div>

          <!-- Stricken Date -->
          <div class="form-group">
            <label for="strickenDate">Stricken Date</label>
            <input 
              id="strickenDate"
              v-model.number="newShip.stricken_date" 
              type="number"
              placeholder="Enter stricken year"
            />
          </div>

          <!-- Country Selection -->
          <div class="form-group">
            <label for="country">Country of Origin *</label>
            <select 
              id="country"
              v-model="newShip.country_of_origin"
              required
            >
              <option value="">Select country</option>
              <option v-for="country in countries" :key="country.value" :value="country.value">
                {{ country.label }}
              </option>
            </select>
          </div>

          <!-- Form Actions -->
          <div class="form-actions">
            <button 
              type="button" 
              class="form-action-btn clear" 
              @click="clearForm"
              aria-label="Clear form"
            >
              <i class="fas fa-times"></i>
              Clear
            </button>
            <button 
              type="submit" 
              class="form-action-btn submit"
              aria-label="Add ship"
            >
              <i class="fas fa-plus"></i>
              Add Ship
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

const API_URL = 'http://localhost:8000/ships';
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
  name: 'AddComponent',
  inject: ['showAlert'],
  props: {
    show: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      newShip: {
        name: '',
        year_built: null,
        commissioned_date: null,
        stricken_date: null,
        country_of_origin: ''
      },
      countries: COUNTRIES
    }
  },
  methods: {
    closeModal() {
      this.clearForm();
      this.$emit('close');
    },

    clearForm() {
      this.newShip = {
        name: '',
        year_built: null,
        commissioned_date: null,
        stricken_date: null,
        country_of_origin: ''
      };
    },

    async addShip() {
      // Validate required fields
      if (!this.newShip.name?.trim() || !this.newShip.year_built) {
        this.showAlert('Please fill in all required fields (Name and Year Built).', 'warning');
        return;
      }

      // Validate name length
      if (this.newShip.name.length < 2 || this.newShip.name.length > 100) {
        this.showAlert('Ship name must be between 2 and 100 characters', 'warning');
        return;
      }

      // Validate years logic
      const { year_built, commissioned_date, stricken_date } = this.newShip;
      
      if (commissioned_date && year_built) {
        if (commissioned_date < year_built) {
          this.showAlert('Commissioned date cannot be earlier than year built', 'warning');
          return;
        }
      }
      
      if (stricken_date) {
        if (stricken_date < (commissioned_date || year_built)) {
          this.showAlert('Stricken date cannot be earlier than commissioned date or year built', 'warning');
          return;
        }
      }

      // Convert empty strings to null for optional fields
      const shipData = {
        ...this.newShip,
        name: this.newShip.name.trim(),
        commissioned_date: this.newShip.commissioned_date || null,
        stricken_date: this.newShip.stricken_date || null,
        country_of_origin: this.newShip.country_of_origin || null
      };

      try {
        const response = await axios.post(API_URL, shipData);
        this.$emit('ship-added', response.data);
        this.clearForm();
        this.closeModal();
        this.showAlert('Ship added successfully!', 'success');
      } catch (error) {
        console.error('Error adding ship:', error);
        const errorMessage = error.response?.data?.detail || 'Error adding ship. Please try again.';
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

/* Form Layout */
.modal-body {
  padding: 20px;
}

.add-ship-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Form Labels */
.form-group label {
  color: #00f7ff;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.9em;
}

.form-group label::after {
  content: " *";
  color: #ff4444;
}

.form-group label:not([required])::after {
  content: none;
}

/* Form Controls */
input, select {
  padding: 12px;
  border: 1px solid rgba(0, 247, 255, 0.3);
  background: rgba(13, 27, 42, 0.7);
  border-radius: 6px;
  color: white;
  font-size: 1em;
}

input:focus, select:focus {
  outline: none;
  border-color: rgba(0, 247, 255, 0.5);
  box-shadow: 0 0 10px rgba(0, 247, 255, 0.2);
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.form-action-btn {
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

.form-action-btn:hover {
  background: linear-gradient(to bottom, rgba(0, 247, 255, 0.1), rgba(0, 247, 255, 0.05));
  border-color: rgba(0, 247, 255, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 0 15px rgba(0, 247, 255, 0.2);
}

.form-action-btn.clear {
  background: rgba(13, 27, 42, 0.95);
  border: 1px solid rgba(255, 68, 68, 0.3);
  color: #ff4444;
}

.form-action-btn.clear:hover {
  border-color: rgba(255, 68, 68, 0.5);
  box-shadow: 0 0 10px rgba(255, 68, 68, 0.2);
}

.form-action-btn.submit {
  background: linear-gradient(to bottom, rgba(13, 27, 42, 0.9), rgba(13, 27, 42, 0.7));
  border: 1px solid rgba(0, 247, 255, 0.3);
}

.form-action-btn.submit:hover {
  border-color: rgba(0, 247, 255, 0.7);
  box-shadow: 0 0 15px rgba(0, 247, 255, 0.3);
}
</style> 