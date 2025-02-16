import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../api";
import { Container, Header, InputField, GoToLink, Button } from '../components/StyleComponents';
import NotificationModal from "../components/NotificationModal";

/**
 * Register Component
 * Handles user registration with username and password.
 */
const Register = () => {
    const [formData, setFormData] = useState({ username: "", password: "" });
    const [statMessage, setStatMessage] = useState({ text: "", type: "" });
    const navigate = useNavigate();

    // Updates form input values
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prevData) => ({ ...prevData, [name]: value }));
    };

    // Handles user registration
    const handleRegister = async () => {
        try {
            const response = await registerUser(formData);
            setStatMessage({ text: response.data.message, type: "success" });
            // setTimeout(() => navigate("/login"), 2000);
        } catch (error) {
            const errorMessage = "Registration failed.";
            setStatMessage({ text: errorMessage, type: "error" });
        }
    };

    // Handle confirmation and navigate to login
    const handleConfirm = () => {
        if (statMessage.type === "success") {
            navigate("/login");
        }
        setStatMessage({ text: "", type: "" });
    };

    return (
        <Container>
            <Header>Register</Header>
            <InputField type="text" name="username" placeholder="Username" value={formData.username} onChange={handleChange} />
            <InputField type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} />
            <Button onClick={handleRegister}> Register </Button>
            <p>
                Already have an account?
                <GoToLink onClick={() => navigate("/login")}> Go to Login </GoToLink>
            </p>
            <NotificationModal message={statMessage.text} type={statMessage.type} onConfirm={handleConfirm} />
        </Container>
    )
}

export default Register;