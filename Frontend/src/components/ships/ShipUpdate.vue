<template>
  <div class="modal-overlay" v-if="show" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Update Ship</h2>
        <button class="close-btn" @click="closeModal" aria-label="Close modal">×</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <!-- Ship Name -->
          <div class="form-group">
            <label for="name">Ship Name</label>
            <input 
              id="name"
              v-model="updatedShip.name" 
              type="text" 
              required
            />
          </div>

          <!-- Year Built -->
          <div class="form-group">
            <label for="yearBuilt">Year Built</label>
            <input 
              id="yearBuilt"
              v-model.number="updatedShip.year_built" 
              type="number" 
              required
            />
          </div>

          <!-- Commissioned Date -->
          <div class="form-group">
            <label for="commissionedDate">Commissioned Date</label>
            <input 
              id="commissionedDate"
              v-model.number="updatedShip.commissioned_date" 
              type="number"
            />
          </div>

          <!-- Stricken Date -->
          <div class="form-group">
            <label for="strickenDate">Stricken Date</label>
            <input 
              id="strickenDate"
              v-model.number="updatedShip.stricken_date" 
              type="number"
            />
          </div>

          <!-- Country of Origin -->
          <div class="form-group">
            <label for="country">Country of Origin</label>
            <select id="country" v-model="updatedShip.country_of_origin">
              <option value="">Select Country</option>
              <option v-for="country in countries" :key="country.value" :value="country.value">
                {{ country.label }}
              </option>
            </select>
          </div>

          <!-- Submit Button -->
          <div class="form-actions">
            <button type="submit" class="submit-btn">Update Ship</button>
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
  name: 'UpdateComponent',
  inject: ['showAlert'],
  props: {
    show: {
      type: Boolean,
      required: true
    },
    ship: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      updatedShip: {
        name: '',
        year_built: null,
        commissioned_date: null,
        stricken_date: null,
        country_of_origin: ''
      },
      countries: COUNTRIES
    }
  },
  watch: {
    ship: {
      immediate: true,
      handler(newShip) {
        if (newShip) {
          this.updatedShip = { ...newShip };
        }
      }
    }
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },

    async handleSubmit() {
      try {
        // Validate dates
        if (this.updatedShip.commissioned_date && this.updatedShip.year_built) {
          if (this.updatedShip.commissioned_date < this.updatedShip.year_built) {
            this.showAlert('Commissioned date cannot be earlier than year built', 'warning');
            return;
          }
        }

        if (this.updatedShip.stricken_date) {
          if (this.updatedShip.stricken_date < (this.updatedShip.commissioned_date || this.updatedShip.year_built)) {
            this.showAlert('Stricken date cannot be earlier than commissioned date or year built', 'warning');
            return;
          }
        }

        const response = await axios.put(
          `${API_URL}/${this.ship.id}`, 
          this.updatedShip
        );

        if (response.status === 200) {
          this.$emit('ship-updated');
          this.closeModal();
          this.showAlert('Ship updated successfully', 'success');
        }
      } catch (error) {
        console.error('Error updating ship:', error);
        const errorMessage = error.response?.data?.detail || 'Error updating ship. Please try again.';
        this.showAlert(errorMessage, 'error');
      }
    }
  }
}
</script>

<style scoped>
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

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  color: #00f7ff;
  margin-bottom: 8px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.9em;
}

input, select {
  width: 100%;
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

.form-actions {
  margin-top: 30px;
  display: flex;
  justify-content: flex-end;
}

.submit-btn {
  padding: 12px 24px;
  background: linear-gradient(to bottom, rgba(0, 247, 255, 0.2), rgba(0, 247, 255, 0.1));
  border: 1px solid rgba(0, 247, 255, 0.3);
  color: #00f7ff;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background: linear-gradient(to bottom, rgba(0, 247, 255, 0.3), rgba(0, 247, 255, 0.2));
  border-color: rgba(0, 247, 255, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 0 15px rgba(0, 247, 255, 0.2);
}
</style> 