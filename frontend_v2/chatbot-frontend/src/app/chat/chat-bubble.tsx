import React from "react";

interface ChatBubbleProps {
	message: string;
	sender: string;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ message, sender }) => {
	const [displayedMessage, setDisplayedMessage] = React.useState(message);

	// const indexRef = React.useRef(0); // Using ref to keep track of the current index
	// const hasBeenTyped = React.useRef(false); // Using ref to keep track of whether the message has been typed

	// React.useEffect(() => {
	// 	indexRef.current = 0; // Reset index when effect runs
	// 	setDisplayedMessage(""); // Clear displayed message when message or sender changes

	// 	if (sender !== "user" && !hasBeenTyped.current) {
	// 		const timer = setInterval(() => {
	// 			if (indexRef.current < message.length) {
	// 				setDisplayedMessage(
	// 					(prev) => prev + message.charAt(indexRef.current)
	// 				);
	// 				indexRef.current += 1;
	// 			} else {
	// 				clearInterval(timer);
	// 			}
	// 		}, 50); // Adjust the interval for faster or slower typing

	// 		return () => clearInterval(timer);
	// 	} else {
	// 		setDisplayedMessage(message);
	// 	}
	// }, [message, sender]); // Effect depends on message and sender

	return (
		<div
			className={`p-2 rounded-lg ${
				sender === "user"
					? "bg-blue-300"
					: "text-slate-800 hover:bg-slate-400 transition-all flex items-center gap-4 md:max-w-[70%]"
			}`}
		>
			{/* <div className="text-sm">{sender}</div> */}
			{sender !== "user" && (
				<span className="w-6">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						strokeWidth={1.5}
						stroke="currentColor"
						className="size-5"
					>
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z"
						/>
					</svg>
				</span>
			)}
			<div
				className={`font-mono flex flex-grow flex-col gap-4 max-w-[400px] ${
					sender === "user" ? "" : "typing-animation-container"
				}`}
			>
				{displayedMessage.split("\n").map((line, index) => (
					<div key={index} className="text-wrap">
						{line}
					</div>
				))}
			</div>
		</div>
	);
};

export default ChatBubble;
