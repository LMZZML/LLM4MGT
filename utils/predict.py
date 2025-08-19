import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential
@retry(wait=wait_random_exponential(min=1, max=30), stop=stop_after_attempt(1000))
def predict(Q, args):
    input = Q
    temperature = 0
    if args.SC == 1:
        temperature = 0.7
    if 'gpt' in args.model:
        client = openai.OpenAI(
            api_key='',
            base_url="https://api.openai.com/v1",
        )
    elif 'qwen' in args.model:
        client = openai.OpenAI(
            api_key='',
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    Answer_list = []
    for text in input:
        response = client.chat.completions.create(
        model= args.model,
        messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": text},
        ],
        temperature=temperature,
        max_tokens=args.token,
        )
        Answer_list.append(response.choices[0].message.content)
    return Answer_list

