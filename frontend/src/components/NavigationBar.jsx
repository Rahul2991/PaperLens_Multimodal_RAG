import { NavBar, ProfileContainer, ProfileCircle, DropdownMenu } from "../components/StyleComponents";
import React, { useEffect, useRef, useState } from "react";

const NavigationBar = ({ username, handleDashboard, handleLogout }) => {
    const [dropdownVisible, setDropdownVisible] = useState(false);
    const dropdownRef = useRef(null);

    const toggleDropdown = () => setDropdownVisible((prev) => !prev);
    
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setDropdownVisible(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    return (
        <NavBar>
            <h3>Multimodal Chat Interface</h3>
            <ProfileContainer ref={dropdownRef} onClick={toggleDropdown} tabIndex={0}>
                <ProfileCircle>{username.charAt(0).toUpperCase()}</ProfileCircle>
                {dropdownVisible && (
                    <DropdownMenu>
                        <button onClick={handleDashboard}>Dashboard</button>
                        <button onClick={handleLogout}>Logout</button>
                    </DropdownMenu>
                )}
            </ProfileContainer>
        </NavBar>
    );
};

export default NavigationBar;