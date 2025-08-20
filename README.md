# Dynamic Baseline Creation System for Enterprise AI Agents

## Overview

The AI Control Tower is a sophisticated ReAct (Reasoning and Acting) agent system that analyzes agent documentation and creates dynamic performance baselines. It processes agent specifications and generates context-aware baseline metrics for performance evaluation, providing customized baseline values based on specific characteristics of each use case.

## Key Features

- **Document Analysis**: Extracts key information from agent documentation and maps technical specifications to relevant metrics
- **ReAct Implementation**: Uses reasoning and acting modules for document analysis and baseline generation  
- **Dynamic Baseline System**: Calculates and adjusts baseline values based on use case requirements and historical performance
- **Comparison Engine**: Compares agent performance against baselines and provides actionable insights
- **REST API**: FastAPI server for easy integration and testing
- **Async Processing**: Support for both synchronous and asynchronous baseline generation

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  User Input     │    │   LangGraph      │    │   OpenAI/LLM    │
│  • Query        │───▶│   Workflow       │◄──▶│   Processing    │
│  • Documents    │    │   Orchestration  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ReAct Agent Workflow                         │
├─────────────────────────────────────────────────────────────────┤
│  1. Document Analysis Tool                                      │
│  2. Baseline Calculation Tool                                   │
│  3. Comparison Analysis Tool                                    │
│  4. Final Report Generation                                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Output Generation                           │
│  • Calculated Baselines                                        │
│  • Technical/Operational/Business Insights                     │
│  • Recommendations                                              │
│  • Readiness Assessment                                         │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. AI Control Tower Agent (`ai_control_tower_agent.py`)

The main agent implements a ReAct workflow with three specialized tools:

#### Document Analysis Tool
- Analyzes agent documentation to extract key performance characteristics
- Identifies capabilities, constraints, and performance targets
- Categorizes complexity levels and domain maturity
- Returns structured JSON analysis

#### Baseline Calculation Tool
- Calculates dynamic baseline values based on document analysis
- Uses predefined baseline ranges from framework
- Prioritizes explicit targets from documentation
- Applies context-aware adjustments

#### Comparison Analysis Tool
- Generates insights and recommendations based on calculated baselines
- Provides category-specific analysis (Technical, Operational, Business)
- Creates readiness assessments across multiple dimensions

### 2. REST API Server (`api_server.py`)

FastAPI server providing endpoints for:

#### Core Endpoints
- `POST /analyze/baseline` - Synchronous baseline generation
- `POST /analyze/baseline/async` - Asynchronous baseline generation  
- `GET /analyze/status/{task_id}` - Check async analysis status
- `GET /framework/ranges` - Get predefined baseline ranges
- `GET /health` - Health check and system status

#### Additional Features
- CORS support for web integration
- Background task processing
- Comprehensive error handling
- Interactive API documentation (Swagger UI)

## Baseline Framework

### Key Metrics Categories

#### Technical Metrics
- **Trajectory Complexity**: 20-80 based on query complexity
- **Tool Utilization**: 40-95% depending on tool maturity

#### Solution Level KPIs  
- **Task Escalation Rate**: 5-40% based on task complexity
- **First Contact Resolution**: 40-90% based on inquiry type

#### Learning and Safety Metrics
- **Improvement Velocity**: 3-20% based on domain stability
- **Guardrail Violations**: 0-5% based on requirement strictness

#### Business Metrics
- **Cost Savings ROI**: 1-10x based on automation potential
- **Customer Satisfaction**: 0-20% improvement based on scenario type

### Dynamic Baseline Logic

1. **Document-Priority**: Uses explicit targets from documentation when available
2. **Context-Adjustment**: Applies domain/complexity factors for variance ranges  
3. **Framework-Fallback**: Uses predefined ranges when no specific targets exist

## Installation & Setup

### Prerequisites
- Python 3.8+
- OpenRouter API key for LLM access

### Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd ai-control-tower

# Install dependencies
pip install -r requirements.txt

# Set environment variables
echo "OPENROUTER_KEY=your_api_key_here" > .env
```

### Required Dependencies
```python
langchain-core
langchain-openai
langgraph
fastapi
uvicorn
pandas
python-dotenv
pydantic
```

## Usage Examples

### 1. Direct Agent Usage

```python
from ai_control_tower_agent import run_ai_control_tower

# Define your query and documentation
query = "Create baseline metrics for a customer service agent"
document = """
Customer Service Agent Specification:
- Handles technical support for cloud services
- Uses knowledge base, ticketing system, and escalation tools  
- Expected to resolve 75% of issues on first contact
- Domain: Mature cloud service support
- Performance targets: <15% escalation rate, >70% CSAT
"""

# Run analysis
result = run_ai_control_tower(query, document)
print(result['final_report'])
```

### 2. API Server Usage

```bash
# Start the API server
python api_server.py

# Server runs on http://localhost:8000
# Documentation: http://localhost:8000/docs
```

#### API Request Example
```bash
curl -X POST "http://localhost:8000/analyze/baseline" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Create baseline metrics for a customer service agent",
    "document_content": "Customer Service Agent Specification: Handles technical support..."
  }'
```

#### Response Format
```json
{
  "success": true,
  "timestamp": "2024-01-20T10:30:00Z",
  "calculated_baselines": {
    "first_contact_resolution": {
      "min": 65.0,
      "max": 80.0, 
      "recommended": 75.0,
      "rationale": "Based on documented target of 75%"
    },
    "task_escalation_rate": {
      "min": 10.0,
      "max": 18.0,
      "recommended": 15.0,
      "rationale": "Based on documented target of <15%"
    }
  },
  "insights": {
    "technical_insights": [...],
    "operational_insights": [...],
    "business_insights": [...],
    "recommendations": [...]
  },
  "readiness_assessment": {
    "technical_readiness": "high",
    "operational_readiness": "medium", 
    "business_readiness": "medium"
  }
}
```

## Example Analysis Flow

### Input Processing
The system processes agent documentation and identifies:
- **Performance Targets**: Explicit numerical goals (75% FCR, <15% escalation)
- **Operational Context**: Technical support for cloud services  
- **Tool Ecosystem**: Well-established tools (knowledge base, ticketing)
- **Domain Maturity**: Mature/stable processes
- **Task Complexity**: Mixed simple and complex issues

### Baseline Generation
1. **Document-Driven**: When explicit targets exist (75% FCR → baseline: 75%, range: 65-80%)
2. **Context-Aware**: Apply complexity factors (complex tasks → trajectory: 40-60)
3. **Framework-Based**: Use predefined ranges for unmapped metrics

### Output Analysis
Generates 7 key baseline metrics across 4 categories:
- 2 Technical Metrics (trajectory complexity, tool utilization)
- 2 Operational KPIs (escalation rate, first contact resolution)
- 1 Learning Metric (improvement velocity)  
- 2 Business Metrics (cost savings ROI, customer satisfaction)

## Technology Stack

- **Orchestration**: LangGraph for workflow management
- **LLM Integration**: OpenAI GPT-4 via OpenRouter
- **API Framework**: FastAPI with async support
- **Tool Framework**: LangChain tools with structured outputs
- **State Management**: TypedDict state management
- **Error Handling**: Comprehensive try-catch with fallback logic

## Advanced Features

### Dynamic Baseline Adaptation
- Prioritizes explicit performance targets from documentation
- Adjusts ranges based on domain maturity and task complexity
- Uses framework defaults when document data is insufficient

### Multi-Dimensional Analysis
- **Technical**: Infrastructure and capability metrics
- **Operational**: Day-to-day performance indicators  
- **Business**: ROI and customer impact measures
- **Learning**: Improvement and safety metrics

### Comprehensive Reporting
- Quantitative baselines with specific numeric targets and ranges
- Qualitative insights with contextual explanations
- Readiness assessments across technical, operational, and business dimensions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following existing code conventions
4. Add tests for new functionality
5. Submit a pull request


## Support

For issues, questions, or contributions:
- Create an issue in the repository
- Refer to API documentation at `/docs` endpoint
- Check system health at `/health` endpoint