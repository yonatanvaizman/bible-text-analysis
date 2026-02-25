[Q]: https://img.shields.io/badge/Q-0044FF?style=flat
[A]: https://img.shields.io/badge/A-00DD00?style=flat

# Lessons Learned
I'll use this page to list my open research/engineering/development questions, and take notes of what I learn so far.

---

![Q][Q] How to make the LLM's responses valid?
- ![A][A] Inference-time: use response_format.
    - This is a strong mechanism to force the LLM to generate a response that conforms to a strict schema.
    - I already saw that ollama supports it (same as openai interface). Very convenient.
    - I can programmatically calculate the schema, given the function signatures of all the tools.
    - I can treat "respond_to_user" as another tool.
- ![A][A] System prompt/instructions. List all the available tools.
- ![A][A] Training with examples. Fine tune the LLM with examples of using the various tools.

![Q][Q] Should the system prompt mention the tools with exactly the LLM's format for tool call?
- I want the framework to be flexible and easy to scale (adding more tools).
- I want the system prompt to be decoupled from which model is used.
- Can I list the tools in the system prompt in a more abstract way (e.g., use the tool's signature and docstring)?

![Q][Q] What happens if I change the system prompt after training the model with a very specific (consistent) system prompt?
- ![A][A] It seems that the model (1b gemma) is not too dumb and it is flexible enough to understand what to do (sometimes). I used gemma3:1b-ft9-350 (trained 1 epoch with examples of only tool lookup_verse), I changed the system prompt to describe the second tool as well (search_phrase) and registerd it. If the user phrases the request similar to system prompt's example, the LLM correctly calls the tool, and may even respond in a helpful manner (this is trickier...).

![Q][Q] Can I make the model robust to new tools or changed tool descriptions?
- I'm trying to train the model with variations of the system prompt. Same core instructions, but different "tool menus" (always covering the relevant tools for the scenario, but not always showing all other tools, and shuffling tool order).
- On one hand: my hypothesis is that this will make the model more robust to changes in the inference system prompt (specifically adding new tools or changing the tools' docstrings).
- On the other hand: maybe this is wasteful. Wasting the "energy"/effort of training - maybe this will teach the model to dedicate attention too much to the system prompt and dedicate less to learn from training examples. I don't know if that is worth the gain.

![Q][Q] Should the LLM always "respond_to_user" with "text"? Should the tool responses always be hidden from the user?
- Adding the second tool (search all occurrences of a phrase) - it's not clearly defined how the LLM can present a single nice string to the user. And what for? The results of this tool are only intermediate - providing context for further analysis.

![Q][Q] While developing the agent I gradually add more tools and scenarios. It's programmatic and easy to re-generate a new set of train/test examples. Should I train from base model each time? Or train from a previous version?

![Q][Q] Training with partial-convo examples. Can it help the model generalize to varied combinations of convo-segments? Can it harm/confuse? How to do it right - should such an example have the system prompt, then a "dummy" message that indicates "imagine there are more messages here" and then the example's messages? Can I formalize it? Perhaps I need a "..." dummy-message for cases where the conversation is longer than the model's attention span and I want to include the first (system) message and the most recent X messages.

![Q][Q] Forced decoding with response format. When I force the LLM to generate a valid JSON, does the format also indicate anything about using newlines and spaces? If so, does that "confuse" the model (e.g., if the training examples were flat JSONs without spaces and the realtime schema demands spaces)?