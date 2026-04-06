import axios from 'axios';

const api = axios.create({
  baseURL: 'https://celebro-mkt-bracci.onrender.com/api/v1', 
});

export default api;