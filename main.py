# main.py
from task_handler import route_instruction

if __name__ == "__main__":
    while True:
        user_input = input(" Enter instruction ('exit' to quit): ")
        if user_input.lower() == "exit":
            print("Exiting AI Pipeline.")
            break
        route_instruction(user_input)
