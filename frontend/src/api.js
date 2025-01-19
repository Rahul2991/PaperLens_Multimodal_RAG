import axios from "axios";

const API = axios.create({ baseURL: "http://localhost:8000" });

API.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

API.interceptors.response.use(
    (response) => response,
    (error) => {
    if (error.response && error.response.status === 401) {
        // Handle unauthorized access (expired token)
        localStorage.removeItem("token");
    }
    return Promise.reject(error);
    }
);

export const registerUser = (userData) => API.post("/register", userData);
export const loginUser = (userData) => API.post("/login", userData);
export const fetchChat = () => API.get("/chat");
export const fetchChatBotResponse = (formData) => API.post("/chat_ai", formData);
