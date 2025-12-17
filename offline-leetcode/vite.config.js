// In vite.config.js  
  
import { defineConfig } from 'vite';  
import react from '@vitejs/plugin-react';  
  
// https://vitejs.dev/config/  
export default defineConfig({  
  plugins: [react()],  
  server: {  
    proxy: {  
      // Any request starting with /static will be forwarded  
      '/static': {  
        target: 'http://127.0.0.1:8000', // Your FastAPI backend URL  
        changeOrigin: true, // Recommended for virtual hosted sites  
      },  
      // You should also proxy your /api calls!  
      '/api': {  
        target: 'http://127.0.0.1:8000',  
        changeOrigin: true,  
      }  
    }  
  }  
});