from openai import OpenAI
client = OpenAI()

def generate_thumbnail(prompt):
    img = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )
    return img.data[0].url