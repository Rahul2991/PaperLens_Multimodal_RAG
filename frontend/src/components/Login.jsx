// Login.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api";
import { Header, InputField, Button, Container, GoToLink, StatMessage } from "./StyleComponents";

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [statMessage, setStatMessage] = useState({ text: "", type: "" });
    const navigate = useNavigate();

    const handleLogin = async () => {
        try {
            const response = await loginUser({ username, password });
            console.log(response);
            localStorage.setItem("token", response.data.access_token);
            localStorage.setItem("username", response.data.username);
            localStorage.setItem("is_admin", response.data.is_admin);
            setStatMessage({text: response.data.message, type: "success" });
            setTimeout(() => navigate("/chat"), 2000);
        } catch (error) {
            const errorMessage = error.response?.data?.detail || error.response?.statusText || "Login failed.";
            setStatMessage({ text: errorMessage, type: "error" });
        }
    };

    return (
        <Container>
            <Header>Login</Header>
            <InputField type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)}/>
            <InputField type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)}/>
            <Button onClick={handleLogin}> Login </Button>
            <div>
                Don't have an account?
                <GoToLink onClick={() => navigate("/register")}> Register Now </GoToLink>
            </div>
            {statMessage.text && <StatMessage type={statMessage.type}>{statMessage.text}</StatMessage>}
        </Container>
    );
};

export default Login;
