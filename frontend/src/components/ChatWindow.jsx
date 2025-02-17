import { ChatWindowContainer, SpinLoaderContainer, SpinLoader, Message, EmptyChat, TypingLoaderContainer, TypingIndicator, Image } from "../components/StyleComponents";
import React, { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

const ChatWindow = ({ chatLoading, loading, messages }) => {
    const chatWindowRef = useRef(null);
    const chatEndRef = useRef(null);

    useEffect(() => {
        if (chatEndRef.current && chatWindowRef.current) {
            chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
        }
    }, [messages]);

    return (
        <ChatWindowContainer ref={chatWindowRef}>
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
        </ChatWindowContainer>
    );
};

export default ChatWindow;