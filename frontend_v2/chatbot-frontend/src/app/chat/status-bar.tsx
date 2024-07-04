"use client";

import { connect } from "http2";
import React from "react";

interface StatusBarProps {
	// Add your component props here
	connected: boolean;
}

const StatusBar: React.FC<StatusBarProps> = ({
	/* Destructure your props here */
	connected,
}) => {
	// Add your component logic here
	return (
		<div
			className={`p-1 text-[10px] rounded-xl ${
				connected
					? "bg-green-200 text-green-500"
					: "bg-red-200 text-red-500"
			}`}
		>
			{connected ? "Connected" : "Disconnected"}
		</div>
	);
};

export default StatusBar;
