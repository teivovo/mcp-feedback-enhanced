import anyio, os
from mcp_feedback_enhanced.server import server_lifespan, mcp

LOG = os.path.join('logs', 'lifespan_probe.txt')

def append(msg: str):
    os.makedirs('logs', exist_ok=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

async def main():
    append('[TEST] before context')
    async with server_lifespan(mcp):
        append('[TEST] inside context')
    append('[TEST] after context')

anyio.run(main)

