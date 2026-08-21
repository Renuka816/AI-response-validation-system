import axios from "axios";

const API = axios.create({
    baseURL: "https://ai-response-gigitvalidation-system-1.onrender.com",
});

export default API;