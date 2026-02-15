from typing import Dict, Any

from langgraph.graph import END, StateGraph, START

from tradingagents.agents import *
from tradingagents.agents.utils.agent_states import AgentState
from .conditional_logic import ConditionalLogic


class GraphSetup:
    """Handles the setup and configuration of the agent graph."""

    def __init__(
        self,
        quick_thinking_llm,
        deep_thinking_llm,
        tool_nodes,  # CAN BE None
        bull_memory,
        bear_memory,
        trader_memory,
        invest_judge_memory,
        risk_manager_memory,
        conditional_logic: ConditionalLogic,
    ):
        self.quick_thinking_llm = quick_thinking_llm
        self.deep_thinking_llm = deep_thinking_llm
        self.tool_nodes = tool_nodes  # None when using Ollama
        self.bull_memory = bull_memory
        self.bear_memory = bear_memory
        self.trader_memory = trader_memory
        self.invest_judge_memory = invest_judge_memory
        self.risk_manager_memory = risk_manager_memory
        self.conditional_logic = conditional_logic

    def setup_graph(self, selected_analysts):
        if not selected_analysts:
            raise ValueError("No analysts selected!")

        use_tools = self.tool_nodes is not None

        workflow = StateGraph(AgentState)

        analyst_nodes = {}
        delete_nodes = {}

        # =========================
        # Create analyst nodes
        # =========================
        if "market" in selected_analysts:
            analyst_nodes["market"] = create_market_analyst(self.quick_thinking_llm)
            delete_nodes["market"] = create_msg_delete()

        if "social" in selected_analysts:
            analyst_nodes["social"] = create_social_media_analyst(self.quick_thinking_llm)
            delete_nodes["social"] = create_msg_delete()

        if "news" in selected_analysts:
            analyst_nodes["news"] = create_news_analyst(self.quick_thinking_llm)
            delete_nodes["news"] = create_msg_delete()

        if "fundamentals" in selected_analysts:
            analyst_nodes["fundamentals"] = create_fundamentals_analyst(self.quick_thinking_llm)
            delete_nodes["fundamentals"] = create_msg_delete()

        # =========================
        # Add analyst nodes
        # =========================
        for analyst, node in analyst_nodes.items():
            workflow.add_node(f"{analyst.capitalize()} Analyst", node)
            workflow.add_node(f"Msg Clear {analyst.capitalize()}", delete_nodes[analyst])

            if use_tools:
                workflow.add_node(f"tools_{analyst}", self.tool_nodes[analyst])

        # =========================
        # Research + trader nodes
        # =========================
        workflow.add_node("Bull Researcher", create_bull_researcher(self.quick_thinking_llm, self.bull_memory))
        workflow.add_node("Bear Researcher", create_bear_researcher(self.quick_thinking_llm, self.bear_memory))
        workflow.add_node("Research Manager", create_research_manager(self.deep_thinking_llm, self.invest_judge_memory))
        workflow.add_node("Trader", create_trader(self.quick_thinking_llm, self.trader_memory))

        workflow.add_node("Risky Analyst", create_risky_debator(self.quick_thinking_llm))
        workflow.add_node("Neutral Analyst", create_neutral_debator(self.quick_thinking_llm))
        workflow.add_node("Safe Analyst", create_safe_debator(self.quick_thinking_llm))
        workflow.add_node("Risk Judge", create_risk_manager(self.deep_thinking_llm, self.risk_manager_memory))

        # =========================
        # Edges
        # =========================
        first = selected_analysts[0]
        workflow.add_edge(START, f"{first.capitalize()} Analyst")

        for i, analyst in enumerate(selected_analysts):
            analyst_node = f"{analyst.capitalize()} Analyst"
            clear_node = f"Msg Clear {analyst.capitalize()}"

            if use_tools:
                tools_node = f"tools_{analyst}"
                workflow.add_conditional_edges(
                    analyst_node,
                    getattr(self.conditional_logic, f"should_continue_{analyst}"),
                    [tools_node, clear_node],
                )
                workflow.add_edge(tools_node, analyst_node)
            else:
                workflow.add_edge(analyst_node, clear_node)

            if i < len(selected_analysts) - 1:
                workflow.add_edge(clear_node, f"{selected_analysts[i+1].capitalize()} Analyst")
            else:
                workflow.add_edge(clear_node, "Bull Researcher")

        # =========================
        # Debate + risk flow
        # =========================
        workflow.add_conditional_edges(
            "Bull Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bear Researcher": "Bear Researcher",
                "Research Manager": "Research Manager",
            },
        )
        workflow.add_conditional_edges(
            "Bear Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bull Researcher": "Bull Researcher",
                "Research Manager": "Research Manager",
            },
        )

        workflow.add_edge("Research Manager", "Trader")
        workflow.add_edge("Trader", "Risky Analyst")

        workflow.add_conditional_edges(
            "Risky Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Safe Analyst": "Safe Analyst",
                "Risk Judge": "Risk Judge",
            },
        )
        workflow.add_conditional_edges(
            "Safe Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Neutral Analyst": "Neutral Analyst",
                "Risk Judge": "Risk Judge",
            },
        )
        workflow.add_conditional_edges(
            "Neutral Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Risky Analyst": "Risky Analyst",
                "Risk Judge": "Risk Judge",
            },
        )

        workflow.add_edge("Risk Judge", END)

        return workflow.compile()
