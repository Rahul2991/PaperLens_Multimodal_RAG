import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createChatSession, fetchChatBotResponse, fetchChatSessions } from "../api";
import { ChatContainer, ChatWindow, FileInput, Header, MessageInput, InputContainer, Message, NavBar, SendButton, Greet, StatMessage, Image, LogoutButton, TypingIndicator, TypingLoaderContainer, SessionSelector, NewSessionButton } from "./StyleComponents";

const Chat = () => {
    const [sessions, setSessions] = useState([]);
    const [activeSessionId, setActiveSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [statMessage, setStatMessage] = useState({ text: "", type: "" });
    const [image, setImage] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchInitialData  = async () => {
            const user = localStorage.getItem("username");
            setUsername(user || "User");
            try {
                const { data } = await fetchChatSessions();
                setSessions(data.sessions);
                if (data.sessions.length > 0) {
                    setActiveSessionId(data.sessions[0].session_id); // Default to the first session
                }
            } catch (error) {
                handleError(error);
            }
        };
        fetchInitialData ();
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
        if (!activeSessionId) {
            setStatMessage({ text: "Please select or create a session first.", type: "error" });
            return;
        }
        const userMessage = { role: "user", text: input, image: image ? URL.createObjectURL(image) : null, };
        setMessages((prev) => [...prev, userMessage]);

        setInput("");
        setImage(null);
        setLoading(true);

        try {
            const formData = new FormData();
            formData.append("message", input);
            formData.append("session_id", activeSessionId);
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

    const handleNewSession = async () => {
        try {
            const { data } = await createChatSession();
            setSessions((prev) => [...prev, { session_id: data.session_id, messages_count: 0 }]);
            setActiveSessionId(data.session_id);
            setMessages([]); // Clear chat for the new session
        } catch (error) {
            handleError(error);
        }
    };

    const handleSessionChange = (sessionId) => {
        setActiveSessionId(sessionId);
        const selectedSession = sessions.find((s) => s.session_id === sessionId);
        console.log(selectedSession);

        const transformedMessages = selectedSession?.messages
            .filter((msg) => msg.role !== "system") // Remove 'system' messages
            .map((msg) => ({
                role: msg.role === "assistant" ? "bot" : msg.role, // Map roles
                text: msg.content, // Map 'content' to 'text'
                image: msg.image || null,
        }));

        setMessages(transformedMessages || []);
    };

    // const loadSession = async (sessionId) => {
    //     try {
    //         const response = await fetch(`/api/sessions/${sessionId}`, {
    //             headers: {
    //                 Authorization: `Bearer ${localStorage.getItem("token")}`,
    //             },
    //         });
    //         const data = await response.json();
    //         setMessages(data.session.messages);
    //         setActiveSessionId(sessionId);
    //     } catch (error) {
    //         console.error("Error loading session:", error);
    //     }
    // };

    return (
        <ChatContainer>

            <NavBar>
                <Greet>Welcome, {username}!</Greet>
                <LogoutButton onClick={handleLogout}> Logout </LogoutButton>
            </NavBar>

            <Header>Multimodal Chat Interface</Header>

            <SessionSelector
                value={activeSessionId || ""}
                onChange={(e) => handleSessionChange(e.target.value)}
            >
                <option value="" disabled>
                    Select a session
                </option>
                {sessions.map((session) => (
                    <option key={session.session_id} value={session.session_id}>
                        Session {session.session_id} ({session.messages_count} messages)
                    </option>
                ))}
            </SessionSelector>

            <NewSessionButton onClick={handleNewSession}>Start New Session</NewSessionButton>

            <ChatWindow>
                {messages.map((msg, index) => (
                    <Message key={index} role={msg.role}>
                        {msg.image && <Image src={msg.image} alt="Attachment"/>}
                        {msg.text}
                    </Message>
                ))}
                {loading && (
                    <TypingLoaderContainer>
                        <TypingIndicator> Bot is typing </TypingIndicator>
                    </TypingLoaderContainer>
                )}
            </ChatWindow>

            <InputContainer>
                <FileInput type="file" accept="image/*" onChange={handleImageChange} disabled={loading} />
                <MessageInput
                    type="text"
                    placeholder="Type a message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={loading}
                />
                <SendButton onClick={handleSend} disabled={loading}> Send </SendButton>
            </InputContainer>

            {statMessage.text && <StatMessage type={statMessage.type}>{statMessage.text}</StatMessage>}
        </ChatContainer>
    );
};

export default Chat;