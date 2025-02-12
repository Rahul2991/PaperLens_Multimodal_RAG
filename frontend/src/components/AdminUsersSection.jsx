import React, { useEffect, useRef, useState } from "react";
import { listUsers } from "../api";
import styled from "styled-components";

const Container  = styled.div`
    max-width: 800px;
    margin: auto;
    padding: 20px;
    background: #f9f9f9;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h2`
    text-align: center;
    color: #333;
`;

const Table = styled.table`
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
`;

const Th = styled.th`
    background: #2563eb;
    color: white;
    padding: 10px;
    text-align: left;
`;

const Td = styled.td`
    padding: 10px;
    border: 1px solid #ddd;
    text-align: left;
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
        <Container>
            <Title>Users</Title>
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
        </Container>
    );
};

export default AdminUsersSection;
