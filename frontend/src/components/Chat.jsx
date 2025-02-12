import React, { useEffect, useRef, useState } from "react";
import { FaPaperclip } from "react-icons/fa";
import ReactMarkdown from "react-markdown";
import { useNavigate } from "react-router-dom";
import { createChatSession, deleteSession, fetchChatBotResponse, fetchChatSessions } from "../api";
import { ChatContainer, ChatWindow, FileInput, MessageInput, InputContainer, Message, NavBar, SendButton, StatMessage, Image, TypingIndicator, TypingLoaderContainer, NewSessionButton, EmptyChat, SpinLoader, DeleteSessionBtn, SidebarContainer, SidebarList, SidebarItem, SessionName, MainContainer, ProfileContainer, ProfileCircle, DropdownMenu, PageContainer, SidebarToggleButton, SpinLoaderContainer, AttachmentButtonWrapper, SideBarGoToBtn, RagModeSelect } from "./StyleComponents";

const Chat = () => {
    const [sessions, setSessions] = useState([]);
    const [activeSessionId, setActiveSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [userAdmin, setUserAdmin] = useState(false);
    const [statMessage, setStatMessage] = useState({ text: "", type: "" });
    const [image, setImage] = useState(null);
    const [loading, setLoading] = useState(false);
    const [chatLoading, setChatLoading] = useState(false);
    const chatEndRef = useRef(null);
    const [dropdownVisible, setDropdownVisible] = useState(false);
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
    const chatWindowRef = useRef(null);
    const dropdownRef = useRef(null);
    const [ragMode, setRagMode] = useState("all");

    useEffect(() => {
        if (chatEndRef.current && chatWindowRef.current) {
            chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
        }
    }, [messages]);

    useEffect(() => {
        const fetchInitialData = async () => {
            const user = localStorage.getItem("username");
            setUsername(user || "User");
            const is_admin = localStorage.getItem("is_admin") === "true";
            setUserAdmin(is_admin);
            console.log("is_admin", is_admin);
            try {
                const { data } = await fetchChatSessions();
                setSessions(data.sessions);
            } catch (error) {
                handleError(error);
            }
        };
        fetchInitialData();
    }, []);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setDropdownVisible(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    const toggleDropdown = () => setDropdownVisible((prev) => !prev);

    const toggleSidebar = () => setIsSidebarCollapsed(!isSidebarCollapsed);

    const handleLogout = () => {
        console.log('logout');
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        localStorage.removeItem("is_admin");
        navigate("/login");
    };

    const handleError = (error) => {
        if (error.response?.status === 401) {
            setStatMessage({ text: "Session expired. Redirecting to login...", type: "error" });
            setTimeout(() => handleLogout(), 2000);
        } else {
            setStatMessage({ text: "An error occurred while connecting to the chat.", type: "error" });
            console.error("Chat error:", error);
            setTimeout(() => setStatMessage({ text: "", type: "" }), 2000);
        }

    };

    const handleSend = async () => {
        let session_id = activeSessionId;
        if (!input.trim() && !image) return;
        if (!activeSessionId) {
            // setStatMessage({ text: "Please select or create a session first.", type: "error" });
            // return;
            const { data } = await createChatSession();
            setSessions((prev) => [...prev, { session_id: data.session_id, messages_count: 0, messages: [] }]);
            setActiveSessionId(data.session_id);
            session_id = data.session_id;
        }
        const userMessage = { role: "user", text: input, image: image ? URL.createObjectURL(image) : null, };
        setMessages((prev) => [...prev, userMessage]);

        setInput("");
        setImage(null);
        setLoading(true);

        try {
            const formData = new FormData();
            formData.append("message", input);
            formData.append("session_id", session_id);
            formData.append("rag_mode", ragMode)
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
            document.getElementById("file-upload").value = "";
            setLoading(false);
        }
    };

    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (file) {
            console.log("Uploaded file:", file.name);  // File name
            console.log("File type:", file.type);     // MIME type (e.g., image/png, application/pdf)
            console.log("File size:", file.size);     // File size in bytes
        } else {
            console.log("No file selected.");
        }
        // setImage(event.target.files[0]);
    };

    const handleNewSession = async () => {
        try {
            const { data } = await createChatSession();
            console.log("data", data.session_id);
            setSessions((prev) => [...prev, { session_id: data.session_id, messages_count: 0, messages: [] }]);
            setActiveSessionId(data.session_id);
            setMessages([]); // Clear chat for the new session
            console.log("session_id", activeSessionId);
        } catch (error) {
            handleError(error);
        }
    };

    const handleSessionChange = async (sessionId) => {
        setChatLoading(true);
        setActiveSessionId(sessionId);
        try {
            const { data } = await fetchChatSessions();
            setSessions(data.sessions);
        } catch (error) {
            handleError(error);
        }
        const selectedSession = sessions.find((s) => s.session_id === sessionId);
        console.log("selectedSession:", selectedSession);

        postProcessMessages(selectedSession);

        setChatLoading(false);
    };

    const postProcessMessages = (selectedSession) => {
        console.log("postProcessMessages:", selectedSession?.messages)
        const transformedMessages = (selectedSession?.messages || [])
            .filter((msg) => msg.role !== "system") // Remove 'system' messages
            .map((msg) => ({
                role: msg.role === "assistant" ? "bot" : msg.role, // Map roles
                text: msg.content || msg.text, // Map 'content' to 'text'
                image: msg.image || null,
            }));
        console.log("transformedMessages:", transformedMessages);
        setMessages(transformedMessages || []);
    }

    const handleDeleteSession = async (sessionId) => {
        try {
            const response = await deleteSession(sessionId)
            if (response.status === 200) {
                setSessions((prev) => prev.filter((session) => session.session_id !== sessionId));
                setMessages([]); // Clear messages if the deleted session was active
                setActiveSessionId(null); // Clear the selected session
                setStatMessage({ text: "Session deleted successfully!", type: "success" })
            }
        } catch (error) {
            handleError(error)
        }
    };

    const handleDashboard = () => {
        userAdmin ? navigate('/admin') : navigate('/user');
    }

    return (
        <PageContainer >
            <NavBar>
                <h3>Multimodal Chat Interface</h3>
                <ProfileContainer ref={dropdownRef} onClick={toggleDropdown} tabIndex={0}>
                    <ProfileCircle>{username.charAt(0).toUpperCase()}</ProfileCircle>
                    {dropdownVisible && (
                        <DropdownMenu>
                            <button onClick={handleDashboard}>Dashboard</button>
                            <button onClick={handleLogout}>Logout</button>
                        </DropdownMenu>
                    )}
                </ProfileContainer>
            </NavBar>
            <MainContainer>
                <SidebarToggleButton onClick={toggleSidebar}>
                    {isSidebarCollapsed ? ">" : "<"}
                </SidebarToggleButton>
                <SidebarContainer isCollapsed={isSidebarCollapsed}>
                    <NewSessionButton onClick={handleNewSession}>Start New Session</NewSessionButton>
                    <SidebarList>
                        {sessions.length === 0 ? (
                            <p>No sessions available.</p>
                        ) : (sessions.map((session) => (
                            <SidebarItem
                                key={session.session_id}
                                isActive={session.session_id === activeSessionId}
                                onClick={() => handleSessionChange(session.session_id)}
                            >
                                <SessionName>{session.session_id}</SessionName>
                                <DeleteSessionBtn
                                    onClick={(e) => {
                                        e.stopPropagation(); // Prevent triggering session selection
                                        const confirmDelete = window.confirm(
                                            "Are you sure you want to delete this session?"
                                        );
                                        if (confirmDelete) handleDeleteSession(session.session_id);
                                    }}
                                >
                                    🗑️
                                </DeleteSessionBtn>
                            </SidebarItem>)))
                        }
                    </SidebarList>
                    <SideBarGoToBtn onClick={handleDashboard}>Dashboard</SideBarGoToBtn>
                </SidebarContainer>
                <ChatContainer>
                    <ChatWindow ref={chatWindowRef}>
                        {chatLoading ? (
                            <SpinLoaderContainer>
                                <SpinLoader />
                                <br />
                                Loading messages...
                            </SpinLoaderContainer>
                        ) : messages.length > 0 ? (messages.map((msg, index) => (
                            <Message key={index} role={msg.role}>
                                {msg.image && <Image src={msg.image} alt="Attachment" />}
                                <ReactMarkdown>{msg.text}</ReactMarkdown>
                            </Message>
                        ))) : <EmptyChat>No messages in this session yet. Start the conversation!</EmptyChat>
                        }
                        {loading && (
                            <TypingLoaderContainer>
                                <TypingIndicator> Bot is typing </TypingIndicator>
                            </TypingLoaderContainer>
                        )}
                        <div ref={chatEndRef} />
                    </ChatWindow>
                    <InputContainer>
                        <>
                            <FileInput
                                type="file"
                                accept=".png,.jpg,.jpeg,.pdf,.txt" // Supported file types
                                onChange={handleFileUpload}
                                id="file-upload"
                                disabled={loading}
                            />
                            <AttachmentButtonWrapper htmlFor="file-upload" disabled={loading}>
                                <FaPaperclip size={18} />
                            </AttachmentButtonWrapper>
                        </>
                        <MessageInput
                            type="text"
                            placeholder="Type a message..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            disabled={loading}
                        />
                        <SendButton onClick={handleSend} disabled={loading}> Send </SendButton>
                        <RagModeSelect value={ragMode} onChange={(e) => setRagMode(e.target.value)} disabled={loading}>
                            <option value="user">User Data Only</option>
                            <option value="all">All Data (Admin + User)</option>
                            <option value="no-rag">Direct Chatbot Response</option>
                        </RagModeSelect>
                    </InputContainer>
                    {statMessage.text && <StatMessage type={statMessage.type}>{statMessage.text}</StatMessage>}
                </ChatContainer>
            </MainContainer>
        </PageContainer >
    );
};

export default Chat;