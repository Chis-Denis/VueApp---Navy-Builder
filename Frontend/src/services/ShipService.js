import axios from 'axios';
import NetworkService from './NetworkService';
import config from '../config';

// Create axios instance with base URL
const api = axios.create({
    baseURL: config.apiBaseUrl
});

// Add a request interceptor to include the Authorization header if token exists
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

class ShipService {
    async getAllShips() {
        try {
            const response = await api.get(config.endpoints.ships);
            return response.data;
        } catch (error) {
            if (!NetworkService.isConnected()) {
                // Return local data when offline
                const localData = localStorage.getItem('ships');
                return localData ? JSON.parse(localData) : [];
            }
            throw error;
        }
    }

    async addShip(ship) {
        if (NetworkService.isConnected()) {
            const response = await api.post(config.endpoints.ships, ship);
            return response.data;
        } else {
            // Add to offline queue
            NetworkService.addToOfflineQueue({
                type: 'CREATE',
                data: ship
            });
            
            // Update local storage
            const localShips = JSON.parse(localStorage.getItem('ships') || '[]');
            const newShip = {
                ...ship,
                id: Date.now(), // Temporary ID for local storage
                isOffline: true
            };
            localShips.push(newShip);
            localStorage.setItem('ships', JSON.stringify(localShips));
            
            return newShip;
        }
    }

    async updateShip(id, ship) {
        if (NetworkService.isConnected()) {
            const response = await api.put(`${config.endpoints.ships}/${id}`, ship);
            return response.data;
        } else {
            // Add to offline queue
            NetworkService.addToOfflineQueue({
                type: 'UPDATE',
                id,
                data: ship
            });
            
            // Update local storage
            const localShips = JSON.parse(localStorage.getItem('ships') || '[]');
            const index = localShips.findIndex(s => s.id === id);
            if (index !== -1) {
                localShips[index] = {
                    ...localShips[index],
                    ...ship,
                    isOffline: true
                };
                localStorage.setItem('ships', JSON.stringify(localShips));
            }
            
            return localShips[index];
        }
    }

    async deleteShip(id) {
        if (NetworkService.isConnected()) {
            await api.delete(`${config.endpoints.ships}/${id}`);
            return true;
        } else {
            // Add to offline queue
            NetworkService.addToOfflineQueue({
                type: 'DELETE',
                id
            });
            
            // Update local storage
            const localShips = JSON.parse(localStorage.getItem('ships') || '[]');
            const filteredShips = localShips.filter(ship => ship.id !== id);
            localStorage.setItem('ships', JSON.stringify(filteredShips));
            
            return true;
        }
    }
}

export default new ShipService(); 

export const getShips = async () => {
    const response = await api.get(config.endpoints.ships);
    return response.data;
};

export const getShipById = async (id) => {
    const response = await api.get(`${config.endpoints.ships}/${id}`);
    return response.data;
};

export const createShip = async (ship) => {
    const response = await api.post(config.endpoints.ships, ship);
    return response.data;
};

export const updateShip = async (id, ship) => {
    const response = await api.put(`${config.endpoints.ships}/${id}`, ship);
    return response.data;
};

export const deleteShip = async (id) => {
    await api.delete(`${config.endpoints.ships}/${id}`);
};

export const searchShips = async (query) => {
    const response = await api.get(`${config.endpoints.ships}/search/?query=${query}`);
    return response.data;
};

export const filterShips = async (filters) => {
    const response = await api.get(`${config.endpoints.ships}/filter/`, { params: filters });
    return response.data;
};

export const getStatistics = async () => {
    const response = await api.get(config.endpoints.statistics);
    return response.data;
}; 