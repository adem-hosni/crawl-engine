import os
import traceback
from graph.workflow import build_graph
from execution.browser import driver
from dotenv import load_dotenv


def main():
    load_dotenv()
    
    # 1. Check API Key
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("❌ ERROR: OPENROUTER_API_KEY not found in environment.")
        return

    print("--- 🚀 DEEP AGENT SAAS: STARTING ---")

    # 2. Build the Machine
    app = build_graph()

    # 3. Get User Mission
    user_goal = "Login to my instagram, email: hyper_x86@proton.me password: XXXXX"

    # 4. Initialize State
    initial_state = {
        "messages": [],  # LangGraph handles history here
        "user_goal": user_goal,
        "retry_count": 0,
        "status": "running",
        "clean_dom": "",
        "interactive_elements": {},
        "last_action": "",
    }

    # 5. Run the Loop
    # recursion_limit=50 prevents infinite loops if the agent gets stuck
    print("\n--- AGENT RUNNING (Check the Chrome Window) ---")

    try:
        for event in app.stream(initial_state, config={"recursion_limit": 50}):

            # PARSE EVENTS FOR CLEAN OUTPUT
            for node_name, values in event.items():

                # If it's the Strategist (LLM) talking
                if node_name == "strategist":
                    last_msg = values["messages"][-1]
                    # Check if it called a tool
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        tool_name = last_msg.tool_calls[0]["name"]
                        tool_args = last_msg.tool_calls[0]["args"]
                        print(
                            f"\n🧠 THOUGHT: I need to use '{tool_name}' with {tool_args}"
                        )
                    else:
                        print(f"\n🧠 THOUGHT: {last_msg.content}")

                # If it's the Executor (Tools) returning data
                elif node_name == "executor":
                    # ToolNode returns a list of ToolMessages
                    tool_msgs = values["messages"]
                    for tm in tool_msgs:
                        print(f"🛠️ TOOL OUTPUT: {tm.content}")

                # If it's Perception
                elif node_name == "perception":
                    url = values.get("current_url", "Unknown")
                    print(f"👀 PERCEPTION: Scanned {url}")

    except KeyboardInterrupt:
        print("\n🛑 User stopped the agent.")
    except Exception as e:
        print(f"\n❌ CRASH: {e}")
        traceback.print_exc()
    finally:
        print("\nPress Enter to close browser...")
        input()
        driver.quit()


if __name__ == "__main__":
    main()
