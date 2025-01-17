import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../api";

const Register = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState({ text: "", type: "" });
    const navigate = useNavigate();

    const handleRegister = async () => {
        try {
            const response = await registerUser({ username, password });
            setMessage({ text: response.data.message, type: "success" });
            setTimeout(() => navigate("/login"), 2000);
        } catch (error) {
            const errorMessage = error.response?.data?.detail || error.response?.statusText || "Registration failed.";
            setMessage({ text: errorMessage, type: "error" });
        }
    };

    const styles = {
        container: {
            maxWidth: "90%",
            width: "400px",
            margin: "0 auto",
            padding: "20px",
            borderRadius: "8px",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
            textAlign: "center",
            fontFamily: "'Roboto', sans-serif",
            boxSizing: "border-box",
        },
        title: {
            fontSize: "24px",
            marginBottom: "20px",
            color: "#333",
        },
        input: {
            width: "100%",
            padding: "10px",
            margin: "10px 0",
            borderRadius: "4px",
            border: "1px solid #ccc",
            fontSize: "16px",
            boxSizing: "border-box",
        },
        button: {
            width: "100%",
            padding: "10px",
            margin: "10px 0",
            border: "none",
            borderRadius: "4px",
            backgroundColor: "#007BFF",
            color: "white",
            fontSize: "16px",
            cursor: "pointer",
            boxSizing: "border-box",
        },
        buttonHover: {
            backgroundColor: "#0056b3",
        },
        message: {
            marginTop: "10px",
            color: message.type === "success" ? "green" : "red",
            fontSize: "14px",
        },
        link: {
            marginTop: "10px",
            display: "inline",
            color: "#007BFF",
            textDecoration: "none",
            fontSize: "14px",
            cursor: "pointer",
        },
        linkHover: {
            color: "#0056b3",
            textDecoration: "underline",
        },
    }

    return (
        <div style={styles.container}>
            <h1 style={styles.title}>Register</h1>
            <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} style={styles.input} />
            <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} style={styles.input} />
            <button
                onClick={handleRegister}
                style={styles.button}
                onMouseOver={(e) => (e.target.style.backgroundColor = styles.buttonHover.backgroundColor)}
                onMouseOut={(e) => (e.target.style.backgroundColor = styles.button.backgroundColor)}
            >
                Register
            </button>
            <div>
                Already have an account? &nbsp;
                <a
                    onClick={() => navigate("/login")}
                    style={styles.link}
                    onMouseOver={(e) => (e.target.style.color = styles.linkHover.color)}
                    onMouseOut={(e) => (e.target.style.color = styles.link.color)}
                >
                    Go to Login
                </a>
            </div>
            {message.text && <p style={styles.message}>{message.text}</p>}
        </div>
    )
}

export default Register;
