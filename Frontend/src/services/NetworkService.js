/**
 * Service to track network connectivity status and server availability
 */
class NetworkService {
    constructor() {
        this.isOnline = navigator.onLine;
        this.isServerAvailable = true;
        this.serverCheckUrl = 'http://localhost:8000/health';
        this.offlineQueue = [];
        this.syncInterval = null;
        
        // Bind event listeners
        window.addEventListener('online', this._handleOnlineStatus.bind(this));
        window.addEventListener('offline', this._handleOnlineStatus.bind(this));
        
        // Initial server check
        this._checkServerAvailability();
        
        // Set up periodic server checks
        setInterval(this._checkServerAvailability.bind(this), 30000);
    }
    
    _handleOnlineStatus() {
        this.isOnline = navigator.onLine;
        if (this.isOnline) {
            // When we come back online, check server immediately
            this._checkServerAvailability();
        } else {
            this.isServerAvailable = false;
        }
    }
    
    async _checkServerAvailability() {
        if (!this.isOnline) {
            this.isServerAvailable = false;
            return;
        }
        
        try {
            const response = await fetch(this.serverCheckUrl, { 
                method: 'GET',
                headers: { 'Cache-Control': 'no-cache' },
                timeout: 5000
            });
            this.isServerAvailable = response.ok;
        } catch (error) {
            this.isServerAvailable = false;
            console.error('Server check failed:', error);
        }
    }
    
    isConnected = () => {
        return this.isOnline && this.isServerAvailable;
    }
    
    addToOfflineQueue = (operation) => {
        this.offlineQueue.push({
            ...operation,
            timestamp: new Date().toISOString()
        });
        this.saveOfflineQueue();
    }
    
    saveOfflineQueue = () => {
        localStorage.setItem('offlineQueue', JSON.stringify(this.offlineQueue));
    }
    
    loadOfflineQueue = () => {
        const queue = localStorage.getItem('offlineQueue');
        this.offlineQueue = queue ? JSON.parse(queue) : [];
    }
    
    syncOfflineChanges = async () => {
        if (!this.isConnected()) return;
        
        this.loadOfflineQueue();
        const queue = [...this.offlineQueue];
        this.offlineQueue = [];
        this.saveOfflineQueue();
        
        for (const operation of queue) {
            try {
                switch (operation.type) {
                    case 'CREATE':
                        await fetch(this.serverCheckUrl, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(operation.data)
                        });
                        break;
                    case 'UPDATE':
                        await fetch(this.serverCheckUrl, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(operation.data)
                        });
                        break;
                    case 'DELETE':
                        await fetch(this.serverCheckUrl, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ id: operation.id })
                        });
                        break;
                }
            } catch (error) {
                // If sync fails, add back to queue
                this.offlineQueue.push(operation);
                this.saveOfflineQueue();
                break;
            }
        }
    }
    
    // Cleanup
    destroy = () => {
        window.removeEventListener('online', this._handleOnlineStatus.bind(this));
        window.removeEventListener('offline', this._handleOnlineStatus.bind(this));
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
            this.syncInterval = null;
        }
    }
}

// Create singleton instance
const instance = new NetworkService();
export default instance; 