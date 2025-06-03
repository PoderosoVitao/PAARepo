import React, { useState } from 'react';
import { Button, Typography, Stack, ButtonGroup, Tooltip, CircularProgress, LinearProgress } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

export default function AlgoritmoMenu({ onRun }) {
    const [problema, setProblema] = useState('A');
    const [algoritmo, setAlgoritmo] = useState('forca_bruta');
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);

    const handleRun = async () => {
        setLoading(true);
        setProgress(0);

        const eventSource = new EventSource('http://localhost:5000/progress-updates');

        eventSource.onmessage = (event) => {
            console.log("Received progress update:", event.data);
            const data = JSON.parse(event.data);
            if (data.progress !== undefined) { // Allow 0 as a valid progress value
                if (typeof data.progress === 'number') {
                    setProgress(data.progress);
                    console.log("Progress bar value:", data.progress);
                } else {
                    console.error("Invalid progress data received:", data);
                }
            }
        };

        try {
            await onRun(problema, algoritmo);
        } finally {
            eventSource.close();
            setLoading(false);
        }
    };

    return (
        <Stack spacing={2}>
            <div>
                <Typography variant="subtitle1" gutterBottom>Escolha o problema:</Typography>
                <ButtonGroup variant="outlined" fullWidth>
                    <Tooltip title="Encontrar o número máximo de estações que um turista pode visitar">
                        <Button
                            onClick={() => setProblema('A')}
                            variant={problema === 'A' ? 'contained' : 'outlined'}
                            sx={{ flex: 1 }}
                        >
                            Problema A
                        </Button>
                    </Tooltip>
                    <Tooltip title="Determinar as estações para instalação de guichês">
                        <Button
                            onClick={() => setProblema('B')}
                            variant={problema === 'B' ? 'contained' : 'outlined'}
                            sx={{ flex: 1 }}
                        >
                            Problema B
                        </Button>
                    </Tooltip>
                </ButtonGroup>
            </div>

            <div>
                <Typography variant="subtitle1" gutterBottom>Escolha o algoritmo:</Typography>
                <Stack spacing={1}>
                    <Button
                        onClick={() => setAlgoritmo('forca_bruta')}
                        variant={algoritmo === 'forca_bruta' ? 'contained' : 'outlined'}
                        fullWidth
                    >
                        Força Bruta
                    </Button>
                    <Button
                        onClick={() => setAlgoritmo('branch_and_bound')}
                        variant={algoritmo === 'branch_and_bound' ? 'contained' : 'outlined'}
                        fullWidth
                    >
                        Branch and Bound
                    </Button>
                    <Button
                        onClick={() => setAlgoritmo('heuristica')}
                        variant={algoritmo === 'heuristica' ? 'contained' : 'outlined'}
                        fullWidth
                    >
                        Heurística
                    </Button>
                </Stack>
            </div>

            <div>
                <Button
                    onClick={handleRun}
                    variant="contained"
                    startIcon={<PlayArrowIcon />}
                    fullWidth
                    disabled={loading}
                >
                    Executar
                </Button>
                {loading && <CircularProgress size={24} sx={{ position: 'absolute', top: '50%', left: '50%', marginTop: '-12px', marginLeft: '-12px' }} />}
            </div>

            <div>
                <LinearProgress variant="determinate" value={progress} />
            </div>
        </Stack>
    );
}
