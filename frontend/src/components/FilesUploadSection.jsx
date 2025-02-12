import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { uploadRagFiles, listFiles } from "../api";

const FileUploadContainer  = styled.div`
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

const Input = styled.input`
    width: 100%;
    padding: 10px;
    margin: 10px 0;
    border: 1px solid #ddd;
    border-radius: 6px;
`;

const Button = styled.button`
    width: 100%;
    padding: 10px;
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
    transition: 0.3s;

    &:hover {
        background-color: #1e4bbb;
    }

    &:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }
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

const FilesUploadSection = (props) => {
    const [files, setFiles] = useState([]);
    const [tags, setTags] = useState("");
    const [loading, setLoading] = useState(false);
    const [filesList, setFilesList] = useState([]);

    const fetchFilesList = async () => {
        try {
            const response = await listFiles(props.is_admin);
            console.log(response.data);  // Assuming the data is in response.data
            setFilesList(response.data);  // Assuming the data is in response.data
        } catch (error) {
            console.error("Error fetching files list:", error);
        }
    };

    useEffect(() => {
        fetchFilesList();
    }, []);

    const handleFileUpload = (e) => {
        const uploadedFiles = Array.from(e.target.files);
        const filesWithTags = uploadedFiles.map((file) => ({
            file: file,
            tags: tags,
        }));

        setFiles((prevFiles) => [...prevFiles, ...filesWithTags]);
        setTags(""); // Reset tags input
    };

    const handleSubmit = async () => {
        setLoading(true);
        const fileList = files.map((fileObj) => fileObj.file);  // Extract files
        const fileTags = files.map((fileObj) => fileObj.tags).join(','); // Extract tags

        try {
            console.log(fileList);
            console.log(fileTags);
            const response = await uploadRagFiles(fileList, fileTags, props.is_admin);
            console.log("Response from server", response);

            
            alert("Files uploaded successfully!");
            setFiles([]);  // Reset file list after successful upload
            setTags(""); // Reset tags input
            document.getElementById("fileInput").value = "";
            document.getElementById("rag-file-upload").value = "";
            
            fetchFilesList();

            setLoading(false);
        } catch (error) {
            setLoading(false);
            console.error("Error uploading files", error);
            alert("File upload failed!");
        }
    };

    return (
        <FileUploadContainer >
            <Title>Upload Files</Title>
            <Input
                type="text"
                placeholder="Add tags (comma-separated)"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                id="fileInput"
            />
            <Input
                type="file"
                accept=".png,.jpg,.jpeg,.pdf,.txt" // Supported file types
                onChange={handleFileUpload}
                id="rag-file-upload"
                multiple
                disabled={loading}
            />
            <Button onClick={handleSubmit} disabled={loading}>
                {loading ? "Uploading..." : "Upload Files"}
            </Button>
            <Title>Files List</Title>
            <Table>
                <thead>
                    <tr>
                        <Th>Filename</Th>
                        {props.is_admin && <Th>Uploader</Th>}
                        {props.is_admin && <Th>Role</Th>}
                        <Th>Upload Time</Th>
                        {props.is_admin && <Th>Collection</Th>}
                        <Th>Tags</Th>
                    </tr>
                </thead>
                <tbody>
                    {filesList.map((file) => (
                        <tr key={file.id}>
                            <Td>{file.filename}</Td>
                            {props.is_admin && <Td>{file.uploader}</Td>}
                            {props.is_admin && <Td>{file.role}</Td>}
                            <Td>{file.upload_time}</Td>
                            {props.is_admin && <Td>{file.collection_name}</Td>}
                            <Td>{file.tags}</Td>
                        </tr>
                    ))}
                </tbody>
            </Table>
        </FileUploadContainer >
    );
};

export default FilesUploadSection;
