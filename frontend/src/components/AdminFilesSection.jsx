import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { uploadRagFilesAdmin, listFiles } from "../api";


const FileUploadContainer = styled.div`
    margin-bottom: 20px;
`;

const FileInput = styled.input`
    margin: 10px 0;
`;

const FileList = styled.ul`
    list-style: none;
    padding: 0;
`;

const FileItem = styled.li`
    padding: 10px;
    border: 1px solid #ddd;
    margin-bottom: 10px;
    border-radius: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
`;

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

const AdminFilesSection = () => {
    const [files, setFiles] = useState([]);
    const [tags, setTags] = useState("");
    const [loading, setLoading] = useState(false);
    const [filesList, setFilesList] = useState([]);

    useEffect(() => {
            // Fetching users from API
            const fetchFilesList = async () => {
                try {
                    const response = await listFiles();
                    console.log(response.data);  // Assuming the data is in response.data
                    setFilesList(response.data);  // Assuming the data is in response.data
                } catch (error) {
                    console.error("Error fetching files list:", error);
                }
            };
    
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
            const response = await uploadRagFilesAdmin(fileList, fileTags);
            console.log("Response from server", response);
            setLoading(false);
            alert("Files uploaded successfully!");
            setFiles([]);  // Reset file list after successful upload
        } catch (error) {
            setLoading(false);
            console.error("Error uploading files", error);
            alert("File upload failed!");
        }
    };

    return (
        <div>
            <h2>Files</h2>
            <FileUploadContainer>
                <input
                    type="text"
                    placeholder="Add tags (comma-separated)"
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                />
                <FileInput
                    type="file"
                    accept=".png,.jpg,.jpeg,.pdf,.txt" // Supported file types
                    onChange={handleFileUpload}
                    id="rag-file-upload"
                    multiple
                    disabled={loading}
                />
                <button onClick={handleSubmit} disabled={loading}>
                    {loading ? "Uploading..." : "Upload Files"}
                </button>
            </FileUploadContainer>
            <FileList>
                {files.map((file, index) => (
                    <FileItem key={index}>
                        <div>
                            <strong>{file.name}</strong> - {file.size} bytes
                        </div>
                        <span>Tags: {file.tags || "None"}</span>
                    </FileItem>
                ))}
            </FileList>

            <div>
                <h2>Files List</h2>
                <Table>
                    <thead>
                        <tr>
                            <Th>Filename</Th>
                            <Th>Uploader</Th>
                            <Th>Role</Th>
                            <Th>Upload Time</Th>
                            <Th>Collection</Th>
                            <Th>Tags</Th>
                        </tr>
                    </thead>
                    <tbody>
                        {filesList.map((file) => (
                            <tr key={file.id}>
                                <Td>{file.filename}</Td>
                                <Td>{file.uploader}</Td>
                                <Td>{file.role}</Td>
                                <Td>{file.upload_time}</Td>
                                <Td>{file.collection_name}</Td>
                                <Td>{file.tags}</Td>
                            </tr>
                        ))}
                    </tbody>
                </Table>
            </div>
        </div>
    );
};

export default AdminFilesSection;
