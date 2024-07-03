import type { Metadata } from "next";
import { Inter, Baskervville } from "next/font/google";
import "./globals.css";
import Image from "next/image";

const inter = Inter({ subsets: ["latin"] });
const baskerville = Baskervville({
	weight: "400",
	style: "normal",
	subsets: ["latin"],
});

export const metadata: Metadata = {
	title: "Atlantic Hotel - Chatbot support",
	description: "A kind of helpful chatbot for your stay in Atlantic Hotel",
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en">
			<body className={inter.className}>
				<header className="flex w-full justify-between px-8 h-20 items-center">
					<div className="flex gap-4 items-center">
						<Image
							src="/logo.png"
							alt="Logo"
							width={64}
							height={64}
						/>
						<span className={`${baskerville.className} text-xl`}>
							Atlantic Hotel
						</span>
					</div>
					<nav className={`${baskerville.className}`}>
						<ul className="flex justify-between gap-4">
							<li>
								<a href="/">Home</a>
							</li>
							<li>
								<a href="/chat">Chatbot Support</a>
							</li>
						</ul>
					</nav>
				</header>
				{children}
			</body>
		</html>
	);
}
