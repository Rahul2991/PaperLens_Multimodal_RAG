import styled, { keyframes } from "styled-components";

const spin = keyframes`
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
    `;

const typingDots = keyframes`
    0% { content: ""; }
    33% { content: "."; }
    66% { content: ".."; }
    100% { content: "..."; }
`;

export const PageContainer = styled.div`
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
`;

export const MainContainer = styled.div`
    display: flex;
    flex: 1;
    overflow: hidden;
`;

export const ChatContainer = styled.div`
    flex-grow: 1; 
    margin: 0px;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    text-align: center;
    font-family: Arial, sans-serif;
    display: flex;
    flex-direction: column;
`;

export const ChatWindow = styled.div`
    height: 75vh;
    overflow-y: auto;
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 10px;
    background-color: #f9f9f9;
    margin-bottom: 20px;
    gap: 10px;
    display: flex;
    flex-direction: column;

    /* Scrollbar styles */
    &::-webkit-scrollbar {
        width: 8px;
    }

    &::-webkit-scrollbar-thumb {
        background: #374151; /* Darker gray */
        border-radius: 4px;
    }

    &::-webkit-scrollbar-thumb:hover {
        background: #475569; /* Hover effect */
    }
    `;

export const NavBar = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 20px;
    background-color: #1f2937; /* Dark gray */
    color: white;
    position: sticky;
    top: 0;
`;

export const ProfileContainer = styled.div`
    position: relative;
    cursor: pointer;
`;

export const ProfileCircle = styled.div`
    width: 40px;
    height: 40px;
    background-color: #374151; /* Slightly lighter gray */
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
    font-weight: bold;
`;

export const DropdownMenu = styled.div.attrs((props) => ({
    isVisible: undefined,
}))`
    position: absolute;
    top: 50px;
    right: 0;
    background-color: white;
    color: black;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    padding: 10px;
    display: ${(props) => (props.isVisible ? "block" : "none")};
    z-index: 10;

    button {
        background: none;
        border: none;
        color: black;
        padding: 8px 12px;
        text-align: left;
        width: 100%;
        cursor: pointer;

        &:hover {
            background-color: #f3f4f6; /* Light gray hover effect */
        }
    }
`;

export const SpinLoaderContainer = styled.div`
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    width: 100%;
    flex-direction: column;
    `;

export const SpinLoader = styled.div`
    border: 4px solid #f3f3f3; // Light gray
    border-top: 4px solid #3498db; // Blue
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: ${spin} 1s linear infinite;
    `;

export const Message = styled.div`
    text-align: ${({ role }) => (role === "user" ? "right" : "left")};
    margin: 5px 0;
    background-color: ${({ role }) => (role === "user" ? "#d1e7ff" : "#f1f1f1")};
    padding: 10px;
    border-radius: 8px;
    display: inline-block;
    align-self: ${({ role }) => (role === "user" ? "flex-end" : "flex-start")};
    max-width: 70%;
    word-wrap: break-word;
    `;

export const InputContainer = styled.div`
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
    `;

export const MessageInput = styled.input`
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 8px;
    fontSize: 16px;
    `;

export const InputField = styled.input`
    width: 100%;
    padding: 10px;
    margin: 10px 0;
    border-radius: 4px;
    border: 1px solid #ccc;
    font-size: 16px;
    box-sizing: border-box;
    `;

export const FileInput = styled.input`
    margin-left: 10px;
    `;

export const SendButton = styled.button`
    padding: 10px 20px;
    font-size: 16px;
    border: none;
    border-radius: 5px;
    background-color: ${({ disabled }) => (disabled ? "#ccc" : "#007bff")};
    color: white;
    cursor: ${({ disabled }) => (disabled ? "not-allowed" : "pointer")};
    
    &:hover {
        background-color: ${({ disabled }) => (disabled ? "#ccc" : "#0056b3")};
    }
    `;

export const Header = styled.h1`
    font-size: 24px;
    color: #333;
    margin-bottom: 20px;
    `;

export const Button = styled.button`
    width: 100%;
    padding: 10px;
    font-size: 16px;
    border: none;
    border-radius: 5px;
    background-color: #007bff;
    color: white;
    cursor: pointer;
    margin: 10px 0;
    
    &:hover {
        background-color: #0056b3;
    }
    `;

export const Container = styled.div`
    max-width: 90%;
    width: 400px;
    margin: 0 auto;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    text-align: center;
    font-family: 'Roboto', sans-serif;
    box-sizing: border-box;
    `;

export const GoToLink = styled.p`
    margin-top: 10px;
    display: inline;
    color: #007BFF;
    text-decoration: none;
    font-size: 14px;
    cursor: pointer;

    &:hover {
        color: #0056b3;
    }`;

export const Greet = styled.span`
    font-size: 18px;
    `;

export const StatMessage = styled.p`
    margin-top: 10px;
    font-size: 14px;
    color: ${({ type }) => (type === "success" ? "green" : "red")};
    `;

export const Image = styled.img`
    max-width: 100%;
    height: auto;
    margin-top: 10px;
    border-radius: 8px;
    `;

export const LogoutButton = styled.button`
    padding: 8px 16px;
    font-size: 14px;
    border: none;
    border-radius: 5px;
    background-color: #ff4d4d;
    color: white;
    cursor: pointer;
    `;

export const TypingLoaderContainer = styled.div`
    display: flex;
    justify-content: left;
    align-items: left;
    height: 100%; // Full height of the container
    `;

export const TypingIndicator = styled.div`
    font-size: 16px;
    color: #555;
    &::after {
        content: "...";
        display: inline-block;
        animation: ${typingDots} 1s steps(3, end) infinite;
    }
`;

export const SessionSelector = styled.select`
    width: 100%;
    padding: 10px;
    margin: 10px 0;
    font-size: 16px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: #f9f9f9;
    color: #333;

    &:focus {
        outline: none;
        border-color: #007bff;
        background-color: #fff;
    }
`;

export const NewSessionButton = styled.button`
    width: 100%;
    padding: 10px;
    background-color: #3b82f6; /* Blue */
    color: #ffffff;
    font-size: 14px;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    margin-bottom: 20px;
    cursor: pointer;
    transition: background-color 0.3s ease;

    &:hover {
        background-color: #2563eb; /* Darker blue */
    }
`;

export const EmptyChat = styled.div`
    text-align: center;
    color: #999;
    font-style: italic;
    margin-top: 20px;
    `;

export const DeleteSessionBtn = styled.button`
    background: none;
    border: none;
    color: #f87171; /* Light red */
    font-size: 16px;
    cursor: pointer;
    transition: color 0.3s ease;

    &:hover {
        color: #dc2626; /* Darker red */
    }
    `;

export const SidebarContainer = styled.div.attrs((props) => ({
    isCollapsed: undefined,
}))`
    width: 250px;
    height: 90vh;
    background-color: #1f2937; /* Dark gray */
    color: #ffffff;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    padding: 20px;
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    transition: transform 0.3s ease-in-out;
    transform: ${(props) => (props.isCollapsed ? "translateX(-100%)" : "translateX(0)")};

    @media (max-width: 768px) {
        width: 250px;
    }
`;

export const SidebarToggleButton = styled.button`
    display: none;
    position: absolute;
    top: 20px;
    left: 20px;
    background-color: #1f2937;
    color: white;
    border: none;
    padding: 10px;
    cursor: pointer;
    font-size: 18px;

    @media (max-width: 768px) {
        display: block;
    }
`;

export const SidebarTitle = styled.h3`
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 20px;
    color: #60a5fa; /* Light blue */
    text-align: center;
    align-items: center;
`;

export const SessionsList = styled.div`
    flex: 1;
    width: 100%;
    overflow-y: auto;
    padding-right: 10px;

    /* Scrollbar styles */
    &::-webkit-scrollbar {
        width: 8px;
    }

    &::-webkit-scrollbar-thumb {
        background: #374151; /* Darker gray */
        border-radius: 4px;
    }

    &::-webkit-scrollbar-thumb:hover {
        background: #475569; /* Hover effect */
    }
`;

export const SessionItem = styled.div.attrs((props) => ({
    isActive: undefined, 
}))`
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: ${({ isActive }) => (isActive ? "#374151" : "#4b5563")};
    color: ${({ isActive }) => (isActive ? "#ffffff" : "#d1d5db")};
    padding: 10px 15px;
    border-radius: 8px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: background-color 0.3s ease;

    &:hover {
        background-color: #2563eb; /* Blue */
        color: #ffffff;
    }
`;

export const SessionName = styled.span`
    flex: 1;
    font-size: 14px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
`;