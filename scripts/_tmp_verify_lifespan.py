from mcp_feedback_enhanced.server import mcp
print("has_lifespan =", getattr(mcp, "_has_lifespan", None))
print("lifespan_attr_exists =", hasattr(mcp, "lifespan"))
print("mcp_class =", type(mcp).__name__)

