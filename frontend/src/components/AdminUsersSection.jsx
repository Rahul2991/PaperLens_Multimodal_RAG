import React, { useEffect, useRef, useState } from "react";
import { listUsers } from "../api";
import styled from "styled-components";

const Container = styled.div`
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    text-align: center;
    background: white;
    width: 100%;
`;

const Title = styled.h2`
    text-align: center;
    color: #333;
`;

const Table = styled.table`
    width: 100%;
    margin-top: 20px;
    border-collapse: collapse;
    text-align: left;
    `;

const Th = styled.th`
    background: #007bff;
    color: white;
    padding: 10px;
`;

const TableRow = styled.tr`
        &:nth-child(even) {
            background: #f2f2f2;
        }
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
                        {/* <Th>ID</Th> */}
                        {/* <Th>Name</Th> */}
                        {/* <Th>Email</Th> */}
                        <Th>Username</Th>
                        <Th>Role</Th>
                        {/* <Th>Interactions</Th> */}
                        {/* <Th>Last Activity</Th> */}
                    </tr>
                </thead>
                <tbody>
                    {usersList.map((user) => (
                        <TableRow key={user.id}>
                            {/* <Td>{user.id}</Td> */}
                            {/* <Td>{user.name}</Td> */}
                            {/* <Td>{user.email}</Td> */}
                            <Td>{user.username}</Td>
                            <Td>{user.is_admin ? "Admin" : "User"}</Td>
                            {/* <Td>{user.interactions}</Td> */}
                            {/* <Td>{user.lastActivity}</Td> */}
                        </TableRow>
                    ))}
                </tbody>
            </Table>
        </Container>
    );
};

export default AdminUsersSection;
