import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App);

// Create a global event bus
app.config.globalProperties.$eventBus = {
    $on: function(event, callback) {
        if (!this._events) this._events = {};
        if (!this._events[event]) this._events[event] = [];
        this._events[event].push(callback);
        return () => this.$off(event, callback);
    },
    $off: function(event, callback) {
        if (!this._events || !this._events[event]) return;
        if (!callback) {
            this._events[event] = [];
            return;
        }
        this._events[event] = this._events[event].filter(cb => cb !== callback);
    },
    $emit: function(event, ...args) {
        if (!this._events || !this._events[event]) return;
        this._events[event].forEach(callback => callback(...args));
    }
};

app.use(router)
app.mount('#app');
