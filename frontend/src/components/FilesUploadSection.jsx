import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { uploadRagFiles, listFiles } from "../api";
import { useDropzone } from "react-dropzone";
import { useNavigate } from "react-router-dom";

const MAX_FILE_SIZE_MB = 10;

const FileUploadContainer = styled.div`
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

const Td = styled.td`
    padding: 10px;
    border: 1px solid #ddd;
    text-align: left;
`;

const Tag = styled.span`
    background: #007bff;
    color: white;
    padding: 5px 10px;
    border-radius: 15px;
    margin: 5px;
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 14px;
`;

const TagClose = styled.span`
    font-weight: bold;
    font-size: 18px;
    position: relative;
    top: -5px;
    left: -1px;
    color: red;
    cursor: pointer;
    width: 16px;
    height: 16px;
`;

const TagInput = styled.div`
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    border: 1px solid #ccc;
    padding: 8px;
    border-radius: 8px;
    min-height: 40px;
    margin-bottom: 15px;
    background: #fff;
`;

const UploadButton = styled.button`
    background: #007bff;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 5px;
    cursor: pointer;
    margin-top: 15px;
    font-size: 16px;
    transition: background 0.3s ease;
    &:hover {
        background: #0056b3;
    }
    &:disabled {
        background: #ccc;
        cursor: not-allowed;
    }
`;

const FileTable = styled.table`
        width: 100%;
        margin-top: 20px;
        border-collapse: collapse;
        text-align: left;
    `;

const TableHeader = styled.th`
        background: #007bff;
        color: white;
        padding: 10px;
    `;

const TableRow = styled.tr`
        &:nth-child(even) {
            background: #f2f2f2;
        }
    `;

const UploadSection = styled.div`
        display: flex;
        justify-content: space-between;
        width: 97.5%;
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    `;

const LeftSection = styled.div`
        display: flex;
        flex-direction: column;
        gap: 15px;
        width: 65%;
    `;

const DropzoneContainer = styled.div`
        display: flex;
        align-items: center;
        justify-content: center;
        width: 96%;
        height: 60%;
        border: 2px dashed #007bff;
        padding: 20px;
        text-align: center;
        cursor: pointer;
        border-radius: 8px;
        background: #f9f9f9;
        &:hover {
            background: #e9ecef;
        }
    `;

const FilePreviewSection = styled.div`
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 30%;
        text-align: center;
        border: 1px solid #ccc;
        padding: 10px;
        border-radius: 8px;
    `;

const PreviewNavigation = styled.div`
        display: flex;
        align-items: center;
        gap: 10px;
    `;

const PreviewImage = styled.img`
        max-width: 375px;
        height: 250px;
        border-radius: 8px;
        margin-bottom: 10px;
    `;

const NoPreview = styled.div`
        display: flex;
        padding: 20px;
        background: #f8d7da;
        color: #721c24;
        border-radius: 8px;
        height: 250px;
        align-items: center;
    `;

const RemoveButton = styled.button`
    margin-top: 10px;
    padding: 8px 12px;
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    
    &:hover {
        background: #c82333;
    }
`;

const FilesUploadSection = ({ is_admin }) => {
    const [files, setFiles] = useState([]);
    // const [tags, setTags] = useState("");
    const [tags, setTags] = useState([]);
    const [loading, setLoading] = useState(false);
    const [filesList, setFilesList] = useState([]);
    const [statMessage, setStatMessage] = useState({ text: "", type: "" });
    const [inputValue, setInputValue] = useState("");
    const navigate = useNavigate();

    const addTag = (e) => {
        if (e.key === "Enter" && inputValue.trim()) {
            setTags([...tags, inputValue.trim()]);
            setInputValue("");
            e.preventDefault();
        }
    };

    const removeTag = (index) => {
        setTags(tags.filter((_, i) => i !== index));
    };

    const handleLogout = () => {
        console.log('logout');
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        localStorage.removeItem("is_admin");
        navigate("/login");
    };

    const handleError = (error) => {
        if (error.response?.status === 401) {
            setStatMessage({ text: "Session expired. Redirecting to login...", type: "error" });
            setTimeout(() => handleLogout(), 2000);
        } else {
            setStatMessage({ text: "An error occurred.", type: "error" });
            console.error("Chat error:", error);
            setTimeout(() => setStatMessage({ text: "", type: "" }), 2000);
        }

    };

    const fetchFilesList = async () => {
        try {
            const response = await listFiles(is_admin);
            setFilesList(response.data);
        } catch (error) {
            handleError(error);
        }
    };

    useEffect(() => {
        fetchFilesList();
    }, []);

    const handleSubmit = async () => {
        setLoading(true);
        try {
            const response = await uploadRagFiles(files, tags.join(","), is_admin);
            alert("Files uploaded successfully!");
            setFiles([]);
            setTags([]);
            fetchFilesList();
        } catch (error) {
            console.error("Error uploading files", error);
            alert("File upload failed!");
        }
        setLoading(false);
    };

    const removeFile = (index) => {
        const updatedFiles = files.filter((_, i) => i !== index);
        setFiles(updatedFiles);
        
        // Adjust index if necessary
        if (updatedFiles.length === 0) {
            setCurrentFileIndex(0);
        } else if (index >= updatedFiles.length) {
            setCurrentFileIndex(updatedFiles.length - 1);
        }
    };

    const [currentFileIndex, setCurrentFileIndex] = useState(0);

    const onDrop = (acceptedFiles) => {
        setFiles([...files, ...acceptedFiles]);
        setCurrentFileIndex(0);
    };

    const { getRootProps, getInputProps } = useDropzone({ 
        onDrop, 
        multiple: true,
        accept: {
            'application/pdf': ['.pdf'],
            'image/*': ['.png', '.jpg', '.jpeg', '.gif'],
            'text/plain': ['.txt'],
        },
    });

    const nextFile = () => {
        setCurrentFileIndex((prevIndex) => (prevIndex + 1) % files.length);
    };

    const prevFile = () => {
        setCurrentFileIndex((prevIndex) => (prevIndex - 1 + files.length) % files.length);
    };

    return (
        <FileUploadContainer >
            <Title>Upload Files</Title>

            <UploadSection>
                <LeftSection>
                    <DropzoneContainer {...getRootProps()}>
                        <input {...getInputProps()} />
                        <p>Drag & drop files here, or click to select files</p>
                    </DropzoneContainer>
                    <TagInput>
                        {tags.map((tag, index) => (
                            <Tag key={index}>
                                {tag}
                                <TagClose onClick={() => removeTag(index)}>x</TagClose>
                            </Tag>
                        ))}
                        <input
                            type="text"
                            placeholder="Add tags and press Enter"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={addTag}
                            style={{ flex: 1, border: "none", outline: "none" }}
                        />
                    </TagInput>
                </LeftSection>
                <FilePreviewSection>
                    {files.length > 0 ? (
                        <>
                            <PreviewNavigation>
                                <button onClick={prevFile}>⬅</button>
                                <PreviewImage src={URL.createObjectURL(files[currentFileIndex])} alt="Preview" />
                                <button onClick={nextFile}>➡</button>
                            </PreviewNavigation>
                            <p>{currentFileIndex + 1} / {files.length}</p>
                            <RemoveButton onClick={() => removeFile(currentFileIndex)}>🗑 Remove</RemoveButton>
                        </>
                    ) : (
                        <NoPreview>No Preview Available</NoPreview>
                    )}
                </FilePreviewSection>
            </UploadSection>
            <UploadButton onClick={handleSubmit} disabled={loading}>{loading ? "Uploading..." : "Upload Files"}</UploadButton>

            <FileTable>
                <thead>
                    <tr>
                        <TableHeader>Filename</TableHeader>
                        {is_admin && <TableHeader>Uploader</TableHeader>}
                        {is_admin && <TableHeader>Role</TableHeader>}
                        <TableHeader>Upload Time</TableHeader>
                        {is_admin && <TableHeader>Collection</TableHeader>}
                        <TableHeader>Tags</TableHeader>
                    </tr>
                </thead>
                <tbody>
                    {filesList.map((file) => (
                        <TableRow key={file.id}>
                            <Td>{file.filename}</Td>
                            {is_admin && <Td>{file.uploader}</Td>}
                            {is_admin && <Td>{file.role}</Td>}
                            <Td>{file.upload_time}</Td>
                            {is_admin && <Td>{file.collection_name}</Td>}
                            <Td>{file.tags}</Td>
                        </TableRow>
                    ))}
                </tbody>
            </FileTable>
        </FileUploadContainer >
    );
};

export default FilesUploadSection;

