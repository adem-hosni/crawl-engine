import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import traceback
from config.logger import get_logger
from graph.workflow import build_graph
from execution.browser import driver
from dotenv import load_dotenv


logger = get_logger("main")


def main():
    load_dotenv()

    # 1. Validation
    if not os.environ.get("OPENROUTER_API_KEY"):
        logger.error("OPENROUTER_API_KEY not found in environment.")
        return

    logger.info("--- 🚀 DEEP AGENT SAAS: STARTING ---")

    # 2. Build Graph
    try:
        app = build_graph()
        logger.info("Graph built successfully.")
    except Exception as e:
        logger.critical(f"Failed to build graph: {e}")
        traceback.print_exc()
        return

    # 3. User Mission
    user_goal = "Create an account on discord. use ademhosni400@icloud.com as an email"

    initial_state = {
        "messages": [],
        "user_goal": user_goal,
        "retry_count": 0,
        "status": "running",
        "clean_dom": "",
        "interactive_elements": {},
        "last_action": "",
    }

    logger.info("--- AGENT RUNNING (Check Chrome) ---")

    # We use a flag to manage the visual line breaks between streaming text and logs
    is_streaming_text = False

    try:
        # 4. THE DUAL-STREAM LOOP
        # "messages" -> Yields individual tokens (characters) for streaming
        # "updates"  -> Yields full state updates when a node finishes (for logging)
        for mode, payload in app.stream(
            initial_state,
            stream_mode=["messages", "updates"],
            config={"configurable": {"thread_id": "session_1"}},
        ):

            # =================================================
            # MODE 1: STREAMING (The "Matrix" Effect)
            # =================================================
            if mode == "messages":
                chunk, metadata = payload
                node_name = metadata.get("langgraph_node", "")

                # Only stream text from the Strategist (LLM)
                if node_name == "strategist" and chunk.content:
                    # If we weren't streaming before, print the "THOUGHT" header
                    if not is_streaming_text:
                        sys.stdout.write("\n🧠 THOUGHT: ")
                        is_streaming_text = True

                    sys.stdout.write(chunk.content)
                    sys.stdout.flush()

            # =================================================
            # MODE 2: UPDATES (The System Logs)
            # =================================================
            elif mode == "updates":
                # If we were just streaming text, finish the line
                if is_streaming_text:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    is_streaming_text = False

                # Iterate through the node that just finished
                for node_name, values in payload.items():

                    # --- Strategist Finished (Log Tool Decisions) ---
                    if node_name == "strategist":
                        if "messages" in values:
                            last_msg = values["messages"][-1]
                            # Check for tool calls (they don't stream as text)
                            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                                tool = last_msg.tool_calls[0]
                                logger.info(
                                    f"⚡ ACTION: Using '{tool['name']}' with args: {tool['args']}"
                                )

                    # --- Executor Finished (Log Tool Outputs) ---
                    elif node_name == "executor":
                        if "messages" in values:
                            # Tool messages can be a list, iterate them
                            for msg in values["messages"]:
                                logger.info(f"🛠️ TOOL OUTPUT: {msg.content}")

                    # --- Perception Finished (Log Scans) ---
                    elif node_name == "perception":
                        url = values.get("current_url", "Unknown")
                        logger.info(f"👀 PERCEPTION: Scanned {url}")

    except KeyboardInterrupt:
        if is_streaming_text:
            print()  # Clean newline
        logger.warning("User stopped the agent.")
    except Exception as e:
        if is_streaming_text:
            print()
        logger.error(f"CRASH: {e}")
        traceback.print_exc()
    finally:
        logger.info("Press Enter to close browser...")
        input()
        driver.quit()
        logger.info("Browser closed.")


if __name__ == "__main__":
    main()
else:
    graph = build_graph()
