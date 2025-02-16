import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { FaFileAlt, FaChartBar, FaCog } from "react-icons/fa";
import { DashboardContainer, DashboardSidebarItem, DropdownMenu, SideBarGoToBtn, NavBar, PageContainer, ProfileCircle, ProfileContainer, SidebarContainer, SidebarIcon, SidebarList } from "../components/StyleComponents"
import FilesUploadSection from "../components/FilesUploadSection";

const UserDashboard = () => {
    const [activePage, setActivePage] = useState("files");
    const [username, setUsername] = useState("");
    const [dropdownVisible, setDropdownVisible] = useState(false);
    const navigate = useNavigate();
    const dropdownRef = useRef(null);

    useEffect(() => {
        const fetchInitialData = async () => {
            const user = localStorage.getItem("username");
            setUsername(user || "User");
        };
        fetchInitialData();
    }, []);

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

    const toggleDropdown = () => setDropdownVisible(!dropdownVisible);


    const handleLogout = () => {
        console.log('logout');
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        navigate("/login");
    };

    const renderContent = () => {
        switch (activePage) {
            case "dashboard":
                return <h2>Welcome to the User Dashboard</h2>;
            case "files":
                return <FilesUploadSection is_admin={false} />
            case "settings":
                return <h2>settings</h2>;
            default:
                return <h2>Select an option from the sidebar</h2>;
        }
    };

    const menuItems = [
        // { name: "Dashboard", icon: <FaChartBar />, id: "dashboard" },
        { name: "Manage Files", icon: <FaFileAlt />, id: "files" },
        // { name: "Settings", icon: <FaCog />, id: "settings" },
    ];

    return (
        <PageContainer>
            <NavBar>
                <h3>User Panel</h3>
                <ProfileContainer ref={dropdownRef} onClick={toggleDropdown} tabIndex={0}>
                    <ProfileCircle>{username.charAt(0).toUpperCase()}</ProfileCircle>
                    {dropdownVisible && (
                        <DropdownMenu>
                            <button onClick={handleLogout}>Logout</button>
                        </DropdownMenu>
                    )}
                </ProfileContainer>
            </NavBar>
            <DashboardContainer>
                <SidebarContainer>
                    <SidebarList>
                        {menuItems.map((item) => (
                            <DashboardSidebarItem key={item.id} active={activePage === item.id} onClick={() => setActivePage(item.id)}>
                                <SidebarIcon>{item.icon}</SidebarIcon>
                                {item.name}
                            </DashboardSidebarItem>
                        ))}
                    </SidebarList>
                    <SideBarGoToBtn onClick={() => { navigate('/chat') }}>Chat</SideBarGoToBtn>
                </SidebarContainer>
                {renderContent()}
            </DashboardContainer>
        </PageContainer>
    )
}

export default UserDashboard;
