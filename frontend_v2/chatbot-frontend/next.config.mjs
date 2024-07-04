/** @type {import('next').NextConfig} */
const nextConfig = {
	env: {
		NEXT_PUBLIC_CHAT_ENDPOINT: "ws://localhost:8765",
	},
	typescript: {
		ignoreBuildErrors: true,
	},
};

export default nextConfig;
