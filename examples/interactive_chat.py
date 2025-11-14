"""
Interactive Chat Interface Example

This script demonstrates the conversational interface for
retrieving Expression Atlas data.
"""

from chat_interface import ExpressionAtlasChat

# Simply create a chat instance and start
chat = ExpressionAtlasChat()

# The chat interface will:
# 1. Ask if you have a specific experiment ID
# 2. If not, ask about species
# 3. Ask about experiment type (baseline vs differential)
# 4. Ask for search keywords
# 5. Ask where to save files
# 6. Summarize requirements and confirm
# 7. Download the data

chat.start()
