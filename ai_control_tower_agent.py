"""
AI Control Tower - ReAct Agent for Dynamic Baseline Creation

This agent analyzes agent documentation and use cases to establish dynamic baselines
for agent metrics, providing customized baseline values based on specific characteristics
of each use case.
"""

import os
import json
import re
from typing import Annotated, Sequence, TypedDict, Dict, Any, List, Optional
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.config import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

class AIControlTowerState(TypedDict):
    """State for the AI Control Tower ReAct workflow"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_query: str
    document_content: str
    use_case_info: Dict[str, Any]
    extracted_metrics: List[Dict[str, Any]]
    baseline_calculations: Dict[str, Any]
    comparison_results: Dict[str, Any]
    final_report: Dict[str, Any]
    error: str

# Baseline ranges from pdp.md
BASELINE_RANGES = {
    "technical_metrics": {
        "trajectory_complexity": {
            "simple_queries": (20, 30),
            "complex_multi_step": (40, 60),
            "highly_specialized": (60, 80)
        },
        "tool_utilization": {
            "well_defined_tools": (80, 95),
            "experimental_tools": (60, 80),
            "unstable_tools": (40, 60)
        }
    },
    "solution_level_kpis": {
        "task_escalation_rate": {
            "simple_tasks": (5, 10),
            "complex_tasks": (15, 25),
            "novel_tasks": (25, 40)
        },
        "first_contact_resolution": {
            "simple_inquiries": (80, 90),
            "complex_issues": (60, 75),
            "technical_problems": (40, 60)
        }
    },
    "learning_safety_metrics": {
        "improvement_velocity": {
            "stable_domain": (3, 5),
            "evolving_domain": (5, 10),
            "new_domain": (10, 20)
        },
        "guardrail_violations": {
            "strict_requirements": (0, 0.5),
            "moderate_requirements": (1, 2),
            "lenient_requirements": (2, 5)
        }
    },
    "business_metrics": {
        "cost_savings": {
            "high_automation_potential": (5, 10),
            "medium_automation": (2, 5),
            "low_automation": (1, 2)
        },
        "customer_satisfaction": {
            "replacement_scenarios": (10, 20),
            "enhancement_scenarios": (5, 15),
            "new_capability_scenarios": (0, 10)
        }
    }
}

# Initialize the LLM
def get_llm():
    """Initialize and return the LLM"""
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=os.getenv("OPENROUTER_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )

@tool
def document_analysis_tool(document_content: str, user_query: str) -> str:
    """
    Analyze agent documentation to extract key performance characteristics.
    
    Args:
        document_content: The content of the agent documentation to analyze
        user_query: The user's query for context
        
    Returns:
        JSON string containing extracted document analysis
    """
    try:
        llm = get_llm()
        
        analysis_prompt = f"""
        You are an expert document analyst for agent performance evaluation.
        
        Analyze the following agent documentation and extract key information:
        
        Document Content: "{document_content}"
        User Query: "{user_query}"
        
        Carefully analyze the document for:
        1. Agent capabilities and limitations
        2. Expected performance targets (look for specific numbers like percentages, rates, etc.)
        3. Technical constraints and requirements
        4. Business objectives and success criteria
        5. Use case complexity assessment
        6. Domain maturity level
        7. Tool ecosystem maturity
        8. Task type complexity
        
        Pay special attention to any numerical performance targets mentioned in the document.
        
        Return a JSON response with the following structure:
        {{
            "agent_capabilities": ["capability1", "capability2"],
            "performance_targets": {{"first_contact_resolution": "75%", "escalation_rate": "<15%", "customer_satisfaction": ">70%"}},
            "technical_constraints": ["constraint1", "constraint2"],
            "business_objectives": ["objective1", "objective2"],
            "complexity_level": "simple|complex|highly_specialized",
            "domain_type": "stable|evolving|new",
            "tool_maturity": "well_defined|experimental|unstable", 
            "task_complexity": "simple|complex|novel",
            "automation_potential": "high|medium|low",
            "scenario_type": "replacement|enhancement|new_capability"
        }}
        """
        
        response = llm.invoke(analysis_prompt)
        
        try:
            # Try to parse as JSON
            result = json.loads(response.content)
            return json.dumps(result)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return json.dumps(result)
                except json.JSONDecodeError:
                    pass
            
            # Fallback to structured text response
            return json.dumps({
                "analysis_text": response.content,
                "complexity_level": "complex",
                "domain_type": "evolving",
                "tool_maturity": "experimental",
                "task_complexity": "complex",
                "automation_potential": "medium",
                "scenario_type": "enhancement"
            })
            
    except Exception as e:
        error_msg = f"Error in document analysis: {str(e)}"
        print(error_msg)
        return json.dumps({"error": error_msg})

@tool  
def baseline_calculation_tool(analysis_json: str, user_query: str) -> str:
    """
    Calculate dynamic baseline values based on document analysis.
    
    Args:
        analysis_json: JSON string containing document analysis results
        user_query: Original user query for context
        
    Returns:
        JSON string containing calculated baseline values
    """
    try:
        analysis = json.loads(analysis_json)
        
        baselines = {}
        
        # Technical Metrics Baselines
        complexity_level = analysis.get("complexity_level", "complex")
        tool_maturity = analysis.get("tool_maturity", "experimental")
        
        # Trajectory Complexity
        if complexity_level == "simple":
            traj_range = BASELINE_RANGES["technical_metrics"]["trajectory_complexity"]["simple_queries"]
        elif complexity_level == "highly_specialized":
            traj_range = BASELINE_RANGES["technical_metrics"]["trajectory_complexity"]["highly_specialized"]
        else:
            traj_range = BASELINE_RANGES["technical_metrics"]["trajectory_complexity"]["complex_multi_step"]
            
        baselines["trajectory_complexity"] = {
            "min": traj_range[0],
            "max": traj_range[1],
            "recommended": (traj_range[0] + traj_range[1]) / 2,
            "rationale": f"Based on {complexity_level} complexity level"
        }
        
        # Tool Utilization
        if tool_maturity == "well_defined":
            tool_range = BASELINE_RANGES["technical_metrics"]["tool_utilization"]["well_defined_tools"]
        elif tool_maturity == "unstable":
            tool_range = BASELINE_RANGES["technical_metrics"]["tool_utilization"]["unstable_tools"]
        else:
            tool_range = BASELINE_RANGES["technical_metrics"]["tool_utilization"]["experimental_tools"]
            
        baselines["tool_utilization"] = {
            "min": tool_range[0],
            "max": tool_range[1],
            "recommended": (tool_range[0] + tool_range[1]) / 2,
            "rationale": f"Based on {tool_maturity} tool maturity"
        }
        
        # Solution Level KPIs
        task_complexity = analysis.get("task_complexity", "complex")
        performance_targets = analysis.get("performance_targets", {})
        
        # Task Escalation Rate - check for performance targets from document
        escalation_target = performance_targets.get("escalation_rate", "")
        
        if escalation_target and ("%" in escalation_target or "<" in escalation_target):
            # Extract percentage from target
            try:
                # Handle formats like "<15%" or "15%"
                target_str = escalation_target.replace("<", "").replace("%", "").strip()
                target_pct = float(target_str)
                # Use document target as baseline
                baselines["task_escalation_rate"] = {
                    "min": max(target_pct - 5, 0),    # At least 0%
                    "max": target_pct + 3,            # Allow some variance
                    "recommended": target_pct,
                    "rationale": f"Based on documented target of {escalation_target}"
                }
            except ValueError:
                # Fall back to complexity-based calculation
                if task_complexity == "simple":
                    escalation_range = BASELINE_RANGES["solution_level_kpis"]["task_escalation_rate"]["simple_tasks"]
                elif task_complexity == "novel":
                    escalation_range = BASELINE_RANGES["solution_level_kpis"]["task_escalation_rate"]["novel_tasks"]
                else:
                    escalation_range = BASELINE_RANGES["solution_level_kpis"]["task_escalation_rate"]["complex_tasks"]
                    
                baselines["task_escalation_rate"] = {
                    "min": escalation_range[0],
                    "max": escalation_range[1],
                    "recommended": (escalation_range[0] + escalation_range[1]) / 2,
                    "rationale": f"Based on {task_complexity} task complexity"
                }
        else:
            # Fall back to complexity-based calculation
            if task_complexity == "simple":
                escalation_range = BASELINE_RANGES["solution_level_kpis"]["task_escalation_rate"]["simple_tasks"]
            elif task_complexity == "novel":
                escalation_range = BASELINE_RANGES["solution_level_kpis"]["task_escalation_rate"]["novel_tasks"]
            else:
                escalation_range = BASELINE_RANGES["solution_level_kpis"]["task_escalation_rate"]["complex_tasks"]
                
            baselines["task_escalation_rate"] = {
                "min": escalation_range[0],
                "max": escalation_range[1],
                "recommended": (escalation_range[0] + escalation_range[1]) / 2,
                "rationale": f"Based on {task_complexity} task complexity"
            }
        
        # First Contact Resolution - check for performance targets from document
        fcr_target = performance_targets.get("first_contact_resolution", "")
        
        if fcr_target and "%" in fcr_target:
            # Extract percentage from target
            try:
                target_pct = float(fcr_target.replace("%", ""))
                # Use document target as baseline, with some variance
                baselines["first_contact_resolution"] = {
                    "min": max(target_pct - 10, 40),  # At least 40%
                    "max": min(target_pct + 5, 95),   # At most 95%
                    "recommended": target_pct,
                    "rationale": f"Based on documented target of {fcr_target}"
                }
            except ValueError:
                # Fall back to complexity-based calculation
                if task_complexity == "simple":
                    fcr_range = BASELINE_RANGES["solution_level_kpis"]["first_contact_resolution"]["simple_inquiries"]
                elif "technical" in user_query.lower():
                    fcr_range = BASELINE_RANGES["solution_level_kpis"]["first_contact_resolution"]["technical_problems"]
                else:
                    fcr_range = BASELINE_RANGES["solution_level_kpis"]["first_contact_resolution"]["complex_issues"]
                    
                baselines["first_contact_resolution"] = {
                    "min": fcr_range[0],
                    "max": fcr_range[1], 
                    "recommended": (fcr_range[0] + fcr_range[1]) / 2,
                    "rationale": f"Based on {task_complexity} inquiry type"
                }
        else:
            # Fall back to complexity-based calculation
            if task_complexity == "simple":
                fcr_range = BASELINE_RANGES["solution_level_kpis"]["first_contact_resolution"]["simple_inquiries"]
            elif "technical" in user_query.lower():
                fcr_range = BASELINE_RANGES["solution_level_kpis"]["first_contact_resolution"]["technical_problems"]
            else:
                fcr_range = BASELINE_RANGES["solution_level_kpis"]["first_contact_resolution"]["complex_issues"]
                
            baselines["first_contact_resolution"] = {
                "min": fcr_range[0],
                "max": fcr_range[1], 
                "recommended": (fcr_range[0] + fcr_range[1]) / 2,
                "rationale": f"Based on {task_complexity} inquiry type"
            }
        
        # Learning and Safety Metrics
        domain_type = analysis.get("domain_type", "evolving")
        
        # Improvement Velocity
        if domain_type == "stable":
            improvement_range = BASELINE_RANGES["learning_safety_metrics"]["improvement_velocity"]["stable_domain"]
        elif domain_type == "new":
            improvement_range = BASELINE_RANGES["learning_safety_metrics"]["improvement_velocity"]["new_domain"]
        else:
            improvement_range = BASELINE_RANGES["learning_safety_metrics"]["improvement_velocity"]["evolving_domain"]
            
        baselines["improvement_velocity"] = {
            "min": improvement_range[0],
            "max": improvement_range[1],
            "recommended": (improvement_range[0] + improvement_range[1]) / 2,
            "rationale": f"Based on {domain_type} domain characteristics"
        }
        
        # Business Metrics
        automation_potential = analysis.get("automation_potential", "medium")
        scenario_type = analysis.get("scenario_type", "enhancement")
        
        # Cost Savings (ROI multiplier)
        if automation_potential == "high":
            cost_range = BASELINE_RANGES["business_metrics"]["cost_savings"]["high_automation_potential"]
        elif automation_potential == "low":
            cost_range = BASELINE_RANGES["business_metrics"]["cost_savings"]["low_automation"]
        else:
            cost_range = BASELINE_RANGES["business_metrics"]["cost_savings"]["medium_automation"]
            
        baselines["cost_savings_roi"] = {
            "min": cost_range[0],
            "max": cost_range[1],
            "recommended": (cost_range[0] + cost_range[1]) / 2,
            "rationale": f"Based on {automation_potential} automation potential"
        }
        
        # Customer Satisfaction Improvement
        if scenario_type == "replacement":
            csat_range = BASELINE_RANGES["business_metrics"]["customer_satisfaction"]["replacement_scenarios"]
        elif scenario_type == "new_capability":
            csat_range = BASELINE_RANGES["business_metrics"]["customer_satisfaction"]["new_capability_scenarios"]
        else:
            csat_range = BASELINE_RANGES["business_metrics"]["customer_satisfaction"]["enhancement_scenarios"]
            
        baselines["customer_satisfaction_improvement"] = {
            "min": csat_range[0],
            "max": csat_range[1],
            "recommended": (csat_range[0] + csat_range[1]) / 2,
            "rationale": f"Based on {scenario_type} scenario type"
        }
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "analysis_inputs": analysis,
            "calculated_baselines": baselines,
            "summary": {
                "total_metrics": len(baselines),
                "complexity_assessment": complexity_level,
                "domain_maturity": domain_type,
                "automation_readiness": automation_potential
            }
        }
        
        return json.dumps(result)
        
    except Exception as e:
        error_msg = f"Error in baseline calculation: {str(e)}"
        print(error_msg)
        return json.dumps({"error": error_msg})

@tool
def comparison_analysis_tool(baseline_json: str, user_query: str) -> str:
    """
    Generate comparison insights and recommendations based on calculated baselines.
    
    Args:
        baseline_json: JSON string containing calculated baseline values
        user_query: Original user query for context
        
    Returns:
        JSON string containing comparison analysis and recommendations
    """
    try:
        baseline_data = json.loads(baseline_json)
        baselines = baseline_data.get("calculated_baselines", {})
        
        # Generate insights for each metric category
        insights = {
            "technical_insights": [],
            "operational_insights": [],
            "business_insights": [],
            "recommendations": []
        }
        
        # Technical Metrics Insights
        if "trajectory_complexity" in baselines:
            traj = baselines["trajectory_complexity"]
            insights["technical_insights"].append(
                f"Trajectory complexity should be {traj['recommended']:.0f} on average "
                f"(range: {traj['min']}-{traj['max']}). {traj['rationale']}."
            )
        
        if "tool_utilization" in baselines:
            tool = baselines["tool_utilization"]
            insights["technical_insights"].append(
                f"Tool utilization should target {tool['recommended']:.0f}% "
                f"(range: {tool['min']}-{tool['max']}%). {tool['rationale']}."
            )
        
        # Operational Insights
        if "task_escalation_rate" in baselines:
            escalation = baselines["task_escalation_rate"]
            insights["operational_insights"].append(
                f"Task escalation rate should be {escalation['recommended']:.1f}% "
                f"(range: {escalation['min']}-{escalation['max']}%). {escalation['rationale']}."
            )
        
        if "first_contact_resolution" in baselines:
            fcr = baselines["first_contact_resolution"]
            insights["operational_insights"].append(
                f"First contact resolution should achieve {fcr['recommended']:.0f}% "
                f"(range: {fcr['min']}-{fcr['max']}%). {fcr['rationale']}."
            )
        
        # Business Insights
        if "cost_savings_roi" in baselines:
            roi = baselines["cost_savings_roi"]
            insights["business_insights"].append(
                f"Expected ROI should be {roi['recommended']:.1f}x "
                f"(range: {roi['min']}-{roi['max']}x). {roi['rationale']}."
            )
        
        if "customer_satisfaction_improvement" in baselines:
            csat = baselines["customer_satisfaction_improvement"]
            insights["business_insights"].append(
                f"Customer satisfaction improvement should be {csat['recommended']:.0f}% "
                f"(range: {csat['min']}-{csat['max']}%). {csat['rationale']}."
            )
        
        # Generate actionable recommendations
        summary = baseline_data.get("summary", {})
        complexity = summary.get("complexity_assessment", "complex")
        domain = summary.get("domain_maturity", "evolving")
        
        if complexity == "simple":
            insights["recommendations"].append("Focus on high throughput and consistent performance metrics")
        elif complexity == "highly_specialized":
            insights["recommendations"].append("Prioritize accuracy and expert-level reasoning capabilities")
        else:
            insights["recommendations"].append("Balance efficiency with comprehensive problem-solving")
        
        if domain == "new":
            insights["recommendations"].append("Plan for rapid learning and adaptation phases")
        elif domain == "stable":
            insights["recommendations"].append("Optimize for reliability and minimal variance")
        else:
            insights["recommendations"].append("Build flexibility for evolving requirements")
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "baseline_summary": summary,
            "insights": insights,
            "metric_count": len(baselines),
            "readiness_assessment": {
                "technical_readiness": "medium" if complexity == "complex" else "high",
                "operational_readiness": "high" if domain == "stable" else "medium",
                "business_readiness": summary.get("automation_readiness", "medium")
            }
        }
        
        return json.dumps(result)
        
    except Exception as e:
        error_msg = f"Error in comparison analysis: {str(e)}"
        print(error_msg)
        return json.dumps({"error": error_msg})

# Initialize tools and LLM
tools = [document_analysis_tool, baseline_calculation_tool, comparison_analysis_tool]
llm_with_tools = get_llm().bind_tools(tools)

def agent(state: AIControlTowerState):
    """Main agent node that decides whether to use tools or generate final report"""
    messages = state["messages"]
    
    # Check which tools have been completed
    tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]
    completed_tools = [msg.name for msg in tool_messages]
    
    # Add system guidance based on progress
    system_prompt = """You are an AI Control Tower agent for dynamic baseline creation. 

Follow this workflow:
1. First, use document_analysis_tool to analyze the agent documentation
2. Then, use baseline_calculation_tool with the analysis results  
3. Finally, use comparison_analysis_tool to generate insights and recommendations

You must complete all three steps in order."""

    if "document_analysis_tool" not in completed_tools:
        system_prompt += "\n\nNext step: Use document_analysis_tool to analyze the provided documentation."
    elif "baseline_calculation_tool" not in completed_tools:
        system_prompt += "\n\nNext step: Use baseline_calculation_tool with the document analysis results."
    elif "comparison_analysis_tool" not in completed_tools:
        system_prompt += "\n\nNext step: Use comparison_analysis_tool with the baseline calculation results."
    else:
        system_prompt += "\n\nAll tools completed. You can now provide a final summary."
    
    # Create messages with system prompt
    guided_messages = [AIMessage(content=system_prompt)] + list(messages)
    
    response = llm_with_tools.invoke(guided_messages)
    return {"messages": [response]}

def should_continue(state: AIControlTowerState):
    """Determine whether to continue to tools or generate final report"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If there are tool calls, continue to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # Check if we have completed all analysis steps
    tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]
    required_tools = ["document_analysis_tool", "baseline_calculation_tool", "comparison_analysis_tool"]
    completed_tools = [msg.name for msg in tool_messages if msg.name in required_tools]
    
    if len(completed_tools) >= 3:
        return "generate_report"
    
    # If we have fewer than 3 tools completed, continue to agent for more tool calls
    if len(completed_tools) < 3:
        return "continue_analysis"
    
    # Otherwise, end the conversation
    return END

def generate_final_report(state: AIControlTowerState) -> AIControlTowerState:
    """Generate the final AI Control Tower report from all tool results"""
    try:
        print("Generating AI Control Tower final report...")
        
        messages = state["messages"]
        user_query = messages[0].content if messages else ""
        
        # Extract tool results from messages
        tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]
        
        document_analysis = {}
        baseline_calculations = {}
        comparison_results = {}
        
        # Process tool results
        tool_results = {}
        for msg in tool_messages:
            tool_results[msg.name] = msg.content
        
        # Extract results
        if "document_analysis_tool" in tool_results:
            document_analysis = json.loads(tool_results["document_analysis_tool"])
        if "baseline_calculation_tool" in tool_results:
            baseline_calculations = json.loads(tool_results["baseline_calculation_tool"])
        if "comparison_analysis_tool" in tool_results:
            comparison_results = json.loads(tool_results["comparison_analysis_tool"])
        
        # Create final report
        final_report = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "analysis": {
                "document_analysis": document_analysis,
                "baseline_calculations": baseline_calculations,
                "comparison_results": comparison_results
            },
            "summary": {
                "total_metrics_analyzed": len(baseline_calculations.get("calculated_baselines", {})),
                "complexity_level": document_analysis.get("complexity_level", "unknown"),
                "domain_type": document_analysis.get("domain_type", "unknown"),
                "readiness_assessment": comparison_results.get("readiness_assessment", {})
            }
        }
        
        return {
            "final_report": final_report,
            "document_content": document_analysis,
            "baseline_calculations": baseline_calculations,
            "comparison_results": comparison_results,
            "user_query": user_query,
            "messages": [AIMessage(content="AI Control Tower baseline analysis completed successfully!")]
        }
        
    except Exception as e:
        error_msg = f"Error in final report generation: {str(e)}"
        print(error_msg)
        return {
            "error": error_msg,
            "final_report": {
                "timestamp": datetime.now().isoformat(),
                "user_query": user_query,
                "error": error_msg
            },
            "messages": [AIMessage(content=f"Error generating report: {error_msg}")]
        }

# Create the tool node
tool_node = ToolNode(tools)

# Create and configure the graph
workflow = StateGraph(AIControlTowerState)

# Add nodes
workflow.add_node("agent", agent)
workflow.add_node("tools", tool_node)
workflow.add_node("generate_report", generate_final_report)

# Add edges
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "generate_report": "generate_report",
        "continue_analysis": "agent",
        END: END,
    },
)
workflow.add_edge("tools", "agent")
workflow.add_edge("generate_report", END)

# Compile the graph
app = workflow.compile()

def run_ai_control_tower(user_query: str, document_content: str = "") -> Dict[str, Any]:
    """
    Run the AI Control Tower agent for dynamic baseline creation
    
    Args:
        user_query: User's query about baseline analysis needs
        document_content: Agent documentation content to analyze
        
    Returns:
        Dictionary containing the complete analysis results
    """
    # If no document content provided, use a sample
    if not document_content:
        document_content = """
        Agent Documentation:
        This customer service agent handles technical support inquiries with moderate complexity.
        It uses well-defined tools for ticket routing and knowledge base search.
        Expected to handle 70% of inquiries without escalation.
        Domain: Established technical support for software products.
        Performance target: 80% first contact resolution.
        """
    
    initial_state = {
        "messages": [HumanMessage(content=f"Analyze this agent documentation and create dynamic baselines: {user_query}. Document: {document_content}")],
        "user_query": user_query,
        "document_content": document_content,
        "use_case_info": {},
        "extracted_metrics": [],
        "baseline_calculations": {},
        "comparison_results": {},
        "final_report": {},
        "error": ""
    }
    
    print("AI Control Tower Agent Starting...\n")
    
    result = app.invoke(initial_state)
    
    print("\n" + "="*60)
    print("AI CONTROL TOWER ANALYSIS COMPLETE")
    print("="*60)
    
    return result

# Example usage
if __name__ == "__main__":
    sample_query = "Create baseline metrics for a customer service agent handling technical support"
    sample_document = """
    Customer Service Agent Specification:
    - Handles technical support for cloud services
    - Uses knowledge base, ticketing system, and escalation tools  
    - Expected to resolve 75% of issues on first contact
    - Domain: Mature cloud service support with well-established processes
    - Task complexity: Mix of simple account issues and complex technical problems
    - Performance targets: <15% escalation rate, >70% CSAT
    """
    
    print(f"Query: {sample_query}\n")
    
    try:
        result = run_ai_control_tower(sample_query, sample_document)
        
        # Print final report
        if result.get('final_report'):
            final_report = result['final_report']
            print(f"\nFINAL BASELINE ANALYSIS:")
            print(f"Query: {final_report.get('user_query', 'N/A')}")
            
            analysis = final_report.get('analysis', {})
            baselines = analysis.get('baseline_calculations', {}).get('calculated_baselines', {})
            
            print(f"\nCALCULATED BASELINES:")
            print("-" * 50)
            for metric, values in baselines.items():
                print(f"{metric.replace('_', ' ').title()}: {values.get('recommended', 0):.1f}")
                print(f"  Range: {values.get('min', 0)}-{values.get('max', 0)}")
                print(f"  Rationale: {values.get('rationale', 'N/A')}")
                print()
            
            # Print insights
            comparison = analysis.get('comparison_results', {})
            insights = comparison.get('insights', {})
            
            if insights:
                print("KEY INSIGHTS:")
                print("-" * 50)
                for category, insight_list in insights.items():
                    if insight_list:
                        print(f"\n{category.replace('_', ' ').title()}:")
                        for insight in insight_list:
                            print(f"• {insight}")
            
            # Print readiness assessment
            readiness = comparison.get('readiness_assessment', {})
            if readiness:
                print(f"\nREADINESS ASSESSMENT:")
                print("-" * 50)
                for area, level in readiness.items():
                    print(f"{area.replace('_', ' ').title()}: {level.upper()}")
                    
        else:
            print("No final report generated")
            
    except Exception as e:
        print(f"Error: {e}")