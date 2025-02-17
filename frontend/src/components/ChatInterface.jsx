import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";
import { ChatContainer } from "./StyleComponents";
import React, { useState } from "react";


const ChatInterface = ({ messages, setMessages, chatLoading, activeSessionId, setActiveSessionId, setSessions, handleError }) => {
    const [loading, setLoading] = useState(false);
    
    return (
        <ChatContainer>
            <ChatWindow chatLoading={chatLoading} loading={loading} messages={messages} />
            <ChatInput 
                loading={loading}
                setLoading={setLoading}
                setMessages={setMessages}
                activeSessionId={activeSessionId}
                setActiveSessionId={setActiveSessionId}
                setSessions={setSessions}
                handleError={handleError}
            />
        </ChatContainer>
    );
};

export default ChatInterface;