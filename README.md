# 📈 Multi-Agent AI Stock Trading System

An AI-powered stock analysis system that uses multiple agents to analyze real-time financial data and generate BUY / SELL / HOLD decisions.

## 🚀 Overview

This project implements a **multi-agent architecture** where different agents specialize in analyzing various aspects of the stock market:

- 📊 Market Analyst (price trends & indicators)
- 💬 Sentiment Analyst (social/media signals)
- 📰 News Analyst (latest global & company news)
- 📑 Fundamentals Analyst (financial statements)

These agents collaborate through a structured pipeline and a debate system to produce a final investment decision.

## 🧠 Key Features

- Multi-agent system using LangGraph
- Real-time stock data using **yfinance**
- Debate-based reasoning (Bull vs Bear)
- Risk management layer for safer decisions
- Context-aware prompt optimization
- Backend-ready structured outputs
- Fully local LLM support using **Ollama**

## ⚙️ Tech Stack
- Python
- LangChain / LangGraph
- Ollama (LLMs)
- yfinance
- Pandas

## 🔄 System Flow
Market + News + Sentiment + Fundamentals
↓
Bull vs Bear Debate
↓
Research Manager Decision
↓
Risk Management Debate
↓
Final BUY / SELL / HOLD
## 🛠️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/multi-agent-stock-trading-system.git
cd multi-agent-stock-trading-system

