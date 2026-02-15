# ===============================
# SAFE IMPORTS
# ===============================
from tradingagents.agents.utils.safety import trim, safe_get, safe_memory_extract


# ===============================
# RISK MANAGER (SAFE VERSION)
# ===============================

def create_risk_manager(llm, memory):

    def risk_manager_node(state) -> dict:

        # --------------------------------
        # SAFE STATE EXTRACTION
        # --------------------------------
        risk_debate_state = safe_get(state, "risk_debate_state", {})

        history = trim(safe_get(risk_debate_state, "history", ""), 3000)
        risky_history = safe_get(risk_debate_state, "risky_history", "")
        safe_history = safe_get(risk_debate_state, "safe_history", "")
        neutral_history = safe_get(risk_debate_state, "neutral_history", "")
        count = safe_get(risk_debate_state, "count", 0)

        # --------------------------------
        # SAFE REPORT EXTRACTION
        # --------------------------------
        market_research_report = trim(safe_get(state, "market_report", ""), 1200)
        sentiment_report = trim(safe_get(state, "sentiment_report", ""), 1000)
        news_report = trim(safe_get(state, "news_report", ""), 1000)
        fundamentals_report = trim(safe_get(state, "fundamentals_report", ""), 1200)

        trader_plan = trim(safe_get(state, "investment_plan", ""), 1500)

        curr_situation = (
            market_research_report
            + "\n\n"
            + sentiment_report
            + "\n\n"
            + news_report
            + "\n\n"
            + fundamentals_report
        )

        # --------------------------------
        # SAFE MEMORY EXTRACTION
        # --------------------------------
        try:
            past_memories_raw = memory.get_memories(curr_situation, n_matches=2)
            past_memory_str = safe_memory_extract(past_memories_raw, 800)
        except Exception:
            past_memory_str = ""

        # --------------------------------
        # CONTROLLED PROMPT
        # --------------------------------
        prompt = f"""
You are the Risk Management Judge.

Your job:
1. Briefly evaluate the risk debate.
2. Consider the trader's proposed plan.
3. Learn from past mistakes.
4. Make a FINAL decision: BUY, SELL, or HOLD.

Be decisive.
Only choose HOLD if strongly justified.
Keep response concise and actionable.

Trader Plan:
{trader_plan}

Risk Debate History:
{history}

Lessons from past similar trades:
{past_memory_str}
"""

        response = llm.invoke(prompt)

        final_decision = trim(response.content, 2000)

        # --------------------------------
        # SAFE STATE UPDATE
        # --------------------------------
        new_risk_state = {
            "judge_decision": final_decision,
            "history": history,
            "risky_history": risky_history,
            "safe_history": safe_history,
            "neutral_history": neutral_history,
            "latest_speaker": "Judge",
            "current_risky_response": safe_get(risk_debate_state, "current_risky_response", ""),
            "current_safe_response": safe_get(risk_debate_state, "current_safe_response", ""),
            "current_neutral_response": safe_get(risk_debate_state, "current_neutral_response", ""),
            "count": count,
        }

        return {
            "risk_debate_state": new_risk_state,
            "final_trade_decision": final_decision,
        }

    return risk_manager_node
