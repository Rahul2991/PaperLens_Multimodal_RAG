import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchChat, fetchChatBotResponse } from "../api";
import { ChatContainer, ChatWindow, FileInput, Header, MessageInput, InputContainer, Loader, LoaderContainer, Message, NavBar, SendButton, Greet, StatMessage, Image, LogoutButton } from "./StyleComponents";

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [statMessage, setStatMessage] = useState({ text: "", type: "" });
    const [image, setImage] = useState(null);
    const [loading, setLoading] = useState(false);

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

    const handleError = (error) => {
        if (error.response?.status === 401) {
            setStatMessage({text: "Session expired. Redirecting to login...", type: "error" });
            setTimeout(() => handleLogout(), 2000);
        } else {
            setStatMessage({text: "An error occurred while connecting to the chat.", type: "error" });
            console.error("Chat error:", error);
        }
    };

    const handleSend = async () => {
        if (!input.trim() && !image) return;
        const userMessage = { role: "user", text: input, image: image ? URL.createObjectURL(image) : null, };
        setMessages((prev) => [...prev, userMessage]);

        setInput("");
        setImage(null);

        try {
            const formData = new FormData();
            formData.append("message", input);
            if (image) formData.append("image", image);

            const response = await fetchChatBotResponse(formData);

            const botMessage = {
                role: "bot",
                text: response.data.message,
                image: response.data.image || null,
            };
            setMessages((prev) => [...prev, botMessage]);
        }
        catch (error) {
            handleError(error);
        } finally {
            setLoading(false);
        }
    };

    const handleImageChange = (event) => {
        setImage(event.target.files[0]);
    };

    return (
        <ChatContainer>

            <NavBar>
                <Greet>Welcome, {username}!</Greet>
                <LogoutButton onClick={handleLogout}> Logout </LogoutButton>
            </NavBar>

            <Header>Multimodal Chat Interface</Header>

            <ChatWindow>
                {messages.map((msg, index) => (
                    <Message key={index} role={msg.role}>
                        {msg.image && <Image src={msg.image} alt="Attachment"/>}
                        {msg.text}
                    </Message>
                ))}
                {loading && (
                    <LoaderContainer>
                        <Loader />
                    </LoaderContainer>
                )}
            </ChatWindow>

            <InputContainer>
                <FileInput type="file" accept="image/*" onChange={handleImageChange} />
                <MessageInput
                    type="text"
                    placeholder="Type a message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                />
                <SendButton onClick={handleSend}> Send </SendButton>
            </InputContainer>

            {statMessage.text && <StatMessage type={statMessage.type}>{statMessage.text}</StatMessage>}
        </ChatContainer>
    );
};

export default Chat;