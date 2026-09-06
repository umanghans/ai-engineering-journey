import litellm
import json
import datetime
from zoneinfo import ZoneInfo

messages=[
	{
		"role":"user",
		"content":"What time is it currently in Tokyo, and what is 4387 * 927?"
	}
]

def get_current_time(timezone: str) -> str:
    try:
        now = datetime.datetime.now(ZoneInfo(timezone))
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as exc:
        return f"ERROR: {exc}"

def calculator(expression:str)->str:
	allowed = set("0123456789+-*/(). ")
	if not set(expression)<=allowed:
		return "ERROR: Unsupported characters."
	return str(eval(expression,{"__builtins__":{}}, {}))

tools = [
	{
		"type" : "function",
		"function":{
			"name":"calculator",
			"description":"Evaluate a basic mathematical expression",
			"parameters":{

                "type": "object",

                "properties": {

                    "expression": {

                        "type": "string",

                        "description": "Mathematical expression to evaluate."

                    }

                },

                "required": ["expression"]

            }
		}
	},
	{
		"type":"function",
		"function":{
			"name":"get_current_time",
			"description": "IANA timezone name such as 'Asia/Tokyo', 'America/New_York', or 'Europe/London'",
			"parameters":{
				"type":"object",
				"properties":{
					"timezone":{
						"type": "string",
						"description":"Timezone to lookup for current time"
					}
				},
				"required":["timezone"]
			}
		}
	},
]
TOOLS = {
	"calculator" : calculator,
	"get_current_time": get_current_time,
}

def run_agent(messages, max_steps=5):
    for step in range(max_steps):
        response = litellm.completion(
            model="ollama_chat/qwen2:7b",
            api_base="http://127.0.0.1:11434",
            messages=messages,
            tools=tools,
            temperature=0,
        )

        assistant_message = response.choices[0].message

        print(
            json.dumps(
                assistant_message.model_dump(),
                indent=2,
                default=str,
            )
        )

        if not assistant_message.tool_calls:
            return assistant_message.content

        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            function_to_call = TOOLS.get(tool_name)

            if function_to_call is None:
                result = f"ERROR: Unknown tool '{tool_name}'"
            else:
                try:
                    result = function_to_call(**arguments)
                except Exception as exc:
                    result = f"ERROR: {exc}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

    return "ERROR: Agent reached max_steps without producing a final answer."


final_answer = run_agent(messages)

print("\nFINAL ANSWER:")
print(final_answer)