import axios from "axios";

const API = axios.create({
    baseURL: "https://onrender.com",
});

export default API;