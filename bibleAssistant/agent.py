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
    KEY_RESP_TOOL_NAME = "tool_name"
    KEY_STATUS = "status"
    KEY_RESULT = "result"
    KEY_ERROR = "error_message"

    STATUS_OK = "ok"
    STATUS_ER = "error"

    SUBKEY_TEXT = "text"

    MAX_STEPS_PER_TURN = 4
    
    TOOL_RESPOND_TO_USER = "respond_to_user"
    TOOL_LOOKUP_VERSE = "lookup_verse"
    TOOL_SEARCH_PHRASE = "search_phrase"

    def _respond_to_user(self, text:str) -> str:
        return text
    
    # def _generate_system_instructions(self) -> str:
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

Available toos:

To get the text of a specific biblical verse:
{{"{self.KEY_TOOL}": "{self.TOOL_LOOKUP_VERSE}", "{self.KEY_ARGS}":{{"version":"<version>", book:"<book>", chapter_num:<integer>, verse_num:<integer>}}}}
When this tool call succeeds, contains the verse. Copy it exactly as-is and return to the user with "{self.TOOL_RESPOND_TO_USER}".

To search for all the verses that have a certain word or phrase:
{{"{self.KEY_TOOL}": "{self.TOOL_SEARCH_PHRASE}", "{self.KEY_ARGS}":{{"phrase":"<phrase>"}}}}
When this tool call succeeds, the tool's response will be a dictionary with key "results", holding the list of all the occurrences of the phrase.
If the user already told you what to do with these result, go ahead and do it. Otherwise respond to the user with "o.k. now what?" to get further instructions.
"""
        # When defining more tools, append more tool-specific instructions ...

        return instructions

    def _generate_system_instructions(self, tool_names:list[str]=None) -> str:
        instructions = f"""You are a research assistant for biblical texts that always responds using a JSON object with fields "{self.KEY_TOOL}" and "{self.KEY_ARGS}".

To respond normally to the user, use:
{{"{self.KEY_TOOL}": "{self.TOOL_RESPOND_TO_USER}", "{self.KEY_ARGS}":{{"{self.SUBKEY_TEXT}": "<text to show the user>"}}}}

To call a tool, you need to indicate which tool to use and what arguments to send to it - use the structure:
{{"{self.KEY_TOOL}": "<tool_name>", "{self.KEY_ARGS}":{{ ... }}}}

After you call a tool, you will receive a tool-response message from role "{self.ROLE_TOOL}" containing a JSON object.
The tool-response object always includes fields "{self.KEY_RESP_TOOL_NAME}" and "{self.KEY_STATUS}".

If the tool call succeeded, the tool response object will have the structure:
{{"{self.KEY_RESP_TOOL_NAME}": "<tool_name>", "{self.KEY_STATUS}": "{self.STATUS_OK}", "{self.KEY_RESULT}": {{ ... }}}}
Different tools have different structures of the returned data inside the dictionary "{self.KEY_RESULT}".
If you know what to do next, go ahead (e.g., if the user already told you what to do with the results, or if you have a plan and you want to use information from the results to do another tool call).
If you're not sure what to do next or how to present the results to the user, you can respond to the user with "o.k. what now?" to get further instructions.

If the tool call fails, the tool response object will have the structure:
{{"{self.KEY_RESP_TOOL_NAME}": "<tool_name>", "{self.KEY_STATUS}": "{self.STATUS_ER}", "{self.KEY_ERROR}": " ... "}}
If the error message is clear enough, you can try to fix the problem yourself (e.g., call the same tool with corrected arguments, or call another tool).
Otherwise, you can surface the error message back to the user (with "{self.TOOL_RESPOND_TO_USER}") sto get further instructions.

Available tools:

"""
        tool_descriptions = []
        if not tool_names:
            tool_names = list(self.tools.keys())
        if self.TOOL_RESPOND_TO_USER in tool_names:
            tool_names.remove(self.TOOL_RESPOND_TO_USER)
        for tool_name in tool_names:
            func = self.tools.get(tool_name)
            if tool_name == self.TOOL_RESPOND_TO_USER:
                continue
            sig = inspect.signature(func)
            doc = func.__doc__
            desc = f"{tool_name}{sig}{doc}"
            # desc = f"{tool_name}{doc}"
            tool_descriptions.append(desc)
        
        tools_str = '\n\n----\n\n'.join(tool_descriptions)
        instructions += tools_str

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

    def initialize_conversation(self):
        self.messages = [{"role": self.ROLE_SYSTEM, "content": self.system_instructions}]
        
    def __init__(self, model_name:str, verbose:bool=False):
        self.verbose = verbose
        self.model_name = model_name
        self.tools = {
            self.TOOL_RESPOND_TO_USER: self._respond_to_user,
            self.TOOL_LOOKUP_VERSE: bblt.lookup_verse,
            self.TOOL_SEARCH_PHRASE: bblt.search_phrase
        }
        self.system_instructions = self._generate_system_instructions()
        self.llm_response_schema = {"oneOf": [self._schema_for_tool(tool_name, func) for (tool_name, func) in self.tools.items()]}
        self.initialize_conversation()
    
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
            
            tool_content = {self.KEY_RESP_TOOL_NAME: tool_name}
            try:
                tool_result = tool_func(**tool_args)
                tool_content[self.KEY_STATUS] = self.STATUS_OK
                tool_content[self.KEY_RESULT] = tool_result
            except Exception as ex:
                tool_content[self.KEY_STATUS] = self.STATUS_ER
                tool_content[self.KEY_ERROR] = str(ex)
            tool_message = {"role": self.ROLE_TOOL, "content": json.dumps(tool_content, ensure_ascii=False)}
            self.messages.append(tool_message)
        
        return f"Agent tried {self.MAX_STEPS_PER_TURN} steps to handle the request, then gave up"



class AgentUI:
    ROLE_SYSTEM = "System"
    ROLE_USER = "You"
    ROLE_ASSISTANT = "Assistant"
    ROLE_TOOLCALL = "Tool call"
    ROLE_TOOLRESP = "Tool response"

    def __init__(self, model_name:str, verbose:bool=False, html=True):
        self.agent = Agent(model_name, verbose=verbose)
        self.html = html
        self.verbose = verbose
        if self.verbose:
            print(f"====\nSystem prompt:\n{self.agent.system_instructions}")
            print("====")
            print(f"LLM response schema:\n{json.dumps(self.agent.llm_response_schema,indent=2)}\n====")
    
    def display_convo(self, messages):
        convo = ""
        for message in messages:
            message_div = self.get_structured_message_div(message["role"], message["content"])
            delim = "<br/>" if self.html else "\n"
            convo += delim + message_div
        if self.html:
            display(HTML(convo))
        else:
            print(convo)

    def get_structured_message_div(self, role, msg):
        try:
            msg_obj = json.loads(msg)
        except:
            # Then this is probably a regular textual system/user message
            if role == Agent.ROLE_SYSTEM:
                role = self.ROLE_SYSTEM
            elif role == Agent.ROLE_USER:
                role = self.ROLE_USER
            else:
                raise ValueError(f"!! Strange. got message without a json structure for role '{role}': '{msg}'")
            return self.get_message_div(role, msg)
        
        if Agent.KEY_TOOL in msg_obj:
            tool_name = msg_obj.get(Agent.KEY_TOOL)
            tool_args = msg_obj.get(Agent.KEY_ARGS)
            if tool_name == Agent.TOOL_RESPOND_TO_USER:
                text = tool_args.get("text")
                return self.get_message_div(self.ROLE_ASSISTANT, text)
            args_str = ", ".join([f"{k}={v}" for k,v in tool_args.items()])
            nice_msg = f"Calling <b>{tool_name}</b>({args_str})"
            return self.get_message_div(self.ROLE_TOOLCALL, nice_msg)
        
        # This must be a tool response:
        tool_name = msg_obj.get("tool_name")
        status = msg_obj.get("status")
        if status == "ok":
            result = msg_obj.get("result")
            nice_msg = f"Response from <b>{tool_name}</b>: {result}"
        else:
            error_msg = msg_obj.get("error_message")
            nice_msg = f"Failed call to <b>{tool_name}</b>: {error_msg}"
        return self.get_message_div(self.ROLE_TOOLRESP, nice_msg)

    def get_message_div(self, role, msg):
        color_map = {
            self.ROLE_SYSTEM: "#990099",
            self.ROLE_USER: "#00BB00",
            self.ROLE_ASSISTANT: "#2222FF",
            self.ROLE_TOOLCALL: "#00BB88",
            self.ROLE_TOOLRESP: "#0088BB"
        }
        style_map = {
            self.ROLE_SYSTEM: "'display: inline-block; border:3px solid {color}; padding:10px; margin-bottom:5px; border-radius: 5px; margin-left: 5px'",
            self.ROLE_USER: "'display: inline-block; border:3px solid {color}; padding:10px; margin-bottom:5px; border-radius: 5px; margin-left: 5px'",
            self.ROLE_ASSISTANT: "'display: inline-block; border:3px solid {color}; padding:10px; margin-bottom:5px; border-radius: 5px; margin-left: 50px'",
            self.ROLE_TOOLCALL: "'display: inline-block; border:3px solid {color}; padding:10px; margin-bottom:5px; border-radius: 5px; margin-left: 100px'",
            self.ROLE_TOOLRESP: "'display: inline-block; border:3px solid {color}; padding:10px; margin-bottom:5px; border-radius: 5px; margin-left: 100px'",
        }
        if self.html:
            color = color_map.get(role)
            div_style = style_map.get(role).format(color=color)
#            div_content = f"<span style='background-color: {color}'>{role}:</span>\n{msg}"
            div_content = f"<span style='color: {color}'>{role}:</span>\n{msg}"
            div_content = div_content.replace('\n', '<br/>')
            html = f"<div style={div_style}>{div_content}</div>"
            return html
        else:
            return f"{role}: {msg}"

    def display_message(self, role, msg):
        message_div = self.get_message_div(role, msg)
        if self.html:
            display(HTML(message_div))
        else:
            print(message_div)

    def start_session(self):
        self.agent.initialize_conversation()
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