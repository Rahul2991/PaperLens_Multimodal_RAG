import React, { useEffect, useRef, useState } from "react";
import { listUsers } from "../api";
import styled from "styled-components";

const Table = styled.table`
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
`;

const Th = styled.th`
    background-color: #2563eb;
    color: white;
    padding: 10px;
`;

const Td = styled.td`
    padding: 10px;
    border: 1px solid #ddd;
`;

const AdminUsersSection = () => {
    const [usersList, setUsersList] = useState([]);

    useEffect(() => {
        // Fetching users from API
        const fetchUsers = async () => {
            try {
                const response = await listUsers();
                console.log(response.data);  // Assuming the data is in response.data
                setUsersList(response.data);  // Assuming the data is in response.data
            } catch (error) {
                console.error("Error fetching users:", error);
            }
        };

        fetchUsers();
    }, []);

    return (
        <div>
            <h2>Users</h2>
            <Table>
                <thead>
                    <tr>
                        <Th>ID</Th>
                        <Th>Name</Th>
                        <Th>Email</Th>
                        <Th>Username</Th>
                        <Th>Role</Th>
                        <Th>Interactions</Th>
                        <Th>Last Activity</Th>
                    </tr>
                </thead>
                <tbody>
                    {usersList.map((user) => (
                        <tr key={user.id}>
                            <Td>{user.id}</Td>
                            <Td>{user.name}</Td>
                            <Td>{user.email}</Td>
                            <Td>{user.username}</Td>
                            <Td>{user.is_admin ? "Admin" : "User"}</Td>
                            <Td>{user.interactions}</Td>
                            <Td>{user.lastActivity}</Td>
                        </tr>
                    ))}
                </tbody>
            </Table>
        </div>
    );
};

export default AdminUsersSection;
