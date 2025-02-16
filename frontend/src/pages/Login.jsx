// Login.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api";
import { Header, InputField, Button, Container, GoToLink } from "../components/StyleComponents";
import NotificationModal from "../components/NotificationModal";

/**
 * Login Component
 * Handles user login with username and password.
 */
const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [statMessage, setStatMessage] = useState({ text: "", type: "" });
    const navigate = useNavigate();

    // Handles user login
    const handleLogin = async () => {
        try {
            const response = await loginUser({ username, password });
            console.log(response);
            localStorage.setItem("token", response.data.access_token);
            localStorage.setItem("username", response.data.username);
            localStorage.setItem("is_admin", response.data.is_admin);
            setStatMessage({ text: response.data.message, type: "success" });
        } catch (error) {
            const errorMessage = "Login failed.";
            setStatMessage({ text: errorMessage, type: "error" });
        }
    };

    // Handle confirmation and navigate to chat page
    const handleConfirm = () => {
        if (statMessage.type === "success") {
            navigate("/chat");
        }
        setStatMessage({ text: "", type: "" });
    };

    return (
        <Container>
            <Header>Login</Header>
            <InputField type="text" name="username" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)}/>
            <InputField type="password" name="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)}/>
            <Button onClick={handleLogin}> Login </Button>
            <p>
                Don't have an account?
                <GoToLink onClick={() => navigate("/register")}> Register Now </GoToLink>
            </p>
            <NotificationModal message={statMessage.text} type={statMessage.type} onConfirm={handleConfirm} />
        </Container>
    );
};

export default Login;
