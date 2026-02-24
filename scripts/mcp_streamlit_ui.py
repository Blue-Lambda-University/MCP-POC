"""Streamlit UI for the MCP server: connect, pick tool, form or JSON, run, view result."""

import base64
import io
import json
import sys
from pathlib import Path

# Ensure project root is on path when run as __main__ (so scripts package is importable)
if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

import streamlit as st

from scripts.client_helper import (
    call_tool,
    default_mcp_url,
    format_tool_result,
    get_result_image_base64,
    list_tools,
)


def ensure_tools():
    if "mcp_tools" not in st.session_state:
        st.session_state.mcp_tools = None
    if "mcp_error" not in st.session_state:
        st.session_state.mcp_error = None


def fetch_tools(url: str):
    ensure_tools()
    try:
        st.session_state.mcp_tools = list_tools(url)
        st.session_state.mcp_error = None
    except Exception as e:
        st.session_state.mcp_tools = []
        st.session_state.mcp_error = str(e)


def main():
    st.set_page_config(page_title="Playwright MCP Client", page_icon="🌐", layout="wide")
    st.title("Playwright MCP Client")
    st.caption("Call tools on the Playwright MCP server (start it with `playwright-mcp` first).")

    ensure_tools()
    url = st.sidebar.text_input("MCP server URL", value=default_mcp_url(), key="mcp_url")
    if st.sidebar.button("Connect / Refresh tools"):
        with st.spinner("Connecting..."):
            fetch_tools(url)
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()

    if st.session_state.mcp_error:
        st.sidebar.error(st.session_state.mcp_error)
    if not st.session_state.mcp_tools:
        st.info("Enter the MCP server URL and click **Connect / Refresh tools**. Ensure the server is running (`playwright-mcp`).")
        return

    tools = st.session_state.mcp_tools
    tool_names = [t.get("name", "") for t in tools if t.get("name")]
    selected = st.selectbox("Select a tool", options=tool_names, key="tool_select")
    if not selected:
        return

    tool_info = next((t for t in tools if t.get("name") == selected), None)
    if tool_info:
        st.sidebar.markdown(f"**{selected}**")
        st.sidebar.markdown(tool_info.get("description") or "(no description)")

    use_json = st.checkbox("Edit as JSON (advanced)", value=False, key="use_json")
    if use_json:
        default_json = "{}"
        schema = (tool_info or {}).get("inputSchema")
        if schema and schema.get("properties"):
            if "params" in schema.get("properties", {}):
                default_json = json.dumps({"params": {}}, indent=2)
            else:
                default_json = json.dumps({p: "" for p in schema.get("properties", {})}, indent=2)
        args_text = st.text_area("Arguments (JSON)", value=default_json, height=120, key="args_json")
        try:
            arguments = json.loads(args_text) if args_text.strip() else {}
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
            arguments = None
    else:
        arguments = {}
        if selected == "browser_navigate":
            u = st.text_input("URL", value="https://example.com", key="nav_url")
            arguments = {"params": {"url": u}}
        elif selected == "browser_scrape":
            u = st.text_input("URL", value="https://example.com", key="scrape_url")
            fmt = st.selectbox("Format", ["text", "html", "links"], key="scrape_fmt")
            sel = st.text_input("Selector (optional)", value="", key="scrape_sel")
            wait_ms = st.number_input("Wait (ms, optional)", min_value=0, value=0, key="scrape_wait")
            arguments = {"params": {"url": u or None, "format": fmt, "selector": sel or None, "wait_ms": wait_ms or None}}
            arguments["params"] = {k: v for k, v in arguments["params"].items() if v is not None}
        elif selected == "browser_click":
            sel = st.text_input("CSS selector", value="button", key="click_sel")
            arguments = {"params": {"selector": sel}}
        elif selected == "browser_type":
            sel = st.text_input("CSS selector", value="input", key="type_sel")
            txt = st.text_input("Text", value="hello", key="type_txt")
            arguments = {"params": {"selector": sel, "text": txt}}
        elif selected == "browser_screenshot":
            full = st.checkbox("Full page", value=False, key="ss_full")
            sel = st.text_input("Selector (optional)", value="", key="ss_sel")
            arguments = {"params": {"full_page": full, "selector": sel or None}}
        else:
            st.info("Use **Edit as JSON** to pass arguments for this tool.")
            arguments = {}

    if st.button("Run tool", key="run_btn") and arguments is not None:
        with st.spinner("Calling..."):
            try:
                result = call_tool(selected, arguments, url)
                text_out = format_tool_result(result)
                st.subheader("Result")
                st.text_area("Output", value=text_out, height=200, key="result_out", disabled=True)
                img_b64 = get_result_image_base64(result)
                if img_b64:
                    try:
                        buf = io.BytesIO(base64.b64decode(img_b64))
                        st.image(buf, caption="Screenshot")
                    except Exception:
                        st.caption("(Could not display image)")
            except Exception as e:
                st.error(str(e))


def run_ui():
    """Entry point for playwright-mcp-ui: run Streamlit app."""
    import subprocess
    app_file = Path(__file__).resolve()
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(app_file),
        "--server.headless", "true",
    ], check=False)


if __name__ == "__main__":
    main()
