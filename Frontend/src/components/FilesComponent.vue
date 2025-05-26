<template>
  <div class="files-container">
    <h2 class="files-title">Files</h2>
    <div class="files-content">
      <!-- File Upload/Download Section -->
      <div class="file-actions glass-card">
        <div class="upload-section">
          <input
            type="file"
            ref="fileInput"
            @change="handleFileUpload"
            style="display: none"
          >
          <button class="file-btn upload-btn" @click="$refs.fileInput.click()">
            <i class="fas fa-upload"></i>
            UPLOAD FILE
          </button>
          <div v-if="isUploading" class="upload-progress">
            <div class="progress-bar">
              <div :style="{ width: uploadProgress + '%' }" class="progress-fill"></div>
            </div>
            <span>{{ uploadProgress }}%</span>
          </div>
        </div>

        <button class="file-btn download-btn" @click="showDownloadDialog">
          <i class="fas fa-download"></i>
          DOWNLOAD FILES
        </button>
      </div>

      <!-- Download Modal -->
      <div v-if="showDownloadModal" class="modal-overlay">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Available Files</h2>
            <button class="close-btn" @click="closeDownloadDialog">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="availableFiles.length === 0" class="no-files">
              No files available for download
            </div>
            <div v-else class="file-list">
              <div v-for="file in availableFiles" :key="file" class="file-item">
                <span class="file-name">{{ file }}</span>
                <button class="action-btn-small" @click="downloadFile(file)">
                  <i class="fas fa-download"></i>
                  DOWNLOAD
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
const FILE_API_URL = 'http://localhost:8000/files';

export default {
  name: 'FilesComponent',
  inject: ['showAlert'],
  data() {
    return {
      isUploading: false,
      uploadProgress: 0,
      showDownloadModal: false,
      availableFiles: [],
    };
  },
  methods: {
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      const formData = new FormData();
      formData.append('file', file);
      this.isUploading = true;
      this.uploadProgress = 0;
      try {
        await axios.post(`${FILE_API_URL}/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            this.uploadProgress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
          }
        });
        this.showAlert('File uploaded successfully!', 'success');
        this.fetchAvailableFiles();
      } catch (error) {
        console.error('Error uploading file:', error);
        this.showAlert('Error uploading file. Please try again.', 'error');
      } finally {
        this.isUploading = false;
        this.uploadProgress = 0;
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
    }
  },
  mounted() {
    this.fetchAvailableFiles();
  }
}
</script>

<style scoped>
.files-container {
  padding: 20px;
  color: #00f7ff;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.files-title {
  color: #7ffcff;
  font-size: 2.1em;
  font-family: 'Orbitron', sans-serif;
  text-align: center;
  margin-bottom: 12px;
  letter-spacing: 2px;
  text-shadow: 0 0 12px #00f7ff33, 0 2px 8px #000a;
}

.files-content {
  background: rgba(13, 27, 42, 0.38);
  border-radius: 16px;
  padding: 48px 0 48px 0;
  margin-top: 10px;
  width: 100vw;
  max-width: 100vw;
  min-height: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}

.glass-card {
  margin: 0 auto 24px auto;
  background: linear-gradient(120deg, rgba(20, 30, 50, 0.68) 60%, rgba(0, 247, 255, 0.07) 100%);
  border-radius: 14px;
  border: 1.5px solid rgba(0, 247, 255, 0.13);
  box-shadow: 0 4px 32px 0 rgba(0,247,255,0.07), 0 2px 16px 0 rgba(0,0,0,0.18);
  backdrop-filter: blur(10px);
  padding: 28px 24px 24px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  min-width: 320px;
  max-width: 380px;
  width: auto;
  position: relative;
  box-sizing: border-box;
  border-bottom: 2.5px solid rgba(0, 247, 255, 0.10);
}

.file-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 12px 0;
  font-size: 1.08em;
  background: linear-gradient(120deg, rgba(13, 27, 42, 0.93) 60%, rgba(0, 247, 255, 0.07) 100%);
  border: 1.5px solid rgba(0, 247, 255, 0.16);
  color: #7ffcff;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.22s cubic-bezier(.4,2,.6,1);
  text-transform: uppercase;
  letter-spacing: 1.1px;
  font-weight: 600;
  min-width: 260px;
  max-width: 340px;
  width: 100%;
  margin: 0;
  height: 44px;
  line-height: 1;
  box-shadow: 0 1px 8px 0 rgba(0,247,255,0.06);
  position: relative;
  overflow: hidden;
}

.file-btn i {
  font-size: 1.35em;
  line-height: 1;
  display: flex;
  align-items: center;
  transition: transform 0.3s cubic-bezier(.4,2,.6,1), color 0.3s;
}

.file-btn:hover {
  background: linear-gradient(120deg, rgba(0, 247, 255, 0.13) 0%, rgba(13, 27, 42, 0.93) 100%);
  border-color: #00f7ff;
  color: #fff;
  box-shadow: 0 0 16px 1px #00f7ff33, 0 2px 8px #00f7ff22;
}

.file-btn:hover i {
  color: #fff;
  transform: scale(1.12) translateY(-1px);
  filter: drop-shadow(0 0 6px #00f7ff99);
}

.upload-progress {
  margin-top: 6px;
  height: 2px;
}

.progress-bar {
  width: 100%;
  height: 2px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 1px;
  overflow: hidden;
  margin-bottom: 2px;
}

.progress-fill {
  height: 100%;
  background: #00f7ff;
  transition: width 0.3s ease;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(13, 27, 42, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: rgba(15, 23, 42, 0.95);
  border-radius: 12px;
  padding: 30px;
  width: 90%;
  max-width: 400px;
  border: 1px solid rgba(0, 247, 255, 0.2);
  box-shadow: 0 0 30px rgba(0, 247, 255, 0.1);
  animation: dialogAppear 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.close-btn {
  background: none;
  border: none;
  color: #00f7ff;
  font-size: 1.3em;
  cursor: pointer;
  opacity: 0.7;
  transition: all 0.3s ease;
}

.close-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}

.no-files {
  color: #ff4444;
  text-align: center;
  font-weight: bold;
  margin: 20px 0;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(13, 27, 42, 0.7);
  border-radius: 6px;
  padding: 8px 12px;
  color: #00f7ff;
}

.file-name {
  font-size: 1em;
  font-weight: 500;
}

.action-btn-small {
  padding: 6px 12px;
  font-size: 0.9em;
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
</style> 