from django.shortcuts import render
import replicate

from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from pydantic import BaseModel
import os
from . import config
import requests
# Create your views here.
# Define the data model for the request (the prompt)
class TextPrompt(BaseModel):
    prompt: str

@api_view(["POST"])
def generate(request):
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    api_key = config.api_key
    engine_id = "stable-diffusion-xl-beta-v2-2-2"

    data = request.data
    prompt = data['prompt']
    print(prompt)
    try:
        response = requests.post(
            f"{api_host}/v1/generation/{engine_id}/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "text_prompts": [
                    {
                        "text": prompt #prompt.prompt
                    }
                ],
                "cfg_scale": 7,
                "height": 512,
                "width": 512,
                "samples": 1,
                "steps": 30,
            },
        )

        if response.status_code != 200:
            return Response({'status_code':500, 'detail':"Image generation failed"})
        data = response.json()
        image_data = data["artifacts"][0]["base64"]

        return Response({"status":200, "image_data": image_data})
    except Exception as e:
        print(e)
        return Response({'status_code':500, 'detail':'got an error'})


# @api_view(['POST'])
# def generate(request):
#     data = request.data
#     prompt=  data['prompt']
#     api_tokens = [
#                 "r8_2qUwkBmmiz9h8wrta9mBwTRiTXG6BWx3RTxUG",
#                 "YOUR_API_TOKEN_2",
#             ]
#     pre_prompt = 'You will only provide a more detailed physical description of a fictional character that will aid an AI for image generation.'
#     prompt_input = prompt
#     # Initialize token index
#     token_index = 0
#     while token_index < len(api_tokens):
#         try:
#                 # Set the current token
#             os.environ['REPLICATE_API_TOKEN'] = api_tokens[token_index]
#             # Generate LLM response
#             output = replicate.run(
#                 "replicate/llama-2-70b-chat:2796ee9483c3fd7aa2e171d38f4ca12251a30609463dcfd4cd76703f22e96cdf",
#                 input={
#                     "prompt": f'{pre_prompt} {prompt_input} Assistant: ',
#                     "temperature": 0.1,
#                     "top_p": 0.9,
#                     "max_length": 128,
#                     "repetition_penalty": 1
#                 }
#             )
#             # Extract the description
#             description = ''
#             for item in output:
#                 description += item
#                 # Remove introductory text
#                 description = description.split(':')[1].strip()
#                 return description
#                 # If successful, break out of the loop
#                 break
#         except Exception as e:
#             print(f"Token {token_index + 1} failed with error: {str(e)}")
#             token_index += 1
#     # If all tokens have been exhausted, you may want to handle this case appropriately
#     if token_index == len(api_tokens):
#         print("All tokens have been used.")

#     return Response()