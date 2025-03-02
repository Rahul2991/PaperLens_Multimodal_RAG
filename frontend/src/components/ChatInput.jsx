import { FaPaperclip } from "react-icons/fa";
import { InputContainer, FileInput, AttachmentButtonWrapper, MessageInput, SendButton, RagModeSelect } from "../components/StyleComponents";
import React, { useState } from "react";
import { createChatSession, fetchChatBotResponse } from "../api";


const ChatInput = ({ loading, setLoading, setMessages, activeSessionId, setActiveSessionId, setSessions, handleError }) => {
    const [image, setImage] = useState(null);
    const [input, setInput] = useState("");
    const [ragMode, setRagMode] = useState("all");

    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (file) {
            console.log("Uploaded file:", file.name);  // File name
            console.log("File type:", file.type);     // MIME type (e.g., image/png, application/pdf)
            console.log("File size:", file.size);     // File size in bytes
        } else {
            console.log("No file selected.");
        }
        setImage(event.target.files[0]);
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

    return (
        <InputContainer>
            <>
                <FileInput
                    type="file"
                    accept=".png,.jpg,.jpeg" // Supported file types
                    onChange={handleFileUpload}
                    id="file-upload"
                    data-testid="file-upload" 
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
                <option value="all">All Data (Admin)</option>
                <option value="no-rag">Direct Chatbot Response</option>
            </RagModeSelect>
        </InputContainer>
    );
};

export default ChatInput;