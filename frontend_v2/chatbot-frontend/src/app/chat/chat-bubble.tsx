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
			className={`p-2 rounded-xl ${
				sender === "user" ? "bg-blue-300" : "text-slate-800"
			}`}
		>
			{/* <div className="text-sm">{sender}</div> */}
			<div
				className={`font-mono flex flex-col gap-4 max-w-[400px] ${
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
