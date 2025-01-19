import styled, { keyframes } from "styled-components";

const spin = keyframes`
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
    `;

export const ChatContainer = styled.div`
    max-width: 1800px;
    margin: auto;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    text-align: center;
    font-family: Arial, sans-serif;
`;

export const ChatWindow = styled.div`
    height: 70vh;
    overflow-y: auto;
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 10px;
    background-color: #f9f9f9;
    margin-bottom: 20px;
    gap: 10px;
    display: flex;
    flex-direction: column;
    `;

export const NavBar = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px;
    background-color: #000;
    color: white;
    border-radius: 8px;
    margin-bottom: 20px;
`;

export const LoaderContainer = styled.div`
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%; // Full height of the container
    `;

export const Loader = styled.div`
    border: 4px solid #f3f3f3; // Light gray
    border-top: 4px solid #3498db; // Blue
    border-radius: 50%;
    width: 40px; // Adjust size as needed
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
    background-color: #007bff;
    color: white;
    cursor: pointer;
    
    &:hover {
        background-color: #0056b3;
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

export const Image = styled.image`
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