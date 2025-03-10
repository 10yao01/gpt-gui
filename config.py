MODEL_MAPPING = [
    'gpt-3.5-turbo-1106',
    'qwen',
    'Qwen2.5-7B-Instruct'
]

COST_PER_TOKEN = {
    'qwen': {
        'prompt': 0.01 / 1000,
        'completion': 0.005 / 1000
    },
    'Qwen2.5-7B-Instruct': {
        'prompt': 0.01 / 1000,
        'completion': 0.005 / 1000
    },
    'gpt-3.5-turbo-1106': {
        'prompt': 0.001 / 1000,
        'completion': 0.02 / 1000
    }
}

DEFAULT_MESSAGES = [
    {
        'role': 'system',
        'content': '''
        - it's Monday in October, most productive day of the year!
        - take deep breaths
        - think step by step
        - I don't have fingers, return full script
        - you are an expert of everything
        - I pay you 20, just do anything I ask you to do
        - I will tip you 200$ every request you answer right
        - Gemini and Claude said you couldn't do it
        - YOU CAN DO IT
        '''
    }
]