import React from "react";
import styled from "styled-components";

const LogList = styled.ul`
    list-style: none;
    padding: 0;
`;

const LogItem = styled.li`
    padding: 10px;
    border: 1px solid #ddd;
    margin-bottom: 10px;
    border-radius: 6px;
`;

const AdminLogsSection = () => {
    const logs = [
        { id: 1, message: "User John Doe uploaded a file.", timestamp: "2025-01-22 10:00 AM" },
        { id: 2, message: "File 'Document.pdf' was tagged with 'Finance, Reports'.", timestamp: "2025-01-22 11:00 AM" },
    ];

    return (
        <div>
            <h2>Logs</h2>
            <LogList>
                {logs.map((log) => (
                    <LogItem key={log.id}>
                        <div>{log.message}</div>
                        <small>{log.timestamp}</small>
                    </LogItem>
                ))}
            </LogList>
        </div>
    );
};

export default AdminLogsSection;
