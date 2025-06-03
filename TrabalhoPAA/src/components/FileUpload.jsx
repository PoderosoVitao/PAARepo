import React from 'react';
import { Button } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';

export default function FileUpload({ label, onFileRead }) {
    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (evt) => {
            onFileRead(evt.target.result);
        };
        reader.readAsText(file);
    };

    return (
        <div style={{ margin: '8px 0' }}>
            <Button
                variant="outlined"
                component="label"
                startIcon={<UploadFileIcon />}
                fullWidth
                sx={{
                    borderColor: 'primary.main',
                    '&:hover': {
                        borderColor: 'primary.dark',
                        backgroundColor: 'primary.50'
                    }
                }}
            >
                {label}
                <input type="file" hidden onChange={handleFileChange} accept=".txt" />
            </Button>
        </div>
    );
}
