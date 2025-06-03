import React, { useState, useEffect, useRef } from 'react';

import { ForceGraph2D } from 'react-force-graph';

export default function GraphView({ stations, lines }) {
    const containerRef = useRef(null);
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

    useEffect(() => {
        const updateDimensions = () => {
            if (containerRef.current) {
                setDimensions({
                    width: containerRef.current.offsetWidth,
                    height: containerRef.current.offsetHeight,
                });
            }
        };

        updateDimensions();
        window.addEventListener('resize', updateDimensions);

        return () => {
            window.removeEventListener('resize', updateDimensions);
        };
    }, []);

    if (!stations || !lines) {
        return <div>Carregue os arquivos de estações e linhas para visualizar o grafo.</div>;
    }

    // Converte os dados para o formato esperado pelo react-force-graph
    const graphData = {
        nodes: Object.keys(stations).map((name) => ({ id: name, name })),
        links: lines.flatMap((linha) =>
            linha[2].map(([from, to]) => ({ source: from, target: to, label: linha[0] }))
        ),
    };

    return (
        <div ref={containerRef} style={{ width: '100%', height: '100%' }}>
            <ForceGraph2D
                graphData={graphData}
                nodeLabel={(node) => node.name}
                nodeAutoColorBy="id"
                linkDirectionalArrowLength={6}
                linkDirectionalArrowRelPos={1}
                linkLabel={(link) => link.label}
                width={dimensions.width}
                height={dimensions.height}
                nodeCanvasObject={(node, ctx, globalScale) => {
                    const label = node.name;
                    const fontSize = 12 / globalScale;
                    ctx.font = `${fontSize}px Sans-Serif`;
                    ctx.fillStyle = 'black';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(label, node.x, node.y);

                    // Desenha o marcador de vértice (ponto)
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
                    ctx.fillStyle = node.color || 'blue';
                    ctx.fill();
                    ctx.strokeStyle = 'black';
                    ctx.stroke();
                }}
            />
        </div>
    );
}
