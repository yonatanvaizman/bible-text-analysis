import json
import inspect
import ollama
from . import bible_tools as bblt
from IPython.display import HTML, display

class Agent:

    ROLE_SYSTEM = "system"
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_TOOL = ROLE_USER # Previously I defined this as role "tool" but in order to support many base models, I'll converge to same role as user
    
    KEY_TOOL = "tool"
    KEY_ARGS = "arguments"
    MAX_STEPS_PER_TURN = 4
    
    TOOL_RESPOND_TO_USER = "respond_to_user"
    TOOL_LOOKUP_VERSE = "lookup_verse"

    # def _respond_to_user(self, arguments:dict) -> str:
    #     text = arguments.get("text", "!! Missing text response")
    #     return text
    def _respond_to_user(self, text:str) -> str:
        return text
    
    def _generate_system_instructions(self) -> str:
        instructions = f"""You are a research assistant that always responds using a JSON object with fields "{self.KEY_TOOL}" and "{self.KEY_ARGS}".

To respond normally to the user, use:
{{"{self.KEY_TOOL}": "{self.TOOL_RESPOND_TO_USER}", "{self.KEY_ARGS}":{{"text": "<text to show the user>"}}}}

To call a tool, use:
{{"{self.KEY_TOOL}": "<tool_name>", "{self.KEY_ARGS}":{{ ... }}}}

After you call a tool, you will receive a message with role "{self.ROLE_TOOL}" containing a JSON object.
The tool message always includes "tool_name" and "status".

If "status" is "ok":
- The message will include a "result" object.
- Read "result.text".
- Respond using "respond_to_user" and copy "result.text" exactly as-is.

If "status" is "error":
- The message will include an "error_message".
- If the error message is clear enough (e.g., if the user spelled a book name wrong and it is clear which book the user intended), you can call the tool again with the corrected arguments.
- Otherwise, respond using "respond_to_user" and copy "error_message" exactly as-is (to let the user tell you what to do next).

Rules:
- Never modify, translate, summarize, or explain text returned by the tool.
- Never add commentary or extra text.
- Never guess missing arguments.
- Never correct user mistakes on the first attempt of a tool call.
- Never retry a failed tool call with exactly the same arguments.

Available tool:

To get the text of a specific biblical verse:
{{"{self.KEY_TOOL}": "{self.TOOL_LOOKUP_VERSE}", "{self.KEY_ARGS}":{{"version":"<version>", book:"<book>", chapter_num:<integer>, verse_num:<integer>}}}}
When this tool call succeeds, contains the verse. Copy it exactly as-is and return to the user with "{self.TOOL_RESPOND_TO_USER}".

"""
        # When defining more tools, append more tool-specific instructions ...

        return instructions

    def _schema_for_tool(self, tool_name, func):
        sig = inspect.signature(func)
        args = {}
        for name, param in sig.parameters.items():
            ann = param.annotation
            if ann == str:
                args[name] = {"type": "string"}
            elif ann == int:
                args[name] = {"type": "integer"}
            elif ann == bool:
                args[name] = {"type": "boolean"}
            elif ann == float:
                args[name] = {"type": "float"}
            else:
                args[name] = {"type": "string"}
        
        schema = {
            "type": "object",
            "properties": {
                self.KEY_TOOL: {"type": "string", "enum": [tool_name]},
                self.KEY_ARGS: {
                    "type": "object",
                    "properties": args,
                    "required": list(args.keys()),
                    "additionalProperties": False
                    },
            },
            "required": [self.KEY_TOOL, self.KEY_ARGS],
            "additionalProperties": False
        }
        return schema

    def __init__(self, model_name:str, verbose:bool=False):
        self.verbose = verbose
        self.model_name = model_name
        self.tools = {
            self.TOOL_RESPOND_TO_USER: self._respond_to_user,
            self.TOOL_LOOKUP_VERSE: bblt.lookup_verse,
        }
        self.system_instructions = self._generate_system_instructions()
        self.messages = [{"role": self.ROLE_SYSTEM, "content": self.system_instructions}]
        self.llm_response_schema = {"oneOf": [self._schema_for_tool(tool_name, func) for (tool_name, func) in self.tools.items()]}
    
    def _call_llm(self) -> str:
        if self.verbose:
            print(self.messages[-1])
        response = ollama.chat(
            model=self.model_name,
            messages=self.messages,
            think=False,
            format=self.llm_response_schema
        )
        resp = response["message"]["content"]
        if self.verbose:
            print({'role':'assistant', 'content':resp})
        return resp
    
    def ask(self, user_message:str) -> str:
        """
        The main entry point to interact with the agent.
        The agent receives a message from the user, processes it (internally with the help of an LLM), 
        possibly making tool calls and collecting tool responses, and when it has a ready response for the user it returns the response string.
        """

        self.messages.append({"role": self.ROLE_USER, "content": user_message})

        for iter in range(self.MAX_STEPS_PER_TURN):
            llm_response = self._call_llm()
            self.messages.append({"role": self.ROLE_ASSISTANT, "content": llm_response})
            try:
                llm_obj = json.loads(llm_response)
            except json.JSONDecodeError as e:
                raise ValueError(f"LLM returned invalid JSON: {llm_response}") from e
                        
            tool_name = llm_obj.get(self.KEY_TOOL, None)
            tool_args = llm_obj.get(self.KEY_ARGS, None)

            if tool_name is None:
                raise ValueError(f"LLM returned a JSON without the required field {self.KEY_TOOL}. JSON: {llm_response}")
            if tool_args is None:
                raise ValueError(f"LLM returned a JSON without the required field {self.KEY_ARGS}. JSON: {llm_response}")
            
            if tool_name == self.TOOL_RESPOND_TO_USER:
                return self._respond_to_user(**tool_args)
            
            tool_func = self.tools.get(tool_name, None)
            if tool_func is None:
                raise ValueError(f"LLM returned a JSON with unsupported tool name '{tool_name}'. JSON: {llm_response}")
            
            tool_content = {"tool_name": tool_name}
            try:
                tool_result = tool_func(**tool_args)
                tool_content["status"] = "ok"
                tool_content["result"] = tool_result
            except Exception as ex:
                tool_content["status"] = "error"
                tool_content["error_message"] = str(ex)
            tool_message = {"role": self.ROLE_TOOL, "content": json.dumps(tool_content, ensure_ascii=False)}
            self.messages.append(tool_message)
        
        return f"Agent tried {self.MAX_STEPS_PER_TURN} steps to handle the request, then gave up"



class AgentUI:
    ROLE_USER = "You"
    ROLE_ASSISTANT = "Assistant"
    ROLE_TOOLCALL = "Tool call"
    ROLE_TOOLRESP = "Tool response"

    def __init__(self, model_name:str, verbose:bool=False, html=True):
        self.agent = Agent(model_name, verbose=verbose)
        self.html = html
        print(f"====\nSystem prompt:\n{self.agent.system_instructions}\n====\nLLM response schema:\n{self.agent.llm_response_schema}\n====")
    
    def display_message(self, role, msg):
        style_map = {
            self.ROLE_USER: "'border:3px solid #9944FF; padding:10px; margin-bottom:5px; border-radius: 5px; margin-left: 5px'",
            self.ROLE_ASSISTANT: "'border:3px solid #2222FF; padding:10px; margin-bottom:5px; border-radius: 5px; margin-left: 50px'",
        }
        div_style = style_map.get(role)
        div_content = f"{role}:\n{msg}"
        html = f"<div style={div_style}>{div_content}</div>"
        if self.html:
            display(HTML(html))
        else:
            print(f"{role}: {msg}")

    def start_session(self):
        print("Agent ready to talk. Type 'exit' to quit.\n")
        iter = 0
        while True:
            user_message = input("You: ").strip()
            self.display_message(self.ROLE_USER, user_message)
            if user_message and user_message.lower() in ["exit", "quit"]:
                self.display_message(self.ROLE_ASSISTANT, "Bye!")
                break
            try:
                agent_response = self.agent.ask(user_message)
                self.display_message(self.ROLE_ASSISTANT, agent_response)
            except Exception as e:
                #print(f"[Error] {e}\n")
                raise e # Let it crash and help me debug ;-)
            iter += 1