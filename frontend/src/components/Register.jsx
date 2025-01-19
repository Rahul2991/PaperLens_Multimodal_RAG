import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../api";
import { Button, Container, GoToLink, Header, InputField, StatMessage } from "./StyleComponents";

const Register = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [statMessage, setStatMessage] = useState({ text: "", type: "" });
    const navigate = useNavigate();

    const handleRegister = async () => {
        try {
            const response = await registerUser({ username, password });
            setStatMessage({ text: response.data.message, type: "success" });
            setTimeout(() => navigate("/login"), 2000);
        } catch (error) {
            const errorMessage = error.response?.data?.detail || error.response?.statusText || "Registration failed.";
            setStatMessage({ text: errorMessage, type: "error" });
        }
    };

    return (
        <Container>
            <Header>Register</Header>
            <InputField type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
            <InputField type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)}/>
            <Button onClick={handleRegister}> Register </Button>
            <div>
                Already have an account?
                <GoToLink onClick={() => navigate("/login")}> Go to Login </GoToLink>
            </div>
            {statMessage.text && <StatMessage type={statMessage.type}>{statMessage.text}</StatMessage>}
        </Container>
    )
}

export default Register;
