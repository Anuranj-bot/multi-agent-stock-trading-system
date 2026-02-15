# tradingagents/graph/trading_graph.py

import os
import json
from pathlib import Path
from typing import Dict, Any


from langchain_community.chat_models import ChatOllama

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.config import set_config
from tradingagents.dataflows.validator import validate_nifty50_symbol

from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)

from tradingagents.agents.utils.agent_utils import (
    get_stock_data,
    get_indicators,
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement,
    get_news,
    get_global_news,
    get_insider_sentiment,
    get_insider_transactions,
)

from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor


class TradingAgentsGraph:
    """
    MAIN orchestration class.
    FREE MODE: OLLAMA ONLY.
    """

    def __init__(
        self,
        selected_analysts=("market", "social", "news", "fundamentals"),
        debug: bool = False,
        config: Dict[str, Any] | None = None,
    ):
        self.debug = debug
        self.config = config or DEFAULT_CONFIG

        # ----------------------------------
        # CONFIG
        # ----------------------------------
        set_config(self.config)

        os.makedirs(
            os.path.join(self.config["project_dir"], "dataflows/data_cache"),
            exist_ok=True,
        )

        # ----------------------------------
        # LLM (OLLAMA ONLY)
        # ----------------------------------
        if self.config["llm_provider"].lower() != "ollama":
            raise RuntimeError(
                "Only Ollama is supported in FREE mode. "
                "Set llm_provider='ollama' in default_config.py"
            )

        self.deep_thinking_llm = ChatOllama(
            model=self.config["deep_think_llm"],
            base_url=self.config["backend_url"],
            temperature=0.2,
        )

        self.quick_thinking_llm = ChatOllama(
            model=self.config["quick_think_llm"],
            base_url=self.config["backend_url"],
            temperature=0.2,
        )

        # ----------------------------------
        # MEMORY (LOCAL / CHROMADB)
        # ----------------------------------
        self.bull_memory = FinancialSituationMemory("bull_memory", self.config)
        self.bear_memory = FinancialSituationMemory("bear_memory", self.config)
        self.trader_memory = FinancialSituationMemory("trader_memory", self.config)
        self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", self.config)
        self.risk_manager_memory = FinancialSituationMemory("risk_manager_memory", self.config)

        # ----------------------------------
        # TOOLS
        # ----------------------------------

        # ----------------------------------
        # GRAPH COMPONENTS
        # ----------------------------------
        self.conditional_logic = ConditionalLogic()

        self.graph_setup = GraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            None,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
        )

        self.propagator = Propagator()
        self.reflector = Reflector(self.quick_thinking_llm)
        self.signal_processor = SignalProcessor(self.quick_thinking_llm)

        self.curr_state = None
        self.ticker = None
        self.log_states_dict = {}

        self.graph = self.graph_setup.setup_graph(selected_analysts)

    # ==================================================
    # TOOL NODES
    # ==================================================
   
    # ==================================================
    # RUN GRAPH
    # ==================================================
    def propagate(self, company_name: str, trade_date: str):
        """
        Run the trading agents graph
        """

        # Validate + normalize NIFTY ticker
        self.ticker = validate_nifty50_symbol(company_name)

        init_state = self.propagator.create_initial_state(
            self.ticker, trade_date
        )
        args = self.propagator.get_graph_args()

        if self.debug:
            trace = []
            for chunk in self.graph.stream(init_state, **args):
                if chunk.get("messages"):
                    chunk["messages"][-1].pretty_print()
                trace.append(chunk)
            final_state = trace[-1]
        else:
            final_state = self.graph.invoke(init_state, **args)

        self.curr_state = final_state
        self._log_state(trade_date, final_state)

        return final_state, self.process_signal(
            final_state["final_trade_decision"]
        )

    # ==================================================
    # LOGGING
    # ==================================================
    def _log_state(self, trade_date, final_state):
        self.log_states_dict[str(trade_date)] = final_state

        out_dir = Path(
            f"eval_results/{self.ticker}/TradingAgentsStrategy_logs"
        )
        out_dir.mkdir(parents=True, exist_ok=True)

        with open(
            out_dir / f"full_states_log_{trade_date}.json", "w"
        ) as f:
            json.dump(self.log_states_dict, f, indent=2)

    # ==================================================
    # LEARNING
    # ==================================================
    def reflect_and_remember(self, returns_losses):
        self.reflector.reflect_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        self.reflector.reflect_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        self.reflector.reflect_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        self.reflector.reflect_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    def process_signal(self, full_signal):
        return self.signal_processor.process_signal(full_signal)
