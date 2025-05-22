<template>
  <div class="statistics-container">
    <h2 class="statistics-title">Statistics</h2>
    <div class="statistics-content">
      <div v-if="loading" class="stats-loading">Loading statistics...</div>
      <div v-else-if="error" class="stats-error">{{ error }}</div>
      <div v-else class="stats-cards">
        <div class="stat-card">
          <div class="stat-label">Total Ships</div>
          <div class="stat-value">{{ stats.total }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Most Common Country</div>
          <div class="stat-value">{{ stats.most_common_country }} <span v-if="stats.most_common_country_count">({{ stats.most_common_country_count }})</span></div>
          </div>
        <div class="stat-card">
          <div class="stat-label">Active Ships</div>
          <div class="stat-value">{{ stats.active }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Retired Ships</div>
          <div class="stat-value">{{ stats.retired }}</div>
      </div>
        <div class="stat-card">
          <div class="stat-label">Oldest Ship Year</div>
          <div class="stat-value">{{ stats.oldest_year }}</div>
          </div>
        <div class="stat-card">
          <div class="stat-label">Newest Ship Year</div>
          <div class="stat-value">{{ stats.newest_year }}</div>
        </div>
      </div>
      <button v-if="!showVisuals" class="visualise-btn" @click="loadVisuals">Visualise</button>
      <div v-if="showVisuals" class="visuals-section">
        <div class="visual-card">
          <h3>Ships by Country</h3>
          <canvas ref="countryChart"></canvas>
        </div>
        <div class="visual-card">
          <h3>Ships by Year</h3>
          <canvas ref="yearChart"></canvas>
        </div>
        <div class="visual-card">
            <h3>Active vs Retired</h3>
          <canvas ref="statusChart"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'StatisticsComponent',
  data() {
    return {
      stats: {},
      loading: true,
      error: null,
      showVisuals: false,
      ships: [],
      charts: {
        country: null,
        year: null,
        status: null
      }
    }
  },
  async mounted() {
    this.loading = true;
    try {
      const response = await axios.get('http://localhost:8000/ships/statistics');
      this.stats = response.data;
      this.error = null;
    } catch (err) {
      this.error = 'Failed to load statistics.';
      this.stats = {};
    } finally {
      this.loading = false;
    }
  },
  methods: {
    async loadVisuals() {
      this.showVisuals = true;
      if (this.ships.length === 0) {
        try {
          const token = localStorage.getItem('token');
          const response = await axios.get('http://localhost:8000/ships/', {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
          this.ships = response.data;
        } catch (err) {
          this.error = 'Failed to load ships for visualisation.';
          return;
        }
      }
      this.$nextTick(() => {
        this.renderCountryChart();
        this.renderYearChart();
        this.renderStatusChart();
      });
    },
    renderCountryChart() {
      if (this.charts.country) this.charts.country.destroy();
      const countryCounts = {};
      this.ships.forEach(ship => {
        if (ship.country_of_origin) {
          countryCounts[ship.country_of_origin] = (countryCounts[ship.country_of_origin] || 0) + 1;
        }
      });
      // Get top 5 countries
      const sortedCountries = Object.entries(countryCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
      const labels = sortedCountries.map(([country]) => country);
      const data = sortedCountries.map(([, count]) => count);
      this.charts.country = new Chart(this.$refs.countryChart, {
        type: 'pie',
        data: {
          labels,
          datasets: [{
            data,
            backgroundColor: [
              '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'
            ]
          }]
        },
        options: {
          plugins: {
            legend: { position: 'bottom', labels: { color: '#7ffcff' } }
          },
          aspectRatio: 1.1,
          responsive: true,
          maintainAspectRatio: true
            }
      });
    },
    renderYearChart() {
      if (this.charts.year) this.charts.year.destroy();
      const yearCounts = {};
      this.ships.forEach(ship => {
        if (ship.year_built) {
          yearCounts[ship.year_built] = (yearCounts[ship.year_built] || 0) + 1;
        }
      });
      // Get top 5 years
      const sortedYears = Object.entries(yearCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([year, count]) => ({ year, count }));
      const labels = sortedYears.map(y => y.year);
      const data = sortedYears.map(y => y.count);
      this.charts.year = new Chart(this.$refs.yearChart, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Ships Built',
            data,
            backgroundColor: 'rgba(0,247,255,0.5)',
            borderColor: '#00f7ff',
            borderWidth: 2
          }]
        },
        options: {
          plugins: {
            legend: { display: false },
            title: { display: false }
          },
          aspectRatio: 1.3,
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            x: { ticks: { color: '#7ffcff' }, grid: { color: '#222' } },
            y: { ticks: { color: '#7ffcff' }, grid: { color: '#222' } }
            }
          }
      });
    },
    renderStatusChart() {
      if (this.charts.status) this.charts.status.destroy();
      let active = 0, retired = 0;
      this.ships.forEach(ship => {
        if (ship.stricken_date) retired++; else active++;
      });
      this.charts.status = new Chart(this.$refs.statusChart, {
        type: 'doughnut',
        data: {
          labels: ['Active', 'Retired'],
          datasets: [{
            data: [active, retired],
            backgroundColor: ['#00f7ff', '#FF6384']
          }]
        },
        options: {
          plugins: {
            legend: { position: 'bottom', labels: { color: '#7ffcff' } }
          },
          aspectRatio: 1.1,
          responsive: true,
          maintainAspectRatio: true
        }
        });
      }
  },
  beforeUnmount() {
    Object.values(this.charts).forEach(chart => { if (chart) chart.destroy(); });
  }
}
</script>

<style scoped>
.statistics-container {
  padding: 32px 0 0 0;
  color: #00f7ff;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.statistics-title {
  color: #7ffcff;
  font-size: 2.1em;
  font-family: 'Orbitron', sans-serif;
  text-align: center;
  margin-bottom: 18px;
  letter-spacing: 2px;
  text-shadow: 0 0 12px #00f7ff33, 0 2px 8px #000a;
}

.statistics-content {
  background: rgba(13, 27, 42, 0.38);
  border-radius: 16px;
  padding: 36px 0 36px 0;
  margin-top: 10px;
  width: 100vw;
  max-width: 100vw;
  min-height: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  box-shadow: 0 4px 32px 0 rgba(0,247,255,0.07), 0 2px 16px 0 rgba(0,0,0,0.18);
  border-bottom: 2.5px solid rgba(0, 247, 255, 0.10);
}

.stats-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 28px;
  justify-content: center;
  align-items: stretch;
  width: 100%;
  max-width: 900px;
}

.stat-card {
  background: linear-gradient(120deg, rgba(20, 30, 50, 0.68) 60%, rgba(0, 247, 255, 0.07) 100%);
  border-radius: 14px;
  border: 1.5px solid rgba(0, 247, 255, 0.13);
  box-shadow: 0 4px 32px 0 rgba(0,247,255,0.07), 0 2px 16px 0 rgba(0,0,0,0.18);
  backdrop-filter: blur(10px);
  padding: 22px 32px;
  min-width: 180px;
  max-width: 220px;
  flex: 1 1 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  transition: box-shadow 0.2s;
}

.stat-card:hover {
  box-shadow: 0 0 24px 0 #00f7ff55, 0 2px 16px 0 rgba(0,0,0,0.18);
  border-color: #00f7ff99;
}

.stat-label {
  font-size: 1.05em;
  color: #7ffcff;
  margin-bottom: 8px;
  letter-spacing: 1px;
  text-shadow: 0 0 8px #00f7ff22;
}

.stat-value {
  font-size: 1.7em;
  font-family: 'Orbitron', sans-serif;
  color: #fff;
  text-shadow: 0 0 10px #00f7ff44, 0 2px 8px #000a;
}

.stats-loading, .stats-error {
  color: #7ffcff;
  font-size: 1.2em;
  text-align: center;
  margin: 40px 0;
}

.visualise-btn {
  margin: 32px auto 0 auto;
  padding: 14px 38px;
  font-size: 1.15em;
  font-family: 'Orbitron', sans-serif;
  color: #00f7ff;
  background: linear-gradient(120deg, rgba(13, 27, 42, 0.93) 60%, rgba(0, 247, 255, 0.07) 100%);
  border: 2px solid #00f7ff55;
  border-radius: 24px;
  box-shadow: 0 2px 16px 0 rgba(0,247,255,0.08);
  cursor: pointer;
  letter-spacing: 2px;
  text-transform: uppercase;
  font-weight: 700;
  transition: all 0.22s cubic-bezier(.4,2,.6,1);
}
.visualise-btn:hover {
  background: #00f7ff22;
  color: #fff;
  border-color: #00f7ff;
  box-shadow: 0 0 24px #00f7ff55;
}

.visuals-section {
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  justify-content: center;
  align-items: flex-start;
  margin-top: 36px;
  width: 100%;
  max-width: 1200px;
}

.visual-card {
  background: rgba(13, 27, 42, 0.7);
  border-radius: 16px;
  box-shadow: 0 2px 16px 0 rgba(0,247,255,0.08);
  padding: 24px 18px 18px 18px;
  min-width: 320px;
  max-width: 380px;
  flex: 1 1 340px;
  display: flex;
    flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  }

.visual-card h3 {
  color: #7ffcff;
  font-size: 1.18em;
  margin-bottom: 18px;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 1.2px;
  text-align: center;
  }

.visual-card canvas {
  width: 100% !important;
  max-width: 320px;
  height: auto !important;
  aspect-ratio: 1.1/1 !important;
  background: rgba(0,0,0,0.08);
  border-radius: 10px;
  margin-bottom: 0;
  display: block;
  margin-left: auto;
  margin-right: auto;
}
</style> 