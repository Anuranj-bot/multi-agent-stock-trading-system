# ===============================
# SAFE IMPORTS
# ===============================
from tradingagents.agents.utils.safety import trim, safe_get, safe_memory_extract


# ===============================
# RESEARCH MANAGER (SAFE VERSION)
# ===============================

def create_research_manager(llm, memory):

    def research_manager_node(state) -> dict:

        # --------------------------------
        # SAFE STATE EXTRACTION
        # --------------------------------
        investment_debate_state = safe_get(state, "investment_debate_state", {})

        history = trim(safe_get(investment_debate_state, "history", ""), 3000)
        bull_history = safe_get(investment_debate_state, "bull_history", "")
        bear_history = safe_get(investment_debate_state, "bear_history", "")
        count = safe_get(investment_debate_state, "count", 0)

        # --------------------------------
        # SAFE REPORT EXTRACTION
        # --------------------------------
        market_research_report = trim(safe_get(state, "market_report", ""), 1500)
        sentiment_report = trim(safe_get(state, "sentiment_report", ""), 1200)
        news_report = trim(safe_get(state, "news_report", ""), 1200)
        fundamentals_report = trim(safe_get(state, "fundamentals_report", ""), 1500)

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
You are the Research Manager.

Your job:
1. Briefly summarize the strongest bull argument.
2. Briefly summarize the strongest bear argument.
3. Make a clear decision: BUY, SELL, or HOLD.
4. Provide a short actionable investment plan.

Be decisive.
Do NOT default to HOLD unless strongly justified.
Keep response concise but strategic.

Debate History:
{history}

Lessons from past similar trades:
{past_memory_str}
"""

        response = llm.invoke(prompt)

        final_decision_text = trim(response.content, 2000)

        # --------------------------------
        # SAFE STATE UPDATE
        # --------------------------------
        new_state = {
            "judge_decision": final_decision_text,
            "history": history,
            "bull_history": bull_history,
            "bear_history": bear_history,
            "current_response": final_decision_text,
            "count": count,
        }

        return {
            "investment_debate_state": new_state,
            "investment_plan": final_decision_text,
        }

    return research_manager_node
