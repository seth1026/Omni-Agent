import axios from 'axios';

// Use environment variable if deployed, otherwise fallback to local backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface PlanTrace {
  plan: {
    requires_clarification: boolean;
    clarification_message?: string;
    tool_plan: string[];
    reasoning: string;
  };
  executed_tools: any[];
  overall_status: string;
  total_execution_time_ms: number;
  final_response: string;
}

export interface ChatResponse {
  response: string;
  trace: PlanTrace;
}

export const uploadFiles = async (files: File[]): Promise<string[]> => {
  const formData = new FormData();
  files.forEach(f => formData.append('files', f));
  
  const res = await axios.post(`${API_BASE_URL}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data.urls;
};

export const sendMessage = async (message: string, fileUrls?: string[]): Promise<ChatResponse> => {
  const res = await axios.post(`${API_BASE_URL}/chat`, {
    message,
    file_urls: fileUrls
  });
  return res.data;
};
