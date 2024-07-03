"use client";
import React from "react";
import StatusBar from "./status-bar";
import ChatBubble from "./chat-bubble";

interface ChatProps {
	// Add your component props here
}

type Message = {
	type: "message";
	text: string;
	author: string;
};

type StateUpdate = {
	type: "state_update";
	key: string;
	value: string;
};

const Chat: React.FC<ChatProps> = (
	{
		/* Destructure your props here */
	}
) => {
	// Add your component logic here
	const [messages, setMessages] = React.useState<Message>([]);

	const [isConnected, setIsConnected] = React.useState(false);

	const [conversationIntent, setConversationIntent] =
		React.useState("No Intent");

	const [inputValue, setInputValue] = React.useState("");
	const ws = React.useRef<WebSocket | null>(null);
	const chatMessagesRef = React.useRef<HTMLUListElement | null>(null);
	// React.useEffect(() => {
	// 	chatMessagesRef.current?.scrollTo({
	// 		top: chatMessagesRef.current.scrollHeight,
	// 		behavior: "smooth",
	// 	});
	// }, [messages]);

	React.useEffect(() => {
		// Replace 'ws://example.com/socket' with your WebSocket connection URL
		ws.current = new WebSocket(process.env.NEXT_PUBLIC_CHAT_ENDPOINT);

		ws.current.onopen = () => {
			console.log("WebSocket Connected");
			setIsConnected(true);
			// You can send messages to the server here using ws.send()
		};

		ws.current.onmessage = (event) => {
			// Handle incoming messages
			console.log("Message from server ", event.data);
			let message: Message | StateUpdate = JSON.parse(event.data);

			if (message.type === "state_update") {
				switch (message.key) {
					case "intent":
						setConversationIntent(message.value);
						break;
					default:
						break;
				}
				return;
			}

			setMessages((prev) => [...prev, message]);
		};

		ws.current.onerror = (error) => {
			// Handle errors
			console.error("WebSocket Error ", error);
		};

		ws.current.onclose = () => {
			// Handle connection closed
			setConversationIntent("No Intent");
			setIsConnected(false);
			console.log("WebSocket Disconnected");
		};

		// Clean up function to close the WebSocket connection when the component unmounts
		return () => {
			setConversationIntent("No Intent");
			setIsConnected(false);
			ws.current.close();
		};
	}, []); // Empty dependency array means this effect runs only once on mount

	const handleSubmit = (event) => {
		event.preventDefault();
		if (inputValue === "") return;

		if (ws.current && ws.current.readyState === WebSocket.OPEN) {
			let message: Message = {
				text: inputValue,
				author: "user",
			};
			ws.current.send(JSON.stringify(message));
			setMessages((prev) => [...prev, message]);

			setInputValue(""); // Clear the input after sending
		}
	};

	const forceReset = () => {
		console.log("resetting");
		if (ws.current && ws.current.readyState === WebSocket.OPEN) {
			console.log("sending reset");
			ws.current.send(
				JSON.stringify({
					force_action: "reset",
					type: "message",
					author: "user",
					text: "",
				})
			);
		}
	};

	return (
		<section className="min-h-[80dvh] h-[80dvh] bg-slate-300 flex">
			<div className="flex flex-col max-w-[1000px] w-full mx-auto justify-end p-12">
				<section
					id="chat-messages"
					className="w-full max-h-[100%] text-slate-600 overflow-y-auto"
				>
					<ul
						ref={chatMessagesRef}
						className="flex justify-end flex-col gap-2"
					>
						{messages.map((message, index) => (
							<li
								key={index}
								className={`flex ${
									message.author === "user"
										? "justify-end"
										: "justify-start"
								}`}
							>
								{/* <b
									className={`mr-2 ${
										message.author === "user"
											? "text-blue-500"
											: "text-purple-500"
									}`}
								>
									{message.author}:
								</b> */}
								<ChatBubble
									key={`msg-${index}`}
									message={message.text}
									sender={message.author}
								/>
								{/* <span
									className={`p-2 rounded-xl ${
										message.author === "user"
											? "bg-blue-300"
											: "text-slate-100"
									}`}
								>
									{message.text}
								</span> */}
								{/* <span className="text-sm text-gray-200">
									{JSON.stringify(message)}
								</span> */}
							</li>
						))}
					</ul>
				</section>
				<div className="mx-auto w-full mb-4 mt-8">
					<div className="flex justify-between gap-2 items-center">
						<span>
							current workflow: <b>{conversationIntent}</b>
						</span>
						<button
							className="bg-red-100 text-red-700 p-2 rounded-xl "
							onClick={() => forceReset()}
						>
							reset conversation
						</button>
					</div>
					<form className="flex" onSubmit={handleSubmit}>
						<input
							onChange={(e) => setInputValue(e.target.value)}
							value={inputValue}
							type="text"
							className="w-full rounded-l-xl p-4 bg-slate-600 placeholder-slate-100 placeholder-opacity-60 text-slate-100"
							placeholder="Type a message..."
						/>
						<button
							className="bg-blue-500 text-white rounded-r-xl p-2 px-4"
							type="submit"
							// disabled={inputValue !== ""}
						>
							Send
						</button>
					</form>
				</div>
				<StatusBar connected={isConnected} />
			</div>
		</section>
	);
};

export default Chat;
