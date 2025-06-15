# tools.py
TOOLS = {}

def tool(name=None):
    def decorator(func):
        key = name or func.__name__
        TOOLS[key] = func
        return func
    return decorator

@tool("<time>")
def get_time():
    from datetime import datetime
    now = datetime.now()
    return f"The today date is {now.date()} and current time is {now.time()}"

@tool("<joke>")
def tell_joke():
    return "Reply this without modification: 'Why did the accountant break up with the calculator? It couldn’t count on it!'"

@tool("<analyze>")
def analyze_stock():
    return "You are currently holding yes bank 100 shares, wipro 5 shares, mutual fund 2 units of Motilal oswal."

def call_tool_from_input(input_text):
    for key in TOOLS:
        if f"{key}" in input_text:
            result = TOOLS[key]()
            return {
                "name": key,
                "output": result
            }
    return None
