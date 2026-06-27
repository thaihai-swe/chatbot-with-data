# Icon Reference

## Rules for Renderer Compatibility (cairosvg / rsvg-convert)

**Never use** `@import url()` for icon fonts — neither cairosvg nor rsvg-convert fetches external resources.
**Always use** inline SVG `<path>`, `<circle>`, `<rect>`, `<text>` combinations.
**Font fallback**: embed font-family in `<style>` using system fonts only.

---

## Generic Semantic Shapes (No product — use these first)

### Database / Vector Store (cylinder)
```xml
<!-- cx=center-x, top=top-y, w=width, h=height -->
<!-- Typical: w=80, h=70 -->
<ellipse cx="cx" cy="top" rx="w/2" ry="w/6" fill="fill" stroke="stroke" stroke-width="1.5"/>
<rect x="cx-w/2" y="top" width="w" height="h" fill="fill" stroke="none"/>
<line x1="cx-w/2" y1="top" x2="cx-w/2" y2="top+h" stroke="stroke" stroke-width="1.5"/>
<line x1="cx+w/2" y1="top" x2="cx+w/2" y2="top+h" stroke="stroke" stroke-width="1.5"/>
<!-- Optional inner rings for Vector Store -->
<ellipse cx="cx" cy="top+h*0.33" rx="w/2" ry="w/6" fill="none" stroke="stroke" stroke-width="0.7" opacity="0.5"/>
<ellipse cx="cx" cy="top+h*0.66" rx="w/2" ry="w/6" fill="none" stroke="stroke" stroke-width="0.7" opacity="0.5"/>
<ellipse cx="cx" cy="top+h" rx="w/2" ry="w/6" fill="fill-dark" stroke="stroke" stroke-width="1.5"/>
```

### LLM / Model Node (rounded rect with spark)
```xml
<!-- Rounded rect with double border = "intelligent" signal -->
<rect x="x" y="y" width="w" height="h" rx="10" fill="fill" stroke="stroke-outer" stroke-width="2.5"/>
<rect x="x+3" y="y+3" width="w-6" height="h-6" rx="8" fill="none" stroke="stroke-inner" stroke-width="0.8" opacity="0.5"/>
<!-- Spark icon (⚡) as text or small lightning path -->
<text x="cx" y="cy-6" text-anchor="middle" font-size="14">⚡</text>
<text x="cx" y="cy+10" text-anchor="middle" fill="text-color" font-size="13" font-weight="600">LLM</text>
```

### Agent / Orchestrator (hexagon)
```xml
<!-- r = circumradius, cx/cy = center -->
<!-- For r=36: points at 36,0  18,31.2  -18,31.2  -36,0  -18,-31.2  18,-31.2 -->
<polygon points="cx,cy-r  cx+r*0.866,cy-r*0.5  cx+r*0.866,cy+r*0.5  cx,cy+r  cx-r*0.866,cy+r*0.5  cx-r*0.866,cy-r*0.5"
         fill="fill" stroke="stroke" stroke-width="1.5"/>
<text x="cx" y="cy+5" text-anchor="middle" fill="text" font-size="12" font-weight="600">Agent</text>
```

### Memory Node (short-term, dashed border)
```xml
<rect x="x" y="y" width="w" height="h" rx="8"
      fill="fill" stroke="stroke" stroke-width="1.5" stroke-dasharray="6,3"/>
<text x="cx" y="cy-6" text-anchor="middle" fill="text" font-size="10" opacity="0.7">MEMORY</text>
<text x="cx" y="cy+8" text-anchor="middle" fill="text" font-size="13">Short-term</text>
```

### Tool / Function Call (rect with gear symbol)
```xml
<rect x="x" y="y" width="w" height="h" rx="6" fill="fill" stroke="stroke" stroke-width="1.5"/>
<!-- Gear: simplified as ⚙ unicode or small circle with lines -->
<text x="cx" y="cy-4" text-anchor="middle" font-size="16">⚙</text>
<text x="cx" y="cy+12" text-anchor="middle" fill="text" font-size="12">Tool Name</text>
```

### Queue / Stream (horizontal pipe)
```xml
<!-- Pipe tube: left cap ellipse + body + right cap ellipse -->
<ellipse cx="x1" cy="cy" rx="ry*0.6" ry="ry" fill="fill-dark" stroke="stroke" stroke-width="1.5"/>
<rect x="x1" y="cy-ry" width="x2-x1" height="ry*2" fill="fill" stroke="none"/>
<line x1="x1" y1="cy-ry" x2="x2" y2="cy-ry" stroke="stroke" stroke-width="1.5"/>
<line x1="x1" y1="cy+ry" x2="x2" y2="cy+ry" stroke="stroke" stroke-width="1.5"/>
<ellipse cx="x2" cy="cy" rx="ry*0.6" ry="ry" fill="fill-light" stroke="stroke" stroke-width="1.5"/>
```

### User / Human Actor
```xml
<!-- Head -->
<circle cx="cx" cy="cy-18" r="10" fill="fill" stroke="stroke" stroke-width="1.2"/>
<!-- Body / shoulders -->
<path d="M cx-14,cy+16 Q cx-14,cy-4 cx,cy-4 Q cx+14,cy-4 cx+14,cy+16"
      fill="fill" stroke="stroke" stroke-width="1.2"/>
<text x="cx" y="cy+30" text-anchor="middle" fill="text" font-size="12">User</text>
```

### API Gateway (hexagon, single border, smaller)
```xml
<polygon points="cx,cy-28  cx+24,cy-14  cx+24,cy+14  cx,cy+28  cx-24,cy+14  cx-24,cy-14"
         fill="fill" stroke="stroke" stroke-width="1.5"/>
<text x="cx" y="cy+5" text-anchor="middle" fill="text" font-size="11">API</text>
```

### Browser / Web Client
```xml
<rect x="x" y="y" width="w" height="h" rx="6" fill="fill" stroke="stroke" stroke-width="1.5"/>
<!-- Title bar -->
<rect x="x" y="y" width="w" height="20" rx="6" fill="fill-dark" stroke="none"/>
<rect x="x" y="y+14" width="w" height="6" fill="fill-dark"/>
<!-- Traffic light dots -->
<circle cx="x+12" cy="y+10" r="4" fill="#ef4444" opacity="0.8"/>
<circle cx="x+24" cy="y+10" r="4" fill="#eab308" opacity="0.8"/>
<circle cx="x+36" cy="y+10" r="4" fill="#22c55e" opacity="0.8"/>
<!-- Content label -->
<text x="cx" y="y+h*0.6" text-anchor="middle" fill="text" font-size="12">Client</text>
```

### Decision Diamond
```xml
<!-- w=half-width, h=half-height -->
<polygon points="cx,cy-h  cx+w,cy  cx,cy+h  cx-w,cy"
         fill="fill" stroke="stroke" stroke-width="1.5"/>
<text x="cx" y="cy+5" text-anchor="middle" fill="text" font-size="12">Condition?</text>
```

### Graph DB (3-circle cluster)
```xml
<!-- Three overlapping circles representing graph nodes -->
<circle cx="cx" cy="cy-14" r="12" fill="fill" stroke="stroke" stroke-width="1.5"/>
<circle cx="cx-12" cy="cy+8" r="12" fill="fill" stroke="stroke" stroke-width="1.5"/>
<circle cx="cx+12" cy="cy+8" r="12" fill="fill" stroke="stroke" stroke-width="1.5"/>
<!-- Connecting edges -->
<line x1="cx" y1="cy-2" x2="cx-7" y2="cy+8" stroke="stroke" stroke-width="1"/>
<line x1="cx" y1="cy-2" x2="cx+7" y2="cy+8" stroke="stroke" stroke-width="1"/>
<line x1="cx-7" y1="cy+8" x2="cx+7" y2="cy+8" stroke="stroke" stroke-width="1"/>
<text x="cx" y="cy+30" text-anchor="middle" fill="text" font-size="11">Graph DB</text>
```

---

## Product Icons (Text-Based — Renderer Safe)

For all of these, use a rounded rect with the product's brand color as background and a short text label.
The text-only approach is guaranteed to render in cairosvg, rsvg-convert, and Chromium.

### AI/ML Products

| Product | Fill | Stroke | Label |
|---------|------|--------|-------|
| OpenAI | #10a37f | #0d8a6a | OpenAI |
| Anthropic/Claude | #d4956a | #b87a52 | Claude |
| Google Gemini | #4285f4 | #3367cc | Gemini |
| Meta LLaMA | #0866ff | #0052cc | LLaMA |
| Mistral | #ff6f00 | #e55a00 | Mistral |
| Groq | #f55036 | #d43820 | Groq |
| Cohere | #39594a | #2a4035 | Cohere |
| Hugging Face | #ffd21e | #e6b800 | 🤗 HF |

### AI Frameworks

| Product | Fill | Stroke | Label |
|---------|------|--------|-------|
| LangChain | #1c3f5e | #162f47 | LangChain |
| LlamaIndex | #c552b5 | #a33d92 | LlamaIndex |
| LangGraph | #1c3f5e | #162f47 | LangGraph |
| CrewAI | #ff4b4b | #e03a3a | CrewAI |
| AutoGen | #0078d4 | #005ea2 | AutoGen |
| DSPy | #7c3aed | #6027cc | DSPy |
| Mem0 | #6366f1 | #4f52d4 | Mem0 |
| Haystack | #3d9970 | #2e7856 | Haystack |

### Vector DBs

| Product | Fill | Stroke | Label |
|---------|------|--------|-------|
| Pinecone | #1c1c2e | #13131f | Pinecone |
| Weaviate | #fa0050 | #d4003e | Weaviate |
| Qdrant | #dc244c | #b81c3c | Qdrant |
| Chroma | #ff6b35 | #e55520 | Chroma |
| Milvus | #00b5e2 | #0090b8 | Milvus |
| pgvector | #336791 | #245578 | pgvector |

### Databases

| Product | Fill | Stroke | Label |
|---------|------|--------|-------|
| PostgreSQL | #336791 | #245578 | PostgreSQL |
| MySQL | #4479a1 | #34618a | MySQL |
| MongoDB | #47a248 | #358236 | MongoDB |
| Redis | #dc382d | #b52d24 | Redis |
| Neo4j | #018bff | #016ed4 | Neo4j |
| Elasticsearch | #005571 | #003f54 | Elastic |

### Messaging

| Product | Fill | Stroke | Label |
|---------|------|--------|-------|
| Kafka | #000000 | #333333 | Kafka |
| RabbitMQ | #ff6600 | #e55500 | RabbitMQ |

### Cloud / Infra

| Product | Fill | Stroke | Label |
|---------|------|--------|-------|
| AWS | #ff9900 | #e58000 | AWS |
| GCP | #4285f4 | #3367cc | GCP |
| Azure | #0078d4 | #005ea2 | Azure |
| Docker | #2496ed | #1a7acc | Docker |
| Kubernetes | #326ce5 | #2456c4 | K8s |
| Vercel | #000000 | #333333 | Vercel |
| Cloudflare | #f48120 | #d36810 | CF |

### Observability

| Product | Fill | Stroke | Label |
|---------|------|--------|-------|
| Grafana | #f46800 | #d45000 | Grafana |
| Prometheus | #e6522c | #c44020 | Prometheus |
| Datadog | #632ca6 | #4e2282 | Datadog |
| LangSmith | #1c3f5e | #162f47 | LangSmith |
| Langfuse | #7c3aed | #6027cc | Langfuse |

---

## Usage Pattern (Product Icon in a Diagram)

```xml
<!-- Product node box with brand color -->
<rect x="x" y="y" width="w" height="h" rx="8"
      fill="#10a37f" stroke="#0d8a6a" stroke-width="1.5"/>
<text x="cx" y="cy+5" text-anchor="middle"
      fill="#ffffff" font-size="13" font-weight="600">OpenAI</text>

<!-- Or with white box + colored accent border -->
<rect x="x" y="y" width="w" height="h" rx="8"
      fill="#ffffff" stroke="#e5e5e5" stroke-width="1.5"/>
<rect x="x" y="y" width="4" height="h" rx="2" fill="#10a37f"/>
<text x="cx+4" y="cy+5" text-anchor="middle"
      fill="#0d0d0d" font-size="13" font-weight="600">OpenAI</text>
```
