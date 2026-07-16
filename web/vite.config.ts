import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/health": "http://localhost:8000",
      "/chat": "http://localhost:8000",
      "/metrics": "http://localhost:8000",
      "/providers": "http://localhost:8000",
      "/tracks": "http://localhost:8000",
      "/config": "http://localhost:8000",
    },
  },
  build: {
    outDir: "dist",
  },
});
