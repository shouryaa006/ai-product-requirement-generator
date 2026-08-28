import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export async function generatePRD(productIdea) {
  const response = await api.post("/api/v1/prd/generate", {
    product_idea: productIdea,
  });

  console.log("FULL PRD API RESPONSE:", response.data);

  return response.data;
}