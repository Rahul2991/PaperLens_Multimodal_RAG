import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { FaUsers, FaFileAlt, FaChartBar, FaCog } from "react-icons/fa";
import { AdminContainer, AdminSidebarItem, DropdownMenu, NavBar, PageContainer, ProfileCircle, ProfileContainer, SidebarContainer, SidebarIcon, SidebarList } from "./StyleComponents"
import { LuLogs } from "react-icons/lu";
import AdminUsersSection from "./AdminUsersSection";
import AdminFilesSection from "./AdminFilesSection";
import AdminLogsSection from "./AdminLogsSection";

const AdminDashboard = () => {
    const [activePage, setActivePage] = useState("dashboard");
    const [username, setUsername] = useState("");
    const [dropdownVisible, setDropdownVisible] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchInitialData = async () => {
            const user = localStorage.getItem("username");
            setUsername(user || "User");
        };
        fetchInitialData();
    }, []);

    const toggleDropdown = () => setDropdownVisible(!dropdownVisible);

    const closeDropdown = () => setDropdownVisible(false);

    const handleLogout = () => {
        console.log('logout');
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        navigate("/login");
    };

    const renderContent = () => {
        switch (activePage) {
            case "dashboard":
                return <h2>Welcome to the Admin Dashboard</h2>;
            case "users":
                return <AdminUsersSection />
            case "files":
                return <AdminFilesSection />
            case "logs":
                return <AdminLogsSection />;
            case "settings":
                return <h2>settings</h2>;
            default:
                return <h2>Select an option from the sidebar</h2>;
        }
    };

    const menuItems = [
        { name: "Dashboard", icon: <FaChartBar />, id: "dashboard" },
        { name: "Manage Users", icon: <FaUsers />, id: "users" },
        { name: "Manage Files", icon: <FaFileAlt />, id: "files" },
        { name: "Logs", icon: <LuLogs />, id: "logs" },
        { name: "Settings", icon: <FaCog />, id: "settings" },
    ];

    return (
        <PageContainer>
            <NavBar>
                <h3>Admin Panel</h3>
                <ProfileContainer onClick={toggleDropdown} onBlur={closeDropdown} tabIndex={0}>
                    <ProfileCircle>{username.charAt(0).toUpperCase()}</ProfileCircle>
                    <DropdownMenu isVisible={dropdownVisible}>
                        <button onClick={handleLogout}>Logout</button>
                    </DropdownMenu>
                </ProfileContainer>
            </NavBar>
            <AdminContainer>
                <SidebarContainer>
                    <SidebarList>
                        {menuItems.map((item) => (
                            <AdminSidebarItem key={item.id} active={activePage === item.id} onClick={() => setActivePage(item.id)}>
                                <SidebarIcon>{item.icon}</SidebarIcon>
                                {item.name}
                            </AdminSidebarItem>
                        ))}
                    </SidebarList>
                </SidebarContainer>
                {renderContent()}
            </AdminContainer>
        </PageContainer>
    )
}

export default AdminDashboard;
