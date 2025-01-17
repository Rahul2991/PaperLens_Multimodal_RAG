import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchChat, fetchChatBotResponse } from "../api";

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchUserName = async () => {
            const user = localStorage.getItem("username");
            setUsername(user || "User");
            // await fetchChatData();
        };
        fetchUserName();
    }, []);

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        navigate("/login");
    };

    const fetchChatData = async (message) => {
        try {
            const response = await fetchChatBotResponse(message);
            const systemResponse = {
                    role: "system",
                    text: response.data.message,
                };
            setMessages((prev) => [...prev, systemResponse])
            // setMessages([{ role: "system", text: response.data.message }]);
        } catch (error) {
            handleError(error);
        }
    };

    const handleError = (error) => {
        if (error.response?.status === 401) {
            setError("Session expired. Redirecting to login...");
            setTimeout(() => handleLogout(), 2000);
        } else {
            setError("An error occurred while connecting to the chat.");
            console.error("Chat error:", error);
        }
    };

    const handleSend = async () => {
        if (!input.trim()) return;
        const userMessage = { role: "user", text: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput(""); // Clear input

        await fetchChatData(input);

        // Simulate a chat response (replace this with your LLM API call)
        // const systemResponse = {
        //     role: "system",
        //     text: `You said: ${input}`,
        // };
        // setTimeout(() => setMessages((prev) => [...prev, systemResponse]), 1000);
    };

    // const getChat = async () => {
    //     try {
    //         const response = await fetchChat();
    //         setMessage(response.data.message);
    //     } catch (error) {
    //         if (error.response && error.response.status === 401) {
    //             setError("Token expired, logging out...");
    //             setTimeout(() => {
    //                 handleLogout();
    //             }, 2000);
    //         } else {
    //             console.error("Failed to fetch chat", error);
    //             setError("An error occurred while fetching chat.");
    //         }
    //     }
    // };

    const styles = {
        container: {
            fontFamily: "Arial, sans-serif",
            padding: "20px",
            maxWidth: "600px",
            margin: "0 auto",
            border: "1px solid #ddd",
            borderRadius: "8px",
            boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
            textAlign: "center",
        },
        navbar: {
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "10px 20px",
            backgroundColor: "#007bff",
            color: "white",
            borderRadius: "8px",
            marginBottom: "20px",
        },
        username: {
            fontSize: "18px",
        },
        logoutButton: {
            padding: "8px 16px",
            fontSize: "14px",
            border: "none",
            borderRadius: "5px",
            backgroundColor: "#ff4d4d",
            color: "white",
            cursor: "pointer",
        },
        header: {
            fontSize: "24px",
            color: "#333",
            marginBottom: "20px",
        },
        chatWindow: {
            display: "flex",
            flexDirection: "column",
            gap: "10px",
            height: "300px",
            overflowY: "auto",
            padding: "10px",
            border: "1px solid #ddd",
            borderRadius: "5px",
            backgroundColor: "#f9f9f9",
            marginBottom: "20px",
        },
        message: {
            padding: "10px",
            borderRadius: "5px",
            maxWidth: "70%",
            wordWrap: "break-word",
        },
        inputContainer: {
            display: "flex",
            gap: "10px",
            marginBottom: "10px",
        },
        input: {
            flex: 1,
            padding: "10px",
            fontSize: "16px",
            borderRadius: "5px",
            border: "1px solid #ddd",
        },
        sendButton: {
            padding: "10px 20px",
            fontSize: "16px",
            border: "none",
            borderRadius: "5px",
            backgroundColor: "#007bff",
            color: "white",
            cursor: "pointer",
        },
        errorText: {
            color: "red",
            marginBottom: "10px",
        },
    };

    return (
        <div style={styles.container}>

            <div style={styles.navbar}>
                <span style={styles.username}>Welcome, {username}!</span>
                <button style={styles.logoutButton} onClick={handleLogout}>
                    Logout
                </button>
            </div>

            <h1 style={styles.header}>Multimodal Chat Interface</h1>

            <div style={styles.chatWindow}>
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        style={{
                            ...styles.message,
                            alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                            backgroundColor: msg.role === "user" ? "#d1e7ff" : "#f1f1f1",
                        }}
                    >
                        {msg.text}
                    </div>
                ))}
            </div>

            <div style={styles.inputContainer}>
                <input
                    type="text"
                    style={styles.input}
                    placeholder="Type a message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                />
                <button style={styles.sendButton} onClick={handleSend}>
                    Send
                </button>
            </div>

            {error && <p style={styles.errorText}>{error}</p>}
            {/* <button style={styles.logoutButton} onClick={handleLogout}>Logout</button> */}
        </div>
    );
};

export default Chat;