import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchChatSessions } from "../api";
import { MainContainer, PageContainer } from "../components/StyleComponents";
import NotificationModal from "../components/NotificationModal";
import ChatInterface from "../components/ChatInterface";
import Sidebar from "../components/Sidebar";
import NavigationBar from "../components/NavigationBar";

const Chat = () => {
    const [sessions, setSessions] = useState([]);
    const [activeSessionId, setActiveSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [username, setUsername] = useState("");
    const [userAdmin, setUserAdmin] = useState(false);
    const [statMessage, setStatMessage] = useState({ text: "", type: "" });
    const [chatLoading, setChatLoading] = useState(false);
    const navigate = useNavigate();
    
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

    const handleDashboard = () => {
        userAdmin ? navigate('/admin') : navigate('/user');
    }

    return (
        <PageContainer >
            <NavigationBar 
                username={username}
                handleDashboard={handleDashboard}
                handleLogout={handleLogout}
            />
            <MainContainer>
                <Sidebar
                    sessions={sessions}
                    setSessions={setSessions}
                    activeSessionId={activeSessionId}
                    setActiveSessionId={setActiveSessionId}
                    setMessages={setMessages}
                    setChatLoading={setChatLoading}
                    setStatMessage={setStatMessage}
                    handleDashboard={handleDashboard}
                    handleError={handleError}
                />
                <ChatInterface
                    messages={messages}
                    setMessages={setMessages}
                    chatLoading={chatLoading}
                    activeSessionId={activeSessionId}
                    setActiveSessionId={setActiveSessionId}
                    setSessions={setSessions}
                    handleError={handleError}
                />
            </MainContainer>
            <NotificationModal message={statMessage.text} type={statMessage.type} onConfirm={() => { }} />
        </PageContainer >
    );
};

export default Chat;