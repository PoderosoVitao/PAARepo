import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import GraphView from './components/GraphView';
import AlgoritmoMenu from './components/AlgoritmoMenu';
import './App.css';
import { Box, Typography, Paper, Stack, Chip } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import axios from 'axios';

function parseStations(text) {
  // Formato: Nome x y\n
  const lines = text.split(/\r?\n/);
  const stations = {};
  for (const line of lines) {
    if (!line.trim()) continue;
    const parts = line.trim().split(/\s+/);
    if (parts.length < 3) continue;
    const x = parseFloat(parts[parts.length - 2]);
    const y = parseFloat(parts[parts.length - 1]);
    const name = parts.slice(0, -2).join(' ');
    stations[name] = [x, y];
  }
  return stations;
}

function parseLines(text) {
  // Formato: LinhaX, cor\nNome1;Nome2\n...
  const lines = text.split(/\r?\n/);
  const result = [];
  let current = null;
  for (const line of lines) {
    if (!line.trim()) continue;
    if (line.startsWith('Linha')) {
      const [linha, cor] = line.split(',').map(s => s.trim());
      current = [linha, cor, []];
      result.push(current);
    } else if (line.includes(';') && current) {
      const [from, to] = line.split(';').map(s => s.trim());
      current[2].push([from, to]);
    }
  }
  return result;
}

function App() {
  const [stations, setStations] = useState(null);
  const [lines, setLines] = useState(null);
  const [result, setResult] = useState('');
  const [progress, setProgress] = useState('');
  const [highlightedEdges, setHighlightedEdges] = useState([]);

  const initializeGraph = async () => {
    try {
      await axios.post('http://localhost:5000/initialize');
      setProgress('Grafo inicializado com sucesso.');
    } catch (error) {
      console.error('Erro ao inicializar o grafo:', error);
    }
  };

  const handleRun = async (problema, algoritmo) => {
    setProgress('Executando algoritmo...');
    try {
      const response = await axios.post('http://localhost:5000/run', {
        problem: problema,
        algorithm: algoritmo
      });
      setResult(`Resultado: ${JSON.stringify(response.data.result)}\nTempo: ${response.data.elapsed_time}s`);
      setProgress('Execução concluída.');

      // Extract edges from the result and update highlightedEdges
      const path = response.data.result;
      console.log('Algorithm result:', path);
      const edges = path.map((node, index) => {
        if (index < path.length - 1) {
          return { source: node, target: path[index + 1] };
        }
        return null;
      }).filter(edge => edge !== null);
      console.log('Processed highlighted edges:', edges);
      setHighlightedEdges(edges);
    } catch (error) {
      console.error('Erro ao executar o algoritmo:', error);
      setProgress('Erro durante a execução.');
    }
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: '#f5f5f5' }}>
      {/* Sidebar */}
      <Box sx={{
        width: 300,
        p: 2,
        borderRight: '1px solid #ddd',
        bgcolor: 'white',
        height: '100%',
        overflowY: 'auto'
      }}>
        <Typography variant="h5" gutterBottom>
          Passe Especial do Metrô de Paris
        </Typography>

        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle1" gutterBottom>Arquivos</Typography>
          <Stack spacing={2}>
            <Box>
              <FileUpload label="Carregar estações" onFileRead={txt => setStations(parseStations(txt))} />
              {stations && (
                <Chip
                  icon={<CheckCircleIcon />}
                  label={`${Object.keys(stations).length} estações carregadas`}
                  color="success"
                  size="small"
                  sx={{ mt: 1 }}
                />
              )}
            </Box>
            <Box>
              <FileUpload label="Carregar linhas" onFileRead={txt => setLines(parseLines(txt))} />
              {lines && (
                <Chip
                  icon={<CheckCircleIcon />}
                  label={`${lines.length} linhas carregadas`}
                  color="success"
                  size="small"
                  sx={{ mt: 1 }}
                />
              )}
            </Box>
          </Stack>
          <button onClick={initializeGraph}>Inicializar Grafo</button>
        </Paper>

        <Paper sx={{ p: 2, mb: 2 }}>
          <AlgoritmoMenu onRun={handleRun} />
          {progress && (
            <Typography variant="body2" sx={{ mt: 2, whiteSpace: 'pre-line', color: 'text.secondary' }}>
              {progress}
            </Typography>
          )}
          {result && (
            <Typography variant="body2" sx={{ mt: 2, whiteSpace: 'pre-line', color: 'text.secondary' }}>
              {result}
            </Typography>
          )}
        </Paper>
      </Box>

      {/* Main Content - Graph */}
      <Box sx={{ flexGrow: 1, p: 2, height: '100%', overflow: 'hidden' }}>
        <Paper sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#fafafa' }}>
          <GraphView stations={stations} lines={lines} highlightedEdges={highlightedEdges} />
        </Paper>
      </Box>
    </Box>
  );
}

export default App;
