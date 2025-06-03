import React, { useState, useEffect, useRef } from 'react';

import { ForceGraph2D } from 'react-force-graph';

export default function GraphView({ stations, lines, highlightedEdges = [] }) {
    const containerRef = useRef(null);
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
    const [graphData, setGraphData] = useState({ nodes: [], links: [] });

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

    useEffect(() => {
        console.log('Highlighted edges received:', highlightedEdges);

        if (stations && lines) {
            const newGraphData = {
                nodes: Object.keys(stations).map((name) => ({ id: name, name })),
                links: lines.flatMap((linha) =>
                    linha[2].map(([from, to]) => {
                        const isHighlighted = highlightedEdges.some(edge => edge.source === from && edge.target === to);
                        return {
                            source: from,
                            target: to,
                            label: linha[0],
                            highlighted: isHighlighted
                        };
                    })
                ),
            };
            console.log('Generated graph data with highlighted edges:', newGraphData);
            setGraphData(newGraphData);
        }
    }, [stations, lines, highlightedEdges]);

    useEffect(() => {
        console.log('Graph data updated, re-rendering graph:', graphData);
    }, [graphData]);

    if (!stations || !lines) {
        return <div>Carregue os arquivos de estações e linhas para visualizar o grafo.</div>;
    }

    return (
        <div ref={containerRef} style={{ width: '100%', height: '100%' }}>
            <ForceGraph2D
                graphData={graphData}
                nodeLabel={(node) => node.name}
                nodeAutoColorBy="id"
                linkDirectionalArrowLength={0} // Disable directional arrows
                linkDirectionalArrowRelPos={0} // Disable arrow positioning
                linkLabel={(link) => link.label}
                width={dimensions.width}
                height={dimensions.height}
                linkCanvasObjectMode={(link) => link.highlighted ? 'after' : 'before'} // Render normal edges before highlighted ones
                linkCanvasObject={(link, ctx, globalScale) => {
                    const isHighlighted = link.highlighted; // Use the highlighted property directly from the graph data
                    
                    if (isHighlighted) {
                        ctx.strokeStyle = 'red';
                        ctx.lineWidth = 1;
                    } else {
                        
                        ctx.strokeStyle = 'gray';
                        ctx.lineWidth = 2;
                    }
                    ctx.beginPath();
                    ctx.moveTo(link.source.x, link.source.y);
                    ctx.lineTo(link.target.x, link.target.y);
                    ctx.stroke();
                }}
                nodeCanvasObject={(node, ctx, globalScale) => {
                    const label = node.name;
                    const fontSize = 12 / globalScale;
                    ctx.font = `${fontSize}px Sans-Serif`;
                    ctx.fillStyle = 'black';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(label, node.x, node.y - 10); // Adjust text position above the vertex marker

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
