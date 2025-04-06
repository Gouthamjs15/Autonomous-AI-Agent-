# task_handler.py
from instruction_parser import parse_instruction
from terminal_execution import run_terminal_command
from Browser_automation import run_pipeline

def route_instruction(instruction):
    parsed = parse_instruction(instruction)

    print("\n[🧠] Parsed Intent:", parsed["intent"])
    print(f"[📊] Confidence Score: {parsed['score']:.2f}")
    print("[⚡] Matched Label:", parsed["label"])
    print("[📜] Commands:", parsed["commands"])

    # ✅ Terminal Instruction Handler
    if parsed["intent"] == "terminal":
        if parsed["commands"]:
            for cmd in parsed["commands"]:
                result = run_terminal_command(cmd)
                if result["success"]:
                    print(f"[✅] Output for '{cmd}':\n{result['stdout']}")
                else:
                    print(f"[❌] Error for '{cmd}':\n{result['stderr']}")
        else:
            print("[⚠️] No valid terminal commands found.")

    # 🌐 Web Instruction Handler
    elif parsed["intent"] == "web":
        if parsed["commands"]:
            print(f"[🚀] Executing Web Pipeline for: '{instruction}'")
            run_pipeline(instruction, parsed["intent"], parsed["commands"])
        else:
            print("[⚠️] No valid web commands found.")

    # 📁 File Handler Instructions
    elif parsed["intent"] == "file_handler":
        if parsed["commands"]:
            from file_system_handler import handle_file_commands
            print(f"[📂] Handling file operation: '{instruction}'")
            handle_file_commands(instruction, parsed["commands"])
        else:
            print("[⚠️] No valid file handling commands found.")

    # 🤷 Fallback
    else:
        print("[❓] Unknown intent. Try rephrasing the instruction.")
