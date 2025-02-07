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

export const registerUser = (userData) => API.post("/auth/register", userData);
export const loginUser = (userData) => API.post("/auth/login", userData);
export const fetchChat = () => API.get("/chat");
export const fetchChatBotResponse = (formData) => API.post("/chat/chat_ai", formData);
export const fetchChatSessions = () => API.get("/chat/sessions");
export const createChatSession = () => API.post("/chat/create_session");
export const deleteSession = async (sessionId) => API.delete(`/chat/sessions/${sessionId}`)
export const listUsers = () => API.get("/admin/users");
export const listFiles = () => API.get("/admin/list_files");

export const uploadRagFilesAdmin = (files, tags) => {
    const formData = new FormData();

    // Append all files to FormData
    files.forEach((file) => {
        formData.append("files", file);
    });

    // Optionally, append tags to FormData if needed
    formData.append("tags", tags);

    return API.post("/admin/upload", formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });
};