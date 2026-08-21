import axios from "axios";

const API = axios.create({
  baseURL: "https://ai-response-validation-system-1.onrender.com/api",
});

export default API;