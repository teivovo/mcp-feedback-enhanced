import os
from mcp_feedback_enhanced.server import mcp
os.environ['MCP_WEB_PORT'] = '8899'
try:
    mcp.run(transport="http", host="127.0.0.1", port=8899)
except KeyboardInterrupt:
    pass

