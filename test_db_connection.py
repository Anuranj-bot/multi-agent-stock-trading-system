from tradingagents.database.db_service import fetch_pending_request

request = fetch_pending_request()

print("Fetched request from database:")
print(request)