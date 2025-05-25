const config = {
    apiBaseUrl: process.env.VUE_APP_API_URL || 'http://localhost:8000',
    endpoints: {
        ships: '/ships',
        auth: '/auth',
        files: '/files',
        statistics: '/ships/statistics',
        autoGeneration: '/auto-generation'
    }
};

export default config; 