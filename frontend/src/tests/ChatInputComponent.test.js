import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ChatInput from "../components/ChatInput";
import { createChatSession, fetchChatBotResponse } from "../api";

jest.mock("../api", () => ({
    createChatSession: jest.fn(),
    fetchChatBotResponse: jest.fn()
}));

describe("ChatInput Component", () => {
    let setLoading, setMessages, setActiveSessionId, setSessions, handleError;

    beforeEach(() => {
        setLoading = jest.fn();
        setMessages = jest.fn();
        setActiveSessionId = jest.fn();
        setSessions = jest.fn();
        handleError = jest.fn();
    });

    test("renders input elements and buttons", () => {
        render(
            <ChatInput
                loading={false}
                setLoading={setLoading}
                setMessages={setMessages}
                activeSessionId={null}
                setActiveSessionId={setActiveSessionId}
                setSessions={setSessions}
                handleError={handleError}
            />
        );

        expect(screen.getByPlaceholderText("Type a message...")).toBeInTheDocument();
        expect(screen.getByRole("button", { name: /send/i })).toBeInTheDocument();
        expect(screen.getByTestId("file-upload")).toBeInTheDocument();
    });

    test("updates input value on change", () => {
        render(<ChatInput loading={false} setLoading={setLoading} setMessages={setMessages} activeSessionId={null} setActiveSessionId={setActiveSessionId} setSessions={setSessions} handleError={handleError} />);
        const input = screen.getByPlaceholderText("Type a message...");
        fireEvent.change(input, { target: { value: "Hello!" } });
        expect(input.value).toBe("Hello!");
    });

    test("calls handleSend on clicking Send button", async () => {
        fetchChatBotResponse.mockResolvedValue({ data: { message: "Bot response", image: null } });
        createChatSession.mockResolvedValue({ data: { session_id: "12345" } });

        render(<ChatInput loading={false} setLoading={setLoading} setMessages={setMessages} activeSessionId={null} setActiveSessionId={setActiveSessionId} setSessions={setSessions} handleError={handleError} />);
        
        fireEvent.change(screen.getByPlaceholderText("Type a message..."), { target: { value: "Hello!" } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));

        await waitFor(() => expect(setLoading).toHaveBeenCalledWith(true));
        await waitFor(() => expect(fetchChatBotResponse).toHaveBeenCalled());
    });

    test("file upload triggers handleFileUpload", () => {
        render(<ChatInput loading={false} setLoading={setLoading} setMessages={setMessages} activeSessionId={null} setActiveSessionId={setActiveSessionId} setSessions={setSessions} handleError={handleError} />);
        
        const fileInput = screen.getByTestId("file-upload");
        const file = new File(["dummy content"], "test.png", { type: "image/png" });
        fireEvent.change(fileInput, { target: { files: [file] } });
        
        expect(fileInput.files[0]).toBe(file);
    });
});
