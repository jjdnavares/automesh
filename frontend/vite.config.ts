import path from "path"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import proxyOptions from "./proxyOptions"
import tailwindcss from "@tailwindcss/vite"
import { tanstackRouter } from "@tanstack/router-plugin/vite"

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [
		tanstackRouter({
			target: 'react',
			autoCodeSplitting: true,
		}),
		react(),
		tailwindcss(),
	],
	server: {
		port: 8080,
		host: "0.0.0.0",
		proxy: proxyOptions
	},
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "src")
		}
	},
	build: {
		outDir: "../automesh/public/frontend",
		emptyOutDir: true,
		target: "es2015",
	},
});
