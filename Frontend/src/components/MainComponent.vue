<template>
  <div class="container">
    <h1>Historical Ships Database</h1>

    <!-- Audio Player -->
    <div class="audio-player">
      <audio 
        ref="bgMusic" 
        loop
        preload="auto"
        @canplay="audioLoaded = true"
        @error="handleAudioError"
      >
        <source src="../assets/background-music.mp3" type="audio/mp3">
        Your browser does not support the audio element.
      </audio>
      <button 
        class="music-toggle"
        @click="toggleMusic"
        :class="{ 'playing': isMusicPlaying }"
        :disabled="!audioLoaded"
        aria-label="Toggle background music"
      >
        <i :class="isMusicPlaying ? 'fas fa-volume-up' : 'fas fa-volume-mute'"></i>
      </button>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <button class="action-btn search-btn" @click="showSearchModal = true">
        <i class="fas fa-search"></i>
        SEARCH
      </button>
      <button class="action-btn filter-btn" @click="showFilterModal = true">
        <i class="fas fa-filter"></i>
        FILTER
      </button>
      <button class="action-btn add-btn" @click="showAddModal = true">
        <i class="fas fa-plus"></i>
        ADD SHIP
      </button>
    </div>

    <!-- Ship List -->
    <div class="ships-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th @click="sortBy('name')" style="cursor: pointer">
              Name
              <i v-if="currentSort === 'name'" :class="['fas', sortAscending ? 'fa-sort-up' : 'fa-sort-down']"></i>
            </th>
            <th @click="sortBy('year_built')" style="cursor: pointer">
              Year Built
              <i v-if="currentSort === 'year_built'" :class="['fas', sortAscending ? 'fa-sort-up' : 'fa-sort-down']"></i>
            </th>
            <th @click="sortBy('commissioned_date')" style="cursor: pointer">
              Commissioned
              <i v-if="currentSort === 'commissioned_date'" :class="['fas', sortAscending ? 'fa-sort-up' : 'fa-sort-down']"></i>
            </th>
            <th @click="sortBy('stricken_date')" style="cursor: pointer">
              Stricken
              <i v-if="currentSort === 'stricken_date'" :class="['fas', sortAscending ? 'fa-sort-up' : 'fa-sort-down']"></i>
            </th>
            <th @click="sortBy('country_of_origin')" style="cursor: pointer">
              Country
              <i v-if="currentSort === 'country_of_origin'" :class="['fas', sortAscending ? 'fa-sort-up' : 'fa-sort-down']"></i>
            </th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ship in paginatedShips" :key="ship.id" :class="getRowClass(ship)">
            <td>{{ ship.id }}</td>
            <td>{{ ship.name }} <span v-if="newSystemShips.has(ship.id)" class="new-tag">NEW</span></td>
            <td>{{ ship.year_built }}</td>
            <td>{{ ship.commissioned_date }}</td>
            <td>{{ ship.stricken_date }}</td>
            <td>{{ ship.country_of_origin }}</td>
            <td class="actions">
              <button @click="updateShip(ship)" class="update">UPDATE</button>
              <button @click="deleteShip(ship.id)" class="delete">DELETE</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination Controls -->
    <div class="pagination">
      <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1" class="page-btn">
        <i class="fas fa-chevron-left"></i>
      </button>
      <span class="page-info" v-if="showTotalPages && totalPages">{{ currentPage }} / {{ totalPages }}</span>
      <span class="page-info" v-else>Page {{ currentPage }}</span>
      <button @click="changePage(currentPage + 1)" :disabled="showTotalPages ? currentPage === totalPages : ships.length < itemsPerPage" class="page-btn">
        <i class="fas fa-chevron-right"></i>
      </button>
    </div>

    <!-- Loading indicator - moved outside ships-table -->
    <div v-if="isLoading" class="loading-indicator">
      <div class="loading-spinner"></div>
      <span>Generating more ships...</span>
    </div>

    <!-- Load More Button -->
    <div v-if="!isLoading && hasMoreShips && currentPage === totalPages" class="load-more-container">
      <button @click="generateMoreShips" class="load-more-btn">
        <i class="fas fa-plus"></i> LOAD MORE SHIPS
      </button>
    </div>

    <!-- Chisu Capitanu Aesthetic Banner -->
    <div class="chisu-banner">
      <span>Chisu Capitanu</span>
    </div>

    <!-- Modal Components -->
    <SearchComponent 
      :show="showSearchModal" 
      @close="showSearchModal = false"
      @search-results="handleSearchResults"
      @clear-search="fetchShips"
    />
    <FilterComponent 
      :show="showFilterModal" 
      @close="showFilterModal = false"
      @filter-results="handleFilterResults"
      @clear-filter="fetchShips"
    />
    <AddComponent 
      :show="showAddModal" 
      @close="showAddModal = false"
      @ship-added="handleShipAdded"
    />

    <UpdateComponent 
      v-if="showUpdateModal"
      :show="showUpdateModal"
      :ship="shipToUpdate"
      @close="showUpdateModal = false"
      @ship-updated="handleShipUpdated"
    />

    <!-- Confirmation Dialog -->
    <div v-if="showConfirmDialog" class="confirm-overlay">
      <div class="confirm-dialog">
        <div class="confirm-content">
          <i class="fas fa-exclamation-triangle warning-icon"></i>
          <p>Are you sure you want to delete this ship?</p>
        </div>
        <div class="confirm-actions">
          <button @click="handleConfirm(true)" class="confirm-btn confirm">
            <i class="fas fa-check"></i> Yes
          </button>
          <button @click="handleConfirm(false)" class="confirm-btn cancel">
            <i class="fas fa-times"></i> No
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import SearchComponent from './ships/ShipSearch.vue';
import FilterComponent from './ships/ShipFilter.vue';
import AddComponent from './ships/ShipForm.vue';
import UpdateComponent from './ships/ShipUpdate.vue';
import { websocketService } from '../services/websocket';

// API endpoint for ship operations
const API_URL = "http://localhost:8000/ships";
const FILE_API_URL = "http://localhost:8000/files";

export default {
  name: 'MainComponent',
  
  // Register child components
  components: {
    SearchComponent,
    FilterComponent,
    AddComponent,
    UpdateComponent,
  },

  // Inject the global alert function
  inject: ['showAlert'],

  // Component state
  data() {
    return {
      ships: [],                 // List of ships from the database
      showSearchModal: false,    // Controls search modal visibility
      showFilterModal: false,    // Controls filter modal visibility
      showAddModal: false,       // Controls add ship modal visibility
      showUpdateModal: false,    // Controls update modal visibility
      showConfirmDialog: false,  // Controls delete confirmation dialog
      shipToDelete: null,        // Stores ID of ship pending deletion
      shipToUpdate: null,        // Stores ship object for updating
      isMusicPlaying: false,
      audioLoaded: false,        // Track if audio is loaded
      currentSort: '',           // Current sort field
      sortAscending: true,       // Sort direction
      statistics: {
        maxCommissionDate: null,
        minCommissionDate: null,
        averageCommissionDate: null
      },
      isLoading: false,
      hasMoreShips: true,
      batchSize: 5, // Number of ships to generate at once
      uploadProgress: 0,
      isUploading: false,
      showDownloadModal: false,
      availableFiles: [],
      newSystemShips: new Set(), // Track newly added system ships
      currentPage: 1,
      itemsPerPage: 10,
      totalPages: 1,
      showTotalPages: true,
    };
  },

  computed: {
    paginatedShips() {
      return this.ships;
    }
  },

  methods: {
    /**
     * Disable automatic generation of ships on the server
     */
    disableAutoGeneration() {
      try {
        // Send a message to the websocket to disable auto-generation
        const sent = websocketService.sendMessage("disable-auto-generation");
        console.log("Attempted to disable auto-generation, success:", sent);
        
        // Also use the HTTP API as a backup method
        axios.post("http://localhost:8000/auto-generation/toggle", { enable: false })
          .then(response => {
            console.log("Auto-generation disabled via API:", response.data);
          })
          .catch(error => {
            console.error("Error disabling via API:", error);
          });
      } catch (error) {
        console.error("Error disabling automatic ship generation:", error);
      }
    },

    /**
     * Fetches all ships from the database
     * Used on component mount and after operations that modify data
     */
    async fetchShipsPage(page = 1) {
      this.isLoading = true;
      try {
        const response = await axios.get(`${API_URL}/page/`, {
          params: { page, page_size: this.itemsPerPage }
        });
        this.ships = response.data.ships;
        if (response.data.total === null || response.data.total === undefined) {
          this.showTotalPages = false;
          this.totalPages = null;
        } else {
          this.showTotalPages = true;
          this.totalPages = Math.ceil(response.data.total / this.itemsPerPage);
        }
        this.currentPage = page;
        this.calculateStatistics();
      } catch (error) {
        console.error("Error fetching paginated ships:", error);
        this.showAlert('Error fetching ships. Please try again.', 'error');
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Updates the ships list with search results
     * @param {Array} results - Array of ships matching search criteria
     */
    handleSearchResults(results) {
      this.ships = results;
    },

    /**
     * Updates the ships list with filter results
     * @param {Array} results - Array of ships matching filter criteria
     */
    handleFilterResults(results) {
      this.ships = results;
    },

    /**
     * Handles real-time ship additions from WebSocket
     * @param {Object} newShip - The newly added ship data
     */
    handleRealtimeShipAdd(newShip) {
      // Add the ship to the list
      this.ships.push(newShip);
      this.calculateStatistics();
      
      // Set current page to see new ship if user is on the last page
      const wasOnLastPage = this.currentPage === this.totalPages;
      
      // Add NEW tag for system-generated ships
      if (newShip.source === 'system') {
        this.newSystemShips.add(newShip.id);
        setTimeout(() => {
          this.newSystemShips.delete(newShip.id);
          // Force a re-render
          this.ships = [...this.ships];
        }, 60000); // NEW tag stays for 1 minute
      }
      
      // Update pagination to show the new ship if user was on the last page
      if (wasOnLastPage) {
        this.currentPage = this.totalPages;
      }
    },

    /**
     * Handles successful ship addition by user
     * Refreshes the ship list and shows success message
     */
    handleShipAdded() {
      this.fetchShips();
      this.showAlert('Ship added successfully!', 'success');
    },

    /**
     * Updates an existing ship's information
     * @param {Object} ship - Ship object with updated data
     */
    async updateShip(ship) {
      this.shipToUpdate = ship;
      this.showUpdateModal = true;
    },

    handleShipUpdated() {
      this.fetchShips();
      this.showUpdateModal = false;
      this.shipToUpdate = null;
    },

    /**
     * Initiates the ship deletion process
     * @param {number} id - ID of the ship to delete
     */
    async deleteShip(id) {
      this.shipToDelete = id;
      this.showConfirmDialog = true;
    },

    /**
     * Handles the confirmation response for ship deletion
     * @param {boolean} confirmed - Whether the user confirmed the deletion
     */
    async handleConfirm(confirmed) {
      if (confirmed && this.shipToDelete) {
        try {
          const response = await axios.delete(`${API_URL}/${this.shipToDelete}`);
          if (response.status === 200) {
            await this.fetchShips();
            this.showAlert('Ship deleted successfully!', 'success');
          } else {
            throw new Error('Failed to delete ship');
          }
        } catch (error) {
          console.error("Error deleting ship:", error);
          this.showAlert('Error deleting ship. Please try again.', 'error');
        }
      }
      this.showConfirmDialog = false;
      this.shipToDelete = null;
    },

    /**
     * Handle audio loading errors
     * @param {Event} error - The error event
     */
    handleAudioError(error) {
      console.error('Audio loading error:', error);
      this.showAlert('Failed to load background music.', 'error');
    },

    /**
     * Toggle background music play/pause
     */
    async toggleMusic() {
      console.log('Toggle music called. Audio loaded:', this.audioLoaded);
      console.log('Audio element:', this.$refs.bgMusic);

      if (!this.audioLoaded || !this.$refs.bgMusic) {
        console.warn('Audio not ready');
        return;
      }

      try {
        if (this.isMusicPlaying) {
          console.log('Pausing music...');
          await this.$refs.bgMusic.pause();
        } else {
          console.log('Playing music...');
          await this.$refs.bgMusic.play();
        }
        this.isMusicPlaying = !this.isMusicPlaying;
        console.log('Music playing state:', this.isMusicPlaying);
      } catch (error) {
        console.error('Audio playback failed:', error);
        this.showAlert('Failed to play audio. Please try again.', 'error');
        this.isMusicPlaying = false;
      }
    },

    /**
     * Handles sorting when a column header is clicked
     * @param {string} field - The field to sort by
     */
    async sortBy(field) {
      try {
        if (this.currentSort === field) {
          if (!this.sortAscending) {
            // Third click - reset to original state
            this.currentSort = '';
            await this.fetchShips(); // Fetch original order
            return;
          }
          // Second click - toggle to descending
          this.sortAscending = !this.sortAscending;
        } else {
          // First click on a new field - sort ascending
          this.currentSort = field;
          this.sortAscending = true;
        }

        const params = new URLSearchParams({
          field: this.currentSort,
          ascending: this.sortAscending
        });

        const response = await axios.get(`${API_URL}/sort/?${params.toString()}`);
        this.ships = response.data;
      } catch (error) {
        console.error('Error sorting ships:', error);
        const errorMessage = error.response?.data?.detail || 'Error sorting ships. Please try again.';
        this.showAlert(errorMessage, 'error');
      }
    },

    /**
     * Calculates statistics for the ships
     */
    calculateStatistics() {
      if (this.ships.length === 0) return;

      const commissionDates = this.ships
        .map(ship => ship.commissioned_date)
        .filter(date => date !== null);

      if (commissionDates.length > 0) {
        this.statistics.maxCommissionDate = Math.max(...commissionDates);
        this.statistics.minCommissionDate = Math.min(...commissionDates);
        this.statistics.averageCommissionDate = Math.round(
          commissionDates.reduce((a, b) => a + b) / commissionDates.length
        );
      }
    },

    getRowClass(ship) {
      if (!ship.commissioned_date) return '';
      
      if (ship.commissioned_date === this.statistics.maxCommissionDate) {
        return 'newest-ship';
      }
      if (ship.commissioned_date === this.statistics.minCommissionDate) {
        return 'oldest-ship';
      }
      if (Math.abs(ship.commissioned_date - this.statistics.averageCommissionDate) < 1) { // within 1 year
        return 'average-ship';
      }
      return '';
    },

    changePage(page) {
      if (page < 1) return;
      if (this.showTotalPages && page > this.totalPages) return;
      this.fetchShipsPage(page);
    },

    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      this.isUploading = true;
      this.uploadProgress = 0;

      try {
        await axios.post(`${FILE_API_URL}/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            this.uploadProgress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
          }
        });

        this.showAlert('File uploaded successfully!', 'success');
        // Don't automatically fetch files anymore
      } catch (error) {
        console.error('Error uploading file:', error);
        this.showAlert('Error uploading file. Please try again.', 'error');
      } finally {
        this.isUploading = false;
        this.uploadProgress = 0;
        // Clear the file input
        event.target.value = '';
      }
    },

    async showDownloadDialog() {
      try {
        await this.fetchAvailableFiles();
        this.showDownloadModal = true;
      } catch (error) {
        console.error('Error fetching files:', error);
        this.showAlert('Error fetching available files.', 'error');
      }
    },

    closeDownloadDialog() {
      this.showDownloadModal = false;
      this.availableFiles = [];
    },

    async fetchAvailableFiles() {
      try {
        const response = await axios.get(`${FILE_API_URL}/list`);
        this.availableFiles = response.data;
      } catch (error) {
        console.error('Error fetching files:', error);
        this.showAlert('Error fetching available files.', 'error');
      }
    },

    async downloadFile(filename) {
      try {
        const response = await axios.get(`${FILE_API_URL}/download/${filename}`, {
          responseType: 'blob'
        });

        // Create a blob URL and trigger download
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error downloading file:', error);
        this.showAlert('Error downloading file. Please try again.', 'error');
      }
    },

    /**
     * Triggers generation of more ships when the Load More button is clicked
     */
    async generateMoreShips() {
      if (this.isLoading || !this.hasMoreShips) return;
      
      this.isLoading = true; // Show loading before generating
      
      try {
        // Use the websocket service to send the message directly
        const sent = websocketService.sendMessage("generate-ship");
        if (!sent) {
          this.showAlert('Failed to connect to server. Please try again.', 'error');
          this.isLoading = false;
          return;
        }
        
        // Wait for the batch to complete
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Stay on the last page to see new ships
        this.currentPage = Math.ceil(this.ships.length / this.itemsPerPage);
      } catch (error) {
        console.error('Error generating ships:', error);
        this.showAlert('Error generating ships. Please try again.', 'error');
      } finally {
        this.isLoading = false;
      }
    },

    async fetchShips() {
      await this.fetchShipsPage(1);
    },
  },

  // Lifecycle hook - fetch ships when component mounts
  mounted() {
    // Initial ships fetch
    this.fetchShips();
    this.fetchAvailableFiles();
    
    // Disable automatic ship generation
    this.disableAutoGeneration();
    
    // Listen for new ship events from WebSocket
    this.$eventBus.$on('new-ship-added', (newShip) => {
      // Handle the ship addition
      this.handleRealtimeShipAdd(newShip);
    });
    
    // Initialize audio element
    if (this.$refs.bgMusic) {
      this.$refs.bgMusic.volume = 0.5;
    }
  },

  beforeUnmount() {
    // Clean up event listener
    this.$eventBus.$off('new-ship-added');
    
    // Stop music when component is destroyed
    if (this.$refs.bgMusic) {
      this.$refs.bgMusic.pause();
      this.$refs.bgMusic.currentTime = 0;
    }
  },

  watch: {
    ships: {
      handler() {
        this.calculateStatistics();
      },
      deep: true
    }
  }
};
</script>

<style>
/* Import Font Awesome for icons */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');

/* Global Background */
body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background-image: url('../assets/World-of-Warships.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  background-repeat: no-repeat;
}

/* Main Container */
.container {
  max-width: 1200px;
  margin: 70px auto;
  padding: 20px;
  background-color: rgba(15, 23, 42, 0.85);
  border-radius: 15px;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Page Title */
h1 {
  color: white;
  margin-bottom: 30px;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
  font-size: 2.5em;
  font-family: 'Orbitron', sans-serif;
  text-transform: uppercase;
  letter-spacing: 2px;
}

/* Audio Player Styles */
.audio-player {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 100;
}

.music-toggle {
  background: rgba(13, 27, 42, 0.8);
  border: 2px solid rgba(0, 247, 255, 0.3);
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00f7ff;
  font-size: 1.2em;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.music-toggle:hover {
  border-color: rgba(0, 247, 255, 0.8);
  transform: scale(1.1);
  box-shadow: 0 0 15px rgba(0, 247, 255, 0.3);
}

.music-toggle.playing {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(0, 247, 255, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(0, 247, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(0, 247, 255, 0);
  }
}

/* Action Buttons Section */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
  padding: 20px;
  background-color: rgba(13, 27, 42, 0.7);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 247, 255, 0.1);
}

/* Main Action Buttons */
.action-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  font-size: 1em;
  background: linear-gradient(to bottom, rgba(13, 27, 42, 0.9), rgba(13, 27, 42, 0.7));
  border: 1px solid rgba(0, 247, 255, 0.3);
  color: #00f7ff;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: bold;
  min-width: 150px;
}

.action-btn:hover {
  background: linear-gradient(to bottom, rgba(0, 247, 255, 0.1), rgba(0, 247, 255, 0.05));
  border-color: rgba(0, 247, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(0, 247, 255, 0.2);
}

.action-btn i {
  font-size: 1.2em;
}

/* Table Container */
.ships-table {
  width: 100%;
  height: 390px;
  overflow-y: auto;
  margin: 20px auto;
  background-color: rgba(13, 27, 42, 0.7);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 247, 255, 0.1);
}

/* Scrollbar Styling */
.ships-table::-webkit-scrollbar {
  width: 8px;
}

.ships-table::-webkit-scrollbar-track {
  background: rgba(13, 27, 42, 0.6);
  border-radius: 4px;
}

.ships-table::-webkit-scrollbar-thumb {
  background: rgba(0, 247, 255, 0.2);
  border-radius: 4px;
}

.ships-table::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 247, 255, 0.3);
}

/* Table Styling */
table {
  width: 100%;
  border-collapse: collapse;
  background-color: transparent;
  color: white;
}

th {
  background-color: rgba(13, 27, 42, 0.95);
  color: white;
  font-weight: bold;
  padding: 8px;
  height: 40px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.85em;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
  user-select: none;
}

th i {
  margin-left: 5px;
  font-size: 0.9em;
  color: #00f7ff;
  opacity: 0.8;
  vertical-align: middle;
}

th:hover {
  background-color: rgba(13, 27, 42, 1);
}

th:hover i {
  opacity: 1;
}

td {
  padding: 8px;
  border: 1px solid rgba(0, 247, 255, 0.1);
  text-align: center;
  height: 50px;
  vertical-align: middle;
}

tr:nth-child(even) {
  background-color: rgba(13, 27, 42, 0.3);
}

tr:hover {
  background-color: rgba(0, 247, 255, 0.05);
}

/* Table Input Fields */
td input {
  width: 100%;
  box-sizing: border-box;
  background-color: rgba(13, 27, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  text-align: center;
  padding: 4px 8px;
  margin: 0;
}

/* Empty State Message */
p {
  color: #00f7ff;
  font-size: 1.2em;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(0, 247, 255, 0.5);
}

/* Table Action Buttons */
.action-btn-small {
  padding: 6px 12px;
  font-size: 0.8em;
  background: linear-gradient(to bottom, rgba(13, 27, 42, 0.9), rgba(13, 27, 42, 0.7));
  border: 1px solid rgba(0, 247, 255, 0.3);
  color: #00f7ff;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: bold;
  margin: 0 2px;
}

.action-btn-small:hover {
  background: linear-gradient(to bottom, rgba(0, 247, 255, 0.1), rgba(0, 247, 255, 0.05));
  border-color: rgba(0, 247, 255, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 0 10px rgba(0, 247, 255, 0.2);
}

/* Delete Button Specific Styles */
.action-btn-small.delete {
  border-color: rgba(255, 68, 68, 0.3);
  color: #ff4444;
}

.action-btn-small.delete:hover {
  background: linear-gradient(to bottom, rgba(220, 38, 38, 0.1), rgba(220, 38, 38, 0.05));
  border-color: rgba(255, 68, 68, 0.5);
  box-shadow: 0 0 10px rgba(255, 68, 68, 0.2);
}

/* Confirmation Dialog */
.confirm-overlay {
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

.confirm-dialog {
  background: rgba(15, 23, 42, 0.95);
  border-radius: 12px;
  padding: 30px;
  width: 90%;
  max-width: 400px;
  border: 1px solid rgba(0, 247, 255, 0.2);
  box-shadow: 0 0 30px rgba(0, 247, 255, 0.1);
  animation: dialogAppear 0.3s ease;
}

.confirm-content {
  text-align: center;
  margin-bottom: 25px;
}

.warning-icon {
  font-size: 2.5em;
  color: #f7ae00;
  margin-bottom: 20px;
  animation: pulseWarning 2s infinite;
}

.confirm-content p {
  color: white;
  font-size: 1.2em;
  margin: 0;
  font-family: 'Orbitron', sans-serif;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.confirm-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.confirm-btn {
  padding: 12px 30px;
  font-size: 1em;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Orbitron', sans-serif;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
}

/* Confirmation Button Styles */
.confirm-btn.confirm {
  color: #48bb78;
  border: 1px solid rgba(72, 187, 120, 0.5);
}

.confirm-btn.confirm:hover {
  background: rgba(72, 187, 120, 0.1);
  box-shadow: 0 0 15px rgba(72, 187, 120, 0.3);
  transform: translateY(-2px);
}

.confirm-btn.cancel {
  color: #ff4444;
  border: 1px solid rgba(255, 68, 68, 0.5);
}

.confirm-btn.cancel:hover {
  background: rgba(255, 68, 68, 0.1);
  box-shadow: 0 0 15px rgba(255, 68, 68, 0.3);
  transform: translateY(-2px);
}

/* Dialog Animations */
@keyframes dialogAppear {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulseWarning {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Loading Indicator Styles */
.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 15px;
  color: #00f7ff;
  gap: 10px;
  background: rgba(13, 27, 42, 0.9);
  border-radius: 8px;
  margin: 20px auto;
  width: fit-content;
  border: 1px solid rgba(0, 247, 255, 0.2);
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(0, 247, 255, 0.3);
  border-top-color: #00f7ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Update the table actions cell styles */
td.actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.update, .delete {
  padding: 6px 12px;
  font-size: 0.8em;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: bold;
}

.update {
  background: linear-gradient(to bottom, rgba(13, 27, 42, 0.9), rgba(13, 27, 42, 0.7));
  border: 1px solid rgba(0, 247, 255, 0.3);
  color: #00f7ff;
}

.update:hover {
  background: linear-gradient(to bottom, rgba(0, 247, 255, 0.1), rgba(0, 247, 255, 0.05));
  border-color: rgba(0, 247, 255, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 0 10px rgba(0, 247, 255, 0.2);
}

.delete {
  background: linear-gradient(to bottom, rgba(13, 27, 42, 0.9), rgba(13, 27, 42, 0.7));
  border: 1px solid rgba(255, 68, 68, 0.3);
  color: #ff4444;
}

.delete:hover {
  background: linear-gradient(to bottom, rgba(220, 38, 38, 0.1), rgba(220, 38, 38, 0.05));
  border-color: rgba(255, 68, 68, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 0 10px rgba(255, 68, 68, 0.2);
}

/* Add back the NEW tag styles */
.new-tag {
  background-color: rgba(72, 187, 120, 0.9);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7em;
  margin-left: 8px;
  font-weight: bold;
  animation: fadeInOut 2s infinite;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

@keyframes fadeInOut {
  0% { opacity: 0.7; }
  50% { opacity: 1; }
  100% { opacity: 0.7; }
}

/* Load More Button Styles */
.load-more-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  background-color: rgba(13, 27, 42, 0.7);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 247, 255, 0.1);
}

.load-more-btn {
  padding: 12px 24px;
  font-size: 1em;
  background: linear-gradient(to bottom, rgba(13, 27, 42, 0.9), rgba(13, 27, 42, 0.7));
  border: 1px solid rgba(0, 247, 255, 0.3);
  color: #00f7ff;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: bold;
}

.load-more-btn:hover {
  background: linear-gradient(to bottom, rgba(0, 247, 255, 0.1), rgba(0, 247, 255, 0.05));
  border-color: rgba(0, 247, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(0, 247, 255, 0.2);
}

/* Pagination Styles */
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.page-btn {
  padding: 8px 16px;
  font-size: 1em;
  background: linear-gradient(to bottom, rgba(13, 27, 42, 0.9), rgba(13, 27, 42, 0.7));
  border: 1px solid rgba(0, 247, 255, 0.3);
  color: #00f7ff;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 0 4px;
}

.page-btn:hover {
  background: linear-gradient(to bottom, rgba(0, 247, 255, 0.1), rgba(0, 247, 255, 0.05));
  border-color: rgba(0, 247, 255, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 0 10px rgba(0, 247, 255, 0.2);
}

.page-btn:disabled {
  background: rgba(13, 27, 42, 0.7);
  border-color: rgba(0, 247, 255, 0.1);
  cursor: not-allowed;
}

.page-info {
  padding: 8px 16px;
  font-size: 1em;
  color: #00f7ff;
  font-weight: bold;
}

/* Chisu Capitanu Aesthetic Banner */
.chisu-banner {
  margin: 40px auto 0 auto;
  padding: 22px 48px;
  max-width: 420px;
  background: rgba(13, 27, 42, 0.55);
  border-radius: 18px;
  box-shadow: 0 4px 32px 0 rgba(0,247,255,0.13), 0 2px 16px 0 rgba(0,0,0,0.18);
  border: 2.5px solid rgba(0, 247, 255, 0.18);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Orbitron', 'Montserrat', sans-serif;
  font-size: 2.1em;
  color: #7ffcff;
  letter-spacing: 2px;
  text-shadow: 0 0 18px #00f7ff55, 0 2px 8px #000a;
  font-weight: 700;
  transition: box-shadow 0.2s;
  animation: chisuGlow 2.5s infinite alternate;
}

@keyframes chisuGlow {
  0% {
    box-shadow: 0 0 24px 0 #00f7ff33, 0 2px 16px 0 rgba(0,0,0,0.18);
  }
  100% {
    box-shadow: 0 0 48px 0 #00f7ff99, 0 2px 16px 0 rgba(0,0,0,0.18);
  }
}
</style>
