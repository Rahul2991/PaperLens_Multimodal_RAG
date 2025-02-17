import { SidebarToggleButton, SidebarContainer, NewSessionButton, SidebarList, SidebarItem, SessionName, DeleteSessionBtn, SideBarGoToBtn } from "./StyleComponents";
import { createChatSession, deleteSession, fetchChatSessions } from "../api";
import React, { useState } from "react";

const Sidebar = ({ sessions, setSessions, activeSessionId, setActiveSessionId, setMessages, setChatLoading, setStatMessage, handleDashboard, handleError }) => {
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

    const toggleSidebar = () => setIsSidebarCollapsed(!isSidebarCollapsed);

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

    return (
        <>
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
        </>
    );
};

export default Sidebar;