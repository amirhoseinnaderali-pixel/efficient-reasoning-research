from efficient_reasoning.generation.parsing import extract_code

def test_fenced_code(): assert extract_code('```python\ndef f(x):\n    return x\n```').startswith('def f')
