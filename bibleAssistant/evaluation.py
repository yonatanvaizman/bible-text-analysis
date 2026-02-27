"""
This module is dedicated to evaluating the agent.
The main method is to use example ("golden") conversations as reference: 
at various points along the conversation, present the agent with the convo-prefix and see how the LLM responds (under the agent's response-format constraints), then judge it.
"""
import json
import numpy as np
import pandas as pd

from . import agent

def compare_tool_args(ref_args:dict, tested_args:dict) -> tuple[bool, int]:
    """
    Compare the refernece with the tested response, concerning the arguments for a tool call.
    Assume both dictionaries have the exact same keys (field names)
    Assume that the structure is flat (use a shallow comparison of values).

    Returns:
        - args_the_same (bool): True iff all the fields in ref_args have the corresponding fields with the same value in tested_args.
        - n_args_the_same (int): The number of fields that have the same value in both dictionaries.
        - n_args_different (int): The number of fields that have different values in the two dictionaries.
    """
    field_names = list(ref_args.keys())
    n_args_the_same = 0
    for field_name in field_names:
        n_args_the_same += int(ref_args[field_name] == tested_args[field_name])
    args_the_same = (n_args_the_same == len(field_names))
    n_args_different = len(field_names) - n_args_the_same
    return (args_the_same, n_args_the_same, n_args_different)

def compare_llm_response(ag:agent.Agent, reference_response:str, tested_response:str, input_messages:list[dict]) -> dict:
    # At the moment, assuming valid schemas in both reference and tested responses (valid, json with expected fields present):
    expe_obj = json.loads(reference_response)
    resp_obj = json.loads(tested_response)

    expected_tool_name = expe_obj[ag.KEY_TOOL]
    response_tool_name = resp_obj[ag.KEY_TOOL]
    tool_name_correct = (expected_tool_name == response_tool_name)
    expected_tool_args = expe_obj[ag.KEY_ARGS]
    response_tool_args = resp_obj[ag.KEY_ARGS]
    if tool_name_correct:
        (args_correct, n_args_the_same, n_args_different) = compare_tool_args(expected_tool_args, response_tool_args)
    else:
        (args_correct, n_args_the_same, n_args_different) = (np.nan, np.nan, np.nan)

    # Check for a repeat tool call:
    repeat_tool_call = False
    for message_dict in input_messages:
        if message_dict['role'] != ag.ROLE_ASSISTANT:
            continue
        prev_llm_resp_obj = json.loads(message_dict['content'])
        if prev_llm_resp_obj[ag.KEY_TOOL] != response_tool_name:
            continue
        (the_same, _, _) = compare_tool_args(prev_llm_resp_obj[ag.KEY_ARGS], response_tool_args)
        if the_same:
            repeat_tool_call = True
            break

    comparison_results = {
        'expected_tool_name': expected_tool_name,
        'response_tool_name': response_tool_name,
        'tool_name_correct': tool_name_correct,
        'expected_tool_args': expected_tool_args,
        'response_tool_args': response_tool_args,
        'args_correct': args_correct,
        'n_args_the_same': n_args_the_same,
        'n_args_different': n_args_different,
        'repeat_tool_call': repeat_tool_call
    }
    return comparison_results

def eval_with_ref_conversation(convo_id, ref_convo, model_name):
    """
    Evaluate the agent using a reference conversation.
    This function goes over the messages of the conversation; for each turn where the LLM generated the response, it sends the prefix of the convo to the agent's LLM,
    collects the tested-LLM's response, and judges it with respect to the expected response (the one in the reference convo for this turn).

    Args:
    convo_id (str): an identifier for this reference conversation.
    ref_convo (dict): must contain fields:
        - metadata (a dictionary of metadata).
        - messages (list of dicts). The sequence of messages comprising the reference conversation. Each item is a dictionary with 'role' and 'content'.
    model_name (str): The name of the model version to test.

    Returns:
    tested_turns (list of dicts): a list of test-results, each dedicated to a turn where the LLM is generating a response. Each tested-turn dictionary will have fields:
        - convo_id (str). The identifier of the reference conversation.
        - convo_metadata (dict). The copied metadata of the reference conversation.
        - tested_turn_num (int). A sequential number of the item in the list. Starting at 0.
        - message_num (int). The number of the conversation-turn being tested. Convo message numbers starting at 0. 
            Typically, the first tested-turn (tested_turn_num=0) will be of message_num=2 (expecting the first LLM response after 1 system message and 1 user message).
        - input_messages (list of dicts). The prefix of the convo until (excluding) the tested turn (should be message_num messages). This is the input sent to the tested LLM.
        - reference_response (str). The LLM's response for this turn as it appears in the reference conversation (the "golden"/correct/expected response).
        - tested_response (str). The response from the tested-LLM. This is the response we judge by comparing to the reference_response.
        - expected_tool_name (str). The tool name we expect according to the reference_response (including dummy tools like "respond_to_user").
        - response_tool_name (str). The tool name we got in the generated response from the tested-LLM.
        - expected_tool_args (dict). The tool arguments we expect according to the reference response.
        - response_tool_args (dict). The tool arguments we got in the generated response from the tested-LLM.
        - repeat_tool_call (bool). True iff the tested-LLM generated a repeat tool call, meaning same tool and exactly the same arguments as a previous tool call that appears in the input messages.
            This isn't a judgement yet, but the hidden assumption is that a golden reference convo will never have that (unless I get to tools whose responses are stochastic and merit repeat calls).
    """
    convo_metadata = ref_convo['metadata']
    convo_messages = ref_convo['messages']
    ag = agent.Agent(model_name)
    tested_turns = []
    for message_num, message_dict in enumerate(convo_messages):
        if message_dict['role'] != ag.ROLE_ASSISTANT:
            continue # We're not testing system, user, or tool-response turns.
        tested_turn_num = len(tested_turns)
        input_messages = convo_messages[:message_num]
        reference_response = message_dict['content']
        tested_response = ag._call_llm(input_messages=input_messages)

        tested_turn = {
            'convo_id': convo_id,
            'convo_metadata': convo_metadata,
            'tested_turn_num': tested_turn_num,
            'message_num': message_num,
            'input_messages': input_messages,
            'reference_response': reference_response,
            'tested_response': tested_response,
        }

        comparison_results = compare_llm_response(ag, reference_response, tested_response)
        tested_turn.update(comparison_results)

        tested_turns.append(tested_turn)
    
    return tested_turns

def calc_stats(tests_subdf):
    return
def eval_with_ref_dataset(ref_convos, model_name):
    tested_turns = []
    for convo_id, ref_convo in enumerate(ref_convos):
        tt_i = eval_with_ref_conversation(convo_id, ref_convo, model_name)
        tested_turns.extend(tt_i)
        print(f"Convo {convo_id}. Added {len(tt_i)} tested LLM turns (now collected: {len(tested_turns)})")
    
    tests_df = pd.DataFrame(tested_turns)
    # TODO: Calc metrics (toolname accuracy, perfect args rate, toolname confusion mat, repeat toolcall rate) on sets: whole, group-by expected toolname, group-by convo (to be used for perfect-convo-rate).
    metrics = {

    }

    return tested_turns
