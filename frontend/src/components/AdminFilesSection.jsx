import React, { useState } from "react";
import styled from "styled-components";
import { uploadRagFilesAdmin } from "../api";


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

const AdminFilesSection = () => {
    const [files, setFiles] = useState([]);
    const [tags, setTags] = useState("");
    const [loading, setLoading] = useState(false);

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
        </div>
    );
};

export default AdminFilesSection;
