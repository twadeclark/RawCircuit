from functools import partial
from pathlib import Path
import json
import re
from jinja2.sandbox import ImmutableSandboxedEnvironment
import torch
import numpy as np
import yaml
from content_loaders.scraper import remove_all_quote, remove_all_newlines_and_tabs, remove_multiple_hashes
import prompt_generator.shared as shared

jinja_env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True)



def generate_chat_prompt_shortcut(comment_history, model_name, state):
    impersonate = False

    model_metadata = get_model_metadata(model_name)
    # print(model_metadata)

    for key, value in model_metadata.items():
        state[key] = value


    messages = []

    chat_template = jinja_env.from_string(state['chat_template_str'])
    instruction_template = jinja_env.from_string(state['instruction_template_str'])
    chat_renderer = partial(chat_template.render, add_generation_prompt=False, name1=state['name1'], name2=state['name2'])
    instruct_renderer = partial(instruction_template.render, add_generation_prompt=False)

    renderer = chat_renderer
    context = replace_character_names(state['context'], state['name1'], state['name2'])
    messages.append({"role": "system", "content": context})

    insert_pos = len(messages)

    back_and_forth = False
    for msg in reversed(comment_history):
        msg = msg.strip()

        if back_and_forth:
            messages.insert(insert_pos, {"role": "assistant", "content": msg})
            # messages.append({"role": "assistant", "content": msg})
        else:
            messages.insert(insert_pos, {"role": "user", "content": msg})

        back_and_forth = not back_and_forth

    def remove_extra_bos(prompt):
        for bos_token in ['<s>', '<|startoftext|>']:
            while prompt.startswith(bos_token):
                prompt = prompt[len(bos_token):]

        return prompt

    def make_prompt(messages):
        prompt = renderer(messages=messages)

        outer_messages = []

        prompt = remove_extra_bos(prompt)
        command = state['chat-instruct_command']
        command = command.replace('<|character|>', state['name2'] if not impersonate else state['name1'])
        command = command.replace('<|prompt|>', prompt)

        prefix = get_generation_prompt(renderer, impersonate=impersonate)[0]
        if not impersonate:
            prefix = apply_extensions('bot_prefix', prefix, state)

        outer_messages.append({"role": "user", "content": command})
        outer_messages.append({"role": "assistant", "content": prefix})

        prompt = instruction_template.render(messages=outer_messages)
        suffix = get_generation_prompt(instruct_renderer, impersonate=False)[1]
        prompt = prompt[:-len(suffix)]


        prompt = remove_extra_bos(prompt)
        return prompt

    prompt = make_prompt(messages)

    # Handle truncation
    max_length = get_max_prompt_length(state)
    while len(messages) > 0 and get_encoded_length(prompt) > max_length:
        # Try to save the system message
        if len(messages) > 1 and messages[0]['role'] == 'system':
            messages.pop(1)
        else:
            messages.pop(0)

        prompt = make_prompt(messages)


    return prompt

    # user_input = 'what is the moon made of?'
    # kwargs = {'_continue': False, 'history': {'internal': [['<|BEGIN-VISIBLE-CHAT|>', 'How can I help you today?']], 'visible': [['', 'How can I help you today?']]}}
    # history_direct = [['<|BEGIN-VISIBLE-CHAT|>', 'How can I help you today?'], ['I have a question about the moon.', "Great! Can you tell me more about the moon's history and its significance in astronomy?"], ["I don't know anything about all that. is the moon made of cheese?", "Yes, it is. It was created by our AI-powered computer when we were still a bunch of small bacteria in space. It took millions of years for us to get there and eventually colonized our solar system's largest body. \n"], ["that's amazing.", 'But now that you know more about the moon, I can help with your question on decision making. Can you provide me with a list of top-performing companies in a specific industry?'], ['all I want is a sandwich.', "Okay, here are some top-rated sandwich shops in New York City according to recent reviews:\n1) Subway\n2) Panera Bread\n3) Olive Garden\n4) Starbucks\n5) McDonald's\n6) Burger King\n7) Wendy's\n8) Papa John's Pizza\n9) Domino's Pizza\n10) Five Guys."]]

    # gcp = generate_chat_prompt(history_direct, user_input, state, **kwargs)
    # print(gcp)
    # generate_chat_prompt(history_direct, user_input, state, **kwargs)





# def generate_chat_prompt(history_direct, user_input, state, **kwargs):
#     impersonate = kwargs.get('impersonate', False)
#     _continue = kwargs.get('_continue', False)
#     also_return_rows = kwargs.get('also_return_rows', False)
#     # history = kwargs.get('history', state['history'])['internal']
#     history = history_direct

#     # Templates
#     chat_template = jinja_env.from_string(state['chat_template_str'])
#     instruction_template = jinja_env.from_string(state['instruction_template_str'])
#     chat_renderer = partial(chat_template.render, add_generation_prompt=False, name1=state['name1'], name2=state['name2'])
#     instruct_renderer = partial(instruction_template.render, add_generation_prompt=False)

#     messages = []

#     if state['mode'] == 'instruct':
#         renderer = instruct_renderer
#         if state['custom_system_message'].strip() != '':
#             messages.append({"role": "system", "content": state['custom_system_message']})
#     else:
#         renderer = chat_renderer
#         if state['context'].strip() != '':
#             context = replace_character_names(state['context'], state['name1'], state['name2'])
#             messages.append({"role": "system", "content": context})

#     insert_pos = len(messages)
#     for user_msg, assistant_msg in reversed(history):
#         user_msg = user_msg.strip()
#         assistant_msg = assistant_msg.strip()

#         if assistant_msg:
#             messages.insert(insert_pos, {"role": "assistant", "content": assistant_msg})

#         if user_msg not in ['', '<|BEGIN-VISIBLE-CHAT|>']:
#             messages.insert(insert_pos, {"role": "user", "content": user_msg})

#     user_input = user_input.strip()
#     if user_input and not impersonate and not _continue:
#         messages.append({"role": "user", "content": user_input})

#     def remove_extra_bos(prompt):
#         for bos_token in ['<s>', '<|startoftext|>']:
#             while prompt.startswith(bos_token):
#                 prompt = prompt[len(bos_token):]

#         return prompt

#     def make_prompt(messages):
#         if state['mode'] == 'chat-instruct' and _continue:
#             prompt = renderer(messages=messages[:-1])
#         else:
#             prompt = renderer(messages=messages)

#         if state['mode'] == 'chat-instruct':
#             outer_messages = []
#             if state['custom_system_message'].strip() != '':
#                 outer_messages.append({"role": "system", "content": state['custom_system_message']})

#             prompt = remove_extra_bos(prompt)
#             command = state['chat-instruct_command']
#             command = command.replace('<|character|>', state['name2'] if not impersonate else state['name1'])
#             command = command.replace('<|prompt|>', prompt)

#             if _continue:
#                 prefix = get_generation_prompt(renderer, impersonate=impersonate, strip_trailing_spaces=False)[0]
#                 prefix += messages[-1]["content"]
#             else:
#                 prefix = get_generation_prompt(renderer, impersonate=impersonate)[0]
#                 if not impersonate:
#                     prefix = apply_extensions('bot_prefix', prefix, state)

#             outer_messages.append({"role": "user", "content": command})
#             outer_messages.append({"role": "assistant", "content": prefix})

#             prompt = instruction_template.render(messages=outer_messages)
#             suffix = get_generation_prompt(instruct_renderer, impersonate=False)[1]
#             prompt = prompt[:-len(suffix)]

#         else:
#             if _continue:
#                 suffix = get_generation_prompt(renderer, impersonate=impersonate)[1]
#                 prompt = prompt[:-len(suffix)]
#             else:
#                 prefix = get_generation_prompt(renderer, impersonate=impersonate)[0]
#                 if state['mode'] == 'chat' and not impersonate:
#                     prefix = apply_extensions('bot_prefix', prefix, state)

#                 prompt += prefix

#         prompt = remove_extra_bos(prompt)
#         return prompt

#     prompt = make_prompt(messages)

#     # Handle truncation
#     #TODO: put this back in later
#     # max_length = get_max_prompt_length(state)
#     # while len(messages) > 0 and get_encoded_length(prompt) > max_length:
#     #     # Try to save the system message
#     #     if len(messages) > 1 and messages[0]['role'] == 'system':
#     #         messages.pop(1)
#     #     else:
#     #         messages.pop(0)

#     #     prompt = make_prompt(messages)

#     if also_return_rows:
#         return prompt, [message['content'] for message in messages]
#     else:
#         return prompt


def replace_character_names(text, name1, name2):
    text = text.replace('{{user}}', name1).replace('{{char}}', name2)
    return text.replace('<USER>', name1).replace('<BOT>', name2)


def get_generation_prompt(renderer, impersonate=False, strip_trailing_spaces=True):
    '''
    Given a Jinja template, reverse-engineers the prefix and the suffix for
    an assistant message (if impersonate=False) or an user message
    (if impersonate=True)
    '''

    if impersonate:
        messages = [
            {"role": "user", "content": "<<|user-message-1|>>"},
            {"role": "user", "content": "<<|user-message-2|>>"},
        ]
    else:
        messages = [
            {"role": "assistant", "content": "<<|user-message-1|>>"},
            {"role": "assistant", "content": "<<|user-message-2|>>"},
        ]

    prompt = renderer(messages=messages)

    suffix_plus_prefix = prompt.split("<<|user-message-1|>>")[1].split("<<|user-message-2|>>")[0]
    suffix = prompt.split("<<|user-message-2|>>")[1]
    prefix = suffix_plus_prefix[len(suffix):]

    if strip_trailing_spaces:
        prefix = prefix.rstrip(' ')

    return prefix, suffix



# This iterator returns the extensions in the order specified in the command-line
def iterator():
    pass
    # for name in sorted(state, key=lambda x: state[x][1]):
    #     if state[name][0]:
    #         yield getattr(extensions, name).script, name



# Extension functions that map string -> string
def _apply_string_extensions(function_name, text, state, is_chat=False):
    # for extension, _ in iterator():
    #     if hasattr(extension, function_name):
    #         func = getattr(extension, function_name)

    #         # Handle old extensions without the 'state' arg or
    #         # the 'is_chat' kwarg
    #         count = 0
    #         has_chat = False
    #         # for k in signature(func).parameters:
    #         #     if k == 'is_chat':
    #         #         has_chat = True
    #         #     else:
    #         #         count += 1

    #         if count == 2:
    #             args = [text, state]
    #         else:
    #             args = [text]

    #         if has_chat:
    #             kwargs = {'is_chat': is_chat}
    #         else:
    #             kwargs = {}

    #         text = func(*args, **kwargs)

    return text

# Extension functions that map string -> string
def _apply_chat_input_extensions(text, visible_text, state):
    for extension, _ in iterator():
        if hasattr(extension, 'chat_input_modifier'):
            text, visible_text = extension.chat_input_modifier(text, visible_text, state)

    return text, visible_text

# Extension that modifies the input parameters before they are used
def _apply_state_modifier_extensions(state):
    for extension, _ in iterator():
        if hasattr(extension, "state_modifier"):
            state = getattr(extension, "state_modifier")(state)

    return state

# Extension that modifies the chat history before it is used
def _apply_history_modifier_extensions(history):
    for extension, _ in iterator():
        if hasattr(extension, "history_modifier"):
            history = getattr(extension, "history_modifier")(history)

    return history

# Extension functions that override the default tokenizer output - The order of execution is not defined
def _apply_tokenizer_extensions(function_name, state, prompt, input_ids, input_embeds):
    for extension, _ in iterator():
        if hasattr(extension, function_name):
            prompt, input_ids, input_embeds = getattr(extension, function_name)(state, prompt, input_ids, input_embeds)

    return prompt, input_ids, input_embeds

# Allow extensions to add their own logits processors to the stack being run.
# Each extension would call `processor_list.append({their LogitsProcessor}())`.
def _apply_logits_processor_extensions(function_name, processor_list, input_ids):
    for extension, _ in iterator():
        if hasattr(extension, function_name):
            result = getattr(extension, function_name)(processor_list, input_ids)
            if type(result) is list:
                processor_list = result

# custom_generate_chat_prompt handling - currently only the first one will work
def _apply_custom_generate_chat_prompt(text, state, **kwargs):
    for extension, _ in iterator():
        if hasattr(extension, 'custom_generate_chat_prompt'):
            return extension.custom_generate_chat_prompt(text, state, **kwargs)

    return None

# Custom generate reply handling - currently only the first one will work
def _apply_custom_generate_reply():
    for extension, _ in iterator():
        if hasattr(extension, 'custom_generate_reply'):
            return getattr(extension, 'custom_generate_reply')

    return None

# Get prompt length in tokens after applying extension functions which override the default tokenizer output
# currently only the first one will work
def _apply_custom_tokenized_length(prompt):
    # for extension, _ in iterator():
    #     if hasattr(extension, 'custom_tokenized_length'):
    #         return getattr(extension, 'custom_tokenized_length')(prompt)

    return None

def _apply_custom_css():
    all_css = ''
    for extension, _ in iterator():
        if hasattr(extension, 'custom_css'):
            all_css += getattr(extension, 'custom_css')()

    return all_css

def _apply_custom_js():
    all_js = ''
    for extension, _ in iterator():
        if hasattr(extension, 'custom_js'):
            all_js += getattr(extension, 'custom_js')()

    return all_js


EXTENSION_MAP = {
    "input": partial(_apply_string_extensions, "input_modifier"),
    "output": partial(_apply_string_extensions, "output_modifier"),
    "chat_input": _apply_chat_input_extensions,
    "state": _apply_state_modifier_extensions,
    "history": _apply_history_modifier_extensions,
    "bot_prefix": partial(_apply_string_extensions, "bot_prefix_modifier"),
    "tokenizer": partial(_apply_tokenizer_extensions, "tokenizer_modifier"),
    'logits_processor': partial(_apply_logits_processor_extensions, 'logits_processor_modifier'),
    "custom_generate_chat_prompt": _apply_custom_generate_chat_prompt,
    "custom_generate_reply": _apply_custom_generate_reply,
    "tokenized_length": _apply_custom_tokenized_length,
    "css": _apply_custom_css,
    "js": _apply_custom_js
}


def encode(prompt, add_special_tokens=True, add_bos_token=True, truncation_length=None):
    if shared.tokenizer is None:
        raise ValueError('No tokenizer is loaded')

    if shared.model.__class__.__name__ in ['LlamaCppModel', 'CtransformersModel', 'Exllamav2Model']:
        input_ids = shared.tokenizer.encode(str(prompt))
        if shared.model.__class__.__name__ not in ['Exllamav2Model']:
            input_ids = np.array(input_ids).reshape(1, len(input_ids))
    else:
        input_ids = shared.tokenizer.encode(str(prompt), return_tensors='pt', add_special_tokens=add_special_tokens)
        if not add_bos_token:
            while len(input_ids[0]) > 0 and input_ids[0][0] == shared.tokenizer.bos_token_id:
                input_ids = input_ids[:, 1:]

    # Handling truncation
    if truncation_length is not None:
        input_ids = input_ids[:, -truncation_length:]

    if shared.model.__class__.__name__ in ['LlamaCppModel', 'Exllamav2Model', 'CtransformersModel'] or shared.args.cpu:
        return input_ids
    # elif shared.args.deepspeed:
        # return input_ids.to(device=local_rank)
        # return None
    elif torch.backends.mps.is_available():
        device = torch.device('mps')
        return input_ids.to(device)
    # elif is_torch_xpu_available():
    #     return input_ids.to("xpu:0")
    else:
        return input_ids.cuda()

def apply_extensions(typ, *args, **kwargs):
    if typ not in EXTENSION_MAP:
        raise ValueError(f"Invalid extension type {typ}")

    return EXTENSION_MAP[typ](*args, **kwargs)

def get_max_prompt_length(state):
    return state['truncation_length'] - state['max_new_tokens']

def get_encoded_length(prompt):
    length_after_extensions = apply_extensions('tokenized_length', prompt)
    if length_after_extensions is not None:
        return length_after_extensions

    word_count = len(prompt.split())

    # return len(encode(prompt)[0])
    return word_count


# with Path(f'{args.model_dir}/config-user.yaml') as p:

def load_instruction_template(template):
    for filepath in [Path(f'{shared.args.model_dir}/instruction-templates/{template}.yaml'), Path(f'{shared.args.model_dir}/instruction-templates/Alpaca.yaml')]:
        if filepath.exists():
            break
    else:
        return ''

    file_contents = open(filepath, 'r', encoding='utf-8').read()
    data = yaml.safe_load(file_contents)
    if 'instruction_template' in data:
        return data['instruction_template']
    else:
        return jinja_template_from_old_format(data)


def jinja_template_from_old_format(params, verbose=False):
    MASTER_TEMPLATE = """
{%- set ns = namespace(found=false) -%}
{%- for message in messages -%}
    {%- if message['role'] == 'system' -%}
        {%- set ns.found = true -%}
    {%- endif -%}
{%- endfor -%}
{%- if not ns.found -%}
    {{- '<|PRE-SYSTEM|>' + '<|SYSTEM-MESSAGE|>' + '<|POST-SYSTEM|>' -}}
{%- endif %}
{%- for message in messages %}
    {%- if message['role'] == 'system' -%}
        {{- '<|PRE-SYSTEM|>' + message['content'] + '<|POST-SYSTEM|>' -}}
    {%- else -%}
        {%- if message['role'] == 'user' -%}
            {{-'<|PRE-USER|>' + message['content'] + '<|POST-USER|>'-}}
        {%- else -%}
            {{-'<|PRE-ASSISTANT|>' + message['content'] + '<|POST-ASSISTANT|>' -}}
        {%- endif -%}
    {%- endif -%}
{%- endfor -%}
{%- if add_generation_prompt -%}
    {{-'<|PRE-ASSISTANT-GENERATE|>'-}}
{%- endif -%}
"""

    if 'context' in params and '<|system-message|>' in params['context']:
        pre_system = params['context'].split('<|system-message|>')[0]
        post_system = params['context'].split('<|system-message|>')[1]
    else:
        pre_system = ''
        post_system = ''

    pre_user = params['turn_template'].split('<|user-message|>')[0].replace('<|user|>', params['user'])
    post_user = params['turn_template'].split('<|user-message|>')[1].split('<|bot|>')[0]

    pre_assistant = '<|bot|>' + params['turn_template'].split('<|bot-message|>')[0].split('<|bot|>')[1]
    pre_assistant = pre_assistant.replace('<|bot|>', params['bot'])
    post_assistant = params['turn_template'].split('<|bot-message|>')[1]

    def preprocess(string):
        return string.replace('\n', '\\n').replace('\'', '\\\'')

    pre_system = preprocess(pre_system)
    post_system = preprocess(post_system)
    pre_user = preprocess(pre_user)
    post_user = preprocess(post_user)
    pre_assistant = preprocess(pre_assistant)
    post_assistant = preprocess(post_assistant)

    if verbose:
        print(
            '\n',
            repr(pre_system) + '\n',
            repr(post_system) + '\n',
            repr(pre_user) + '\n',
            repr(post_user) + '\n',
            repr(pre_assistant) + '\n',
            repr(post_assistant) + '\n',
        )

    result = MASTER_TEMPLATE
    if 'system_message' in params:
        result = result.replace('<|SYSTEM-MESSAGE|>', preprocess(params['system_message']))
    else:
        result = result.replace('<|SYSTEM-MESSAGE|>', '')

    result = result.replace('<|PRE-SYSTEM|>', pre_system)
    result = result.replace('<|POST-SYSTEM|>', post_system)
    result = result.replace('<|PRE-USER|>', pre_user)
    result = result.replace('<|POST-USER|>', post_user)
    result = result.replace('<|PRE-ASSISTANT|>', pre_assistant)
    result = result.replace('<|PRE-ASSISTANT-GENERATE|>', pre_assistant.rstrip(' '))
    result = result.replace('<|POST-ASSISTANT|>', post_assistant)

    result = result.strip()

    return result


def get_model_metadata(model):
    model_settings = {}

    # Get settings from models/config.yaml and models/config-user.yaml
    settings = shared.model_config
    for pat in settings:
        if re.match(pat.lower(), model.lower()):
            for k in settings[pat]:
                model_settings[k] = settings[pat][k]

    path = Path(f'{shared.args.model_dir}/{model}/config.json')
    if path.exists():
        hf_metadata = json.loads(open(path, 'r', encoding='utf-8').read())
    else:
        hf_metadata = None

    # if 'loader' not in model_settings:
    #     if hf_metadata is not None and 'quip_params' in hf_metadata:
    #         loader = 'QuIP#'
    #     else:
    #         loader = infer_loader(model, model_settings)

    #     model_settings['loader'] = loader

    # GGUF metadata
    # if model_settings['loader'] in ['llama.cpp', 'llamacpp_HF', 'ctransformers']:
    #     path = Path(f'{shared.args.model_dir}/{model}')
    #     if path.is_file():
    #         model_file = path
    #     else:
    #         model_file = list(path.glob('*.gguf'))[0]

    #     metadata = metadata_gguf.load_metadata(model_file)
    #     if 'llama.context_length' in metadata:
    #         model_settings['n_ctx'] = metadata['llama.context_length']
    #     if 'llama.rope.scale_linear' in metadata:
    #         model_settings['compress_pos_emb'] = metadata['llama.rope.scale_linear']
    #     if 'llama.rope.freq_base' in metadata:
    #         model_settings['rope_freq_base'] = metadata['llama.rope.freq_base']
    #     if 'tokenizer.chat_template' in metadata:
    #         template = metadata['tokenizer.chat_template']
    #         eos_token = metadata['tokenizer.ggml.tokens'][metadata['tokenizer.ggml.eos_token_id']]
    #         bos_token = metadata['tokenizer.ggml.tokens'][metadata['tokenizer.ggml.bos_token_id']]
    #         template = template.replace('eos_token', "'{}'".format(eos_token))
    #         template = template.replace('bos_token', "'{}'".format(bos_token))

    #         template = re.sub(r'raise_exception\([^)]*\)', "''", template)
    #         model_settings['instruction_template'] = 'Custom (obtained from model metadata)'
    #         model_settings['instruction_template_str'] = template

    # else:
    #     # Transformers metadata
    #     if hf_metadata is not None:
    #         metadata = json.loads(open(path, 'r', encoding='utf-8').read())
    #         if 'max_position_embeddings' in metadata:
    #             model_settings['truncation_length'] = metadata['max_position_embeddings']
    #             model_settings['max_seq_len'] = metadata['max_position_embeddings']

    #         if 'rope_theta' in metadata:
    #             model_settings['rope_freq_base'] = metadata['rope_theta']

    #         if 'rope_scaling' in metadata and type(metadata['rope_scaling']) is dict and all(key in metadata['rope_scaling'] for key in ('type', 'factor')):
    #             if metadata['rope_scaling']['type'] == 'linear':
    #                 model_settings['compress_pos_emb'] = metadata['rope_scaling']['factor']

    #         if 'quantization_config' in metadata:
    #             if 'bits' in metadata['quantization_config']:
    #                 model_settings['wbits'] = metadata['quantization_config']['bits']
    #             if 'group_size' in metadata['quantization_config']:
    #                 model_settings['groupsize'] = metadata['quantization_config']['group_size']
    #             if 'desc_act' in metadata['quantization_config']:
    #                 model_settings['desc_act'] = metadata['quantization_config']['desc_act']

    #     # Read AutoGPTQ metadata
    #     path = Path(f'{shared.args.model_dir}/{model}/quantize_config.json')
    #     if path.exists():
    #         metadata = json.loads(open(path, 'r', encoding='utf-8').read())
    #         if 'bits' in metadata:
    #             model_settings['wbits'] = metadata['bits']
    #         if 'group_size' in metadata:
    #             model_settings['groupsize'] = metadata['group_size']
    #         if 'desc_act' in metadata:
    #             model_settings['desc_act'] = metadata['desc_act']

    # Try to find the Jinja instruct template
    path = Path(f'{shared.args.model_dir}/{model}') / 'tokenizer_config.json'
    if path.exists():
        metadata = json.loads(open(path, 'r', encoding='utf-8').read())
        if 'chat_template' in metadata:
            template = metadata['chat_template']
            for k in ['eos_token', 'bos_token']:
                if k in metadata:
                    value = metadata[k]
                    if type(value) is dict:
                        value = value['content']

                    template = template.replace(k, "'{}'".format(value))

            template = re.sub(r'raise_exception\([^)]*\)', "''", template)
            model_settings['instruction_template'] = 'Custom (obtained from model metadata)'
            model_settings['instruction_template_str'] = template

    if 'instruction_template' not in model_settings:
        model_settings['instruction_template'] = 'Alpaca'

    if model_settings['instruction_template'] != 'Custom (obtained from model metadata)':
        model_settings['instruction_template_str'] = load_instruction_template(model_settings['instruction_template'])

    # Ignore rope_freq_base if set to the default value
    if 'rope_freq_base' in model_settings and model_settings['rope_freq_base'] == 10000:
        model_settings.pop('rope_freq_base')

    # Apply user settings from models/config-user.yaml
    settings = shared.user_config
    for pat in settings:
        if re.match(pat.lower(), model.lower()):
            for k in settings[pat]:
                model_settings[k] = settings[pat][k]

    return model_settings
