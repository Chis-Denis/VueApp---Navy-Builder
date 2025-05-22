<template>
  <div class="statistics-container">
    <div class="stats-buttons">
      <!-- Ships by Country Button -->
      <div class="stat-button" @click="showChart('country')" :class="{ active: activeChart === 'country' }">
        <div class="button-content">
          <div class="icon">🌍</div>
          <div class="text">
            <h3>Ships by Country</h3>
            <p>{{ mostCommonCountry }} leads with {{ getCountryCount(mostCommonCountry) }} ships</p>
          </div>
          <div class="hover-effect"></div>
        </div>
        <canvas v-if="activeChart === 'country'" ref="countryChart" class="chart-display"></canvas>
      </div>

      <!-- Ships by Year Button -->
      <div class="stat-button" @click="showChart('year')" :class="{ active: activeChart === 'year' }">
        <div class="button-content">
          <div class="icon">📅</div>
          <div class="text">
            <h3>Ships by Year</h3>
            <p>From {{ oldestShipYear }} to {{ newestShipYear }}</p>
          </div>
          <div class="hover-effect"></div>
        </div>
        <canvas v-if="activeChart === 'year'" ref="yearChart" class="chart-display"></canvas>
      </div>

      <!-- Active vs Retired Button -->
      <div class="stat-button" @click="showChart('status')" :class="{ active: activeChart === 'status' }">
        <div class="button-content">
          <div class="icon">⚓</div>
          <div class="text">
            <h3>Active vs Retired</h3>
            <p>{{ activeShips }} Active, {{ retiredShips }} Retired</p>
          </div>
          <div class="hover-effect"></div>
        </div>
        <canvas v-if="activeChart === 'status'" ref="statusChart" class="chart-display"></canvas>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
import api from '../../services/ShipService'

Chart.register(...registerables)

export default {
  name: 'StatisticsComponent',
  
  // Add event bus injection
  inject: ['$eventBus'],
  
  data() {
    return {
      totalShips: 0,
      mostCommonCountry: 'N/A',
      mostCommonCountryCount: 0,
      activeShips: 0,
      retiredShips: 0,
      oldestShipYear: 'N/A',
      newestShipYear: 'N/A',
      charts: {
        country: null,
        year: null,
        status: null
      },
      activeChart: null,
      unsubscribe: null // Store the unsubscribe function
    }
  },
  computed: {
    averageYearBuilt() {
      if (!this.ships.length) return 'N/A';
      return this.ships.reduce((total, ship) => total + ship.year_built, 0) / this.ships.length;
    }
  },
  methods: {
    async fetchStatistics() {
      try {
        const stats = await api.get('/ships/statistics');
        this.totalShips = stats.data.total;
        this.oldestShipYear = stats.data.oldest_year || 'N/A';
        this.newestShipYear = stats.data.newest_year || 'N/A';
        this.mostCommonCountry = stats.data.most_common_country || 'N/A';
        this.mostCommonCountryCount = stats.data.most_common_country_count || 0;
        this.activeShips = stats.data.active;
        this.retiredShips = stats.data.retired;
      } catch (error) {
        console.error('Error fetching statistics:', error);
      }
    },
    getCountryCount(country) {
      return country === this.mostCommonCountry ? this.mostCommonCountryCount : 0;
    },
    showChart(chartType) {
      if (this.activeChart === chartType) {
        this.activeChart = null
      } else {
        this.activeChart = chartType
        this.$nextTick(() => {
          this.createChart(chartType)
        })
      }
    },
    createChart(chartType) {
      if (this.charts[chartType]) {
        this.charts[chartType].destroy()
      }

      const chartConfigs = {
        country: this.createCountryChartConfig(),
        year: this.createYearChartConfig(),
        status: this.createStatusChartConfig()
      }

      const config = chartConfigs[chartType]
      if (config && this.$refs[`${chartType}Chart`]) {
        this.charts[chartType] = new Chart(this.$refs[`${chartType}Chart`], config)
      }
    },
    createCountryChartConfig() {
      return {
        type: 'pie',
        data: {
          labels: Object.keys(this.countryData),
          datasets: [{
            data: Object.values(this.countryData),
            backgroundColor: [
              '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
              '#FF9F40', '#FF6384', '#36A2EB', '#FFCE56'
            ]
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right'
            }
          }
        }
      }
    },
    createYearChartConfig() {
      const yearGroups = {}
      this.ships.forEach(ship => {
        yearGroups[ship.year_built] = (yearGroups[ship.year_built] || 0) + 1
      })

      // Sort years chronologically
      const sortedYears = Object.keys(yearGroups).sort((a, b) => a - b)

      return {
        type: 'bar',
        data: {
          labels: sortedYears,
          datasets: [{
            label: 'Ships Built',
            data: sortedYears.map(year => yearGroups[year]),
            backgroundColor: 'rgba(54, 162, 235, 0.8)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              ticks: {
                color: 'rgba(255, 255, 255, 0.7)'
              }
            },
            x: {
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              ticks: {
                color: 'rgba(255, 255, 255, 0.7)',
                maxRotation: 45,
                minRotation: 45
              }
            }
          },
          plugins: {
            legend: {
              labels: {
                color: 'rgba(255, 255, 255, 0.9)'
              }
            },
            title: {
              display: true,
              text: 'Ships Built by Year',
              color: 'rgba(255, 255, 255, 0.9)',
              font: {
                size: 16
              }
            }
          }
        }
      }
    },
    createStatusChartConfig() {
      return {
        type: 'doughnut',
        data: {
          labels: ['Active', 'Retired'],
          datasets: [{
            data: [this.activeShips, this.retiredShips],
            backgroundColor: ['#4BC0C0', '#FF6384']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right'
            }
          }
        }
      }
    },
    /**
     * Handles real-time updates when new ships are added
     * @param {Object} newShip - The newly added ship data
     */
    handleRealtimeUpdate(newShip) {
      // Add the new ship to our local ships array
      this.ships.unshift(newShip);
      
      // Update country statistics
      this.countryData[newShip.country_of_origin] = (this.countryData[newShip.country_of_origin] || 0) + 1;
      
      // Update most common country
      this.mostCommonCountry = Object.entries(this.countryData)
        .sort(([, a], [, b]) => b - a)[0][0];
      
      // Update active ships count
      if (!newShip.stricken_date) {
        this.activeShips++;
      }
      
      // Update total ships count
      this.totalShips++;
      
      // If a chart is currently displayed, update it
      if (this.activeChart) {
        this.createChart(this.activeChart);
      }
    },
  },
  async mounted() {
    await this.fetchStatistics();
    if (this.$eventBus) {
      this.unsubscribe = this.$eventBus.$on('new-ship-added', this.fetchStatistics);
    }
  },
  beforeUnmount() {
    if (this.unsubscribe) this.unsubscribe();
    Object.values(this.charts).forEach(chart => { if (chart) chart.destroy(); });
  }
}
</script>

<style scoped>
.statistics-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(180deg, rgba(13, 17, 23, 0.8) 0%, rgba(13, 17, 23, 0.95) 100%);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
}

.stats-buttons {
  display: flex;
  flex-direction: row;
  gap: 20px;
  padding: 20px;
  justify-content: center;
  align-items: stretch;
}

.stat-button {
  flex: 1;
  background: linear-gradient(135deg, rgba(23, 32, 42, 0.9) 0%, rgba(44, 62, 80, 0.9) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  height: 180px;
  max-width: 400px;
  backdrop-filter: blur(5px);
  display: flex;
  flex-direction: column;
}

.stat-button:hover:not(.active) {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 123, 255, 0.2),
              0 0 20px rgba(0, 123, 255, 0.1),
              0 0 40px rgba(0, 123, 255, 0.05);
  border-color: rgba(0, 123, 255, 0.5);
}

.stat-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(0, 123, 255, 0.8) 50%, 
    transparent 100%
  );
  animation: scan 2s linear infinite;
}

@keyframes scan {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.button-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  color: white;
  z-index: 1;
  position: relative;
}

.icon {
  font-size: 2.5rem;
  background: rgba(0, 123, 255, 0.1);
  padding: 20px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0, 123, 255, 0.2);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.text {
  text-align: center;
}

.text h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.95);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.text p {
  margin: 0;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 300;
}

.hover-effect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(
    circle at var(--x, 50%) var(--y, 50%),
    rgba(0, 123, 255, 0.1) 0%,
    transparent 60%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-button:hover .hover-effect {
  opacity: 1;
}

.stat-button.active {
  flex: 2;
  height: auto;
  min-height: 550px;
  cursor: default;
  transform: none;
}

.chart-display {
  margin-top: 30px;
  width: 100%;
  height: 350px !important;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

@media (max-width: 1024px) {
  .stats-buttons {
    flex-direction: column;
    align-items: stretch;
  }

  .stat-button {
    width: 100%;
    max-width: none;
  }

  .stat-button.active {
    min-height: 500px;
    height: auto;
  }

  .chart-display {
    height: 300px !important;
    padding: 15px;
  }
}

@media (max-width: 768px) {
  .button-content {
    gap: 10px;
  }

  .icon {
    padding: 15px;
    font-size: 2rem;
  }

  .text h3 {
    font-size: 1.1rem;
  }

  .text p {
    font-size: 0.9rem;
  }
}
</style> 