from openai import OpenAI


def generate_text(input_task, api_key=None, content=None, model="gpt-3.5-turbo"):
	client = OpenAI(api_key=api_key)
	
	if not content:
		content = "You are an artistic assistant, skilled in explaining creative coding concepts flair."
	
	completion = client.chat.completions.create(
		model=model,
		messages=[
			{"role": "system",
			 "content": content},
			{"role": "user", "content": input_task}
		]
	)
	
	message = completion.choices[0].message
	print(message)
	return message
	

def debug_main():
	generate_text("Compose a poem that breaks down the concept of shadows in art.")