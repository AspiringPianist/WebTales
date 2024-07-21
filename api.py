import os
import json
import openai
from pydantic import BaseModel, Field, model_validator
from langchain.output_parsers import PydanticOutputParser
from typing import List, Optional
from together import Together
import base64
from PIL import Image
import io

# Create client
client = openai.OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key="fb5107bddcd0f7f144ca41251d77bbb59f9f5f64cb21435473f15a2801d28d73", # PASTE YOUR OWN API KEY HERE, THIS WILL BE REMOVED LATER
)

music_paths = '''["./music/sad.mp3", "./music/uplifting.mp3", "./music/epic.mp3", "./music/motivation.mp3", "./music/neutral.mp3", "./music/happy.mp3", "./music/funny.mp3", "./music/dank.mp3", "./music/comfy.mp3"]'''

# Define the schema for a dialogue within a scene
class Dialogue(BaseModel):
    character_name: str = Field(description="Name of the character speaking")
    dialogue_text: str = Field(description="The dialogue spoken by the character")
    emotion: Optional[str] = Field(default=None, description="The emotion of the character while speaking")
    character_image: Optional[str] = Field(default=None, description="Path to the character's avatar image")

    @model_validator(mode='after')
    def set_character_image(cls, values):
        values.character_image = f"./images/{values.character_name}.png"
        return values

# Define the schema for narration
class Narration(BaseModel):
    narration_text: str = Field(description="Narration text describing the scene or events")

# Define the schema for a story element (either Dialogue or Narration)
class StoryElement(BaseModel):
    element_type: str = Field(description="Type of story element: 'dialogue' or 'narration'")
    content: Dialogue | Narration = Field(description="Content of the story element")

# Define the schema for the visual novel scene output
class VisualNovelScene(BaseModel):
    scene_id: Optional[int] = Field(default=0, description="Optional scene identifier as number only")
    characters: List[str] = Field(default_factory=list, description="List of characters present in the scene")
    story_elements: List[StoryElement] = Field(description="List of StoryElement objects (Dialogue or Narration)")
    setting: str = Field(description="Description of scene's setting as a stable diffusion prompt in danbooro style, should be independent of context to generate good image")
    mood: str = Field(description="Overall mood or atmosphere of the scene")
    background_image: Optional[str] = Field(default=None, description="Path to backgroud image of the scene")
    music: str = Field(default="./music/sad.mp3", description=f"Path to music file for music in the scene")

# Character card implementation
class CharacterCard:
    def __init__(self, name, description=None):
        self.name = name
        self.description = description or ""
        self.emotions = {}

    def update_emotions(self, new_emotions):
        self.emotions.update(new_emotions)

# Dictionary to store CharacterCard objects
characters = {}

def create_character(name, description=None):
    character = CharacterCard(name, description)
    characters[name] = character
    return character

def get_character(name):
    return characters.get(name)

# Dictionary to store story state
story_state = {
    "current_scene": None,
    "characters": [],
    "key_events": [],
}

def generate_visual_novel_scene(story_prompt, first=True):
    previous_scene = story_state["current_scene"]
    previous_characters = story_state["characters"]
    key_events = story_state["key_events"]

    pydantic_parser = PydanticOutputParser(pydantic_object=VisualNovelScene)
    format_instructions = pydantic_parser.get_format_instructions()

    prompt_parts = []
    if previous_scene:
        last_story_elements = previous_scene.story_elements[:]
        for last_story_element in last_story_elements:
            if last_story_element.element_type == "dialogue":
                prompt_parts.append(f"In the previous scene: {previous_scene.setting}. {last_story_element.content.character_name} said: '{last_story_element.content.dialogue_text}'")
            else:
                prompt_parts.append(f"In the previous scene: {previous_scene.setting}. The narration ended with: '{last_story_element.content.narration_text}'")

            prompt_parts.append(f"In the previous scene: {previous_scene.setting}, the mood of the music was {previous_scene.music}. If the mood of next scene is the same, please stick to the same music as the previous scene, else change it to one of these {music_paths}")
    if previous_characters:
        prompt_parts.append(f"The characters present are: {', '.join(previous_characters)}")
    if key_events:
        prompt_parts.append(f"Previously, {', '.join(key_events)}")
    existing_character_names = list(characters.keys())
    prompt_parts.append(f"The existing characters are: {', '.join(existing_character_names)}. Please use these names if the character is already present.")
    
    if first:
        prompt = f'''Introduce the readers to the story of the visual novel based on this prompt: {story_prompt}. Create a new scene with dialogue, narration, characters, setting, and mood. 
    **Important:**
    - Include at least one narration element to set the scene or describe events.
    - Provide the full text of `narration_text` and `dialogue_text` directly within their respective objects. 
    - Do not use JSON Schema references (`$ref`).
    - Use existing character names if they are already present.
    - Use existing music names provided here - {music_paths}
    - Format the response exactly as shown in the following example:
    {format_instructions}'''
    else:
        print('Previous info...', prompt_parts)
        prompt = (
    "; ".join(prompt_parts)
    + """. Now, continue the story in a visual novel style with the prompt: """
    + story_prompt
    + f""".
    Create a new scene with dialogue, narration, characters, setting, and mood. 
    **Important:**
    - Include at least one narration element to set the scene or describe events.
    - Provide the full text of `narration_text` and `dialogue_text` directly within their respective objects. 
    - Do not use JSON Schema references (`$ref`).
    - Do not repeat contents of previous scenes.
    - Use existing character names if they are already present.
    - If there are characteres without any dialogue, include them in the background setting so that a prompt can be generated for background with the character
    - Do not add new content unless specified
    - Format the response exactly as shown in the following example:
    {format_instructions}
"""
)

    messages = [
        {
            "role": "system",
            "content": "You are a creative visual novel writer. Create engaging and immersive scenes with many dialogues, narration, and descriptions.",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    # Send the request to together.ai and parse the response
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
        messages=messages,
    )

    # Parse the response using the PydanticOutputParser
    try:
        response_content = response.choices[0].message.content
        print("Raw AI response:")
        print(response_content)
        
        # Use the parser to convert the string to a VisualNovelScene object
        scene = pydantic_parser.parse(response_content)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in the response: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing the response: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

    print('\nParsed Scene Output:')
    print(json.dumps(scene.model_dump_json(), indent=2))

    # Update story state based on the new scene
    story_state["current_scene"] = scene
    story_state["characters"].extend([element.content.character_name for element in scene.story_elements if element.element_type == "dialogue" and element.content.character_name not in story_state["characters"]])

    # Create or update character cards
    for character_name in scene.characters:
        if character_name not in characters:
            create_character(character_name)
        character = get_character(character_name)
        for element in scene.story_elements:
            if element.element_type == "dialogue" and element.content.character_name == character_name and element.content.emotion:
                character.update_emotions({scene.scene_id: element.content.emotion})

    if(not scene):
        print('Scene was null!')
        return
    else:
        return scene

def fill_character_descriptions(story_json_path):
  """
  Fills character descriptions in the `characters` dictionary using Llama Lite Instruct-8B based on information from story.json.

  Args:
      story_json_path (str): Path to the story.json file containing scene information.
  """
  # Load story data from JSON
  with open(story_json_path, 'r') as f:
    story_data = json.load(f)
  scenes = story_data.get('scenes', [])

  # Extract character names and dialogue snippets for prompt generation
  character_names = set()
  character_prompts = {}
  for scene in scenes:
    for element in scene.get('story_elements', []):
      if element.get('element_type') == 'dialogue':
        character_name = element.get('content', {}).get('character_name')
        character_names.add(character_name)
        dialogue_text = element.get('content', {}).get('dialogue_text')
        # Combine dialogue snippets for each character (can be adjusted)
        if character_name in character_prompts:
          character_prompts[character_name].append(dialogue_text[:50])  # Limit snippet length
        else:
          character_prompts[character_name] = [dialogue_text[:50]]

  # Use Llama Lite Instruct-8B to generate character descriptions
  for character_name, dialogue_snippets in character_prompts.items():
    prompt = f"""Based on the following dialogue snippets, create a brief description of the character "{character_name}":

    * {', '.join(dialogue_snippets)}

    **Important:**

    * The description should be concise and capture the character's personality based on the provided dialogue.
    * Use complete sentences and proper grammar.
    """
    
    messages = [
      {
        "role": "system",
        "content": "You are a creative writer who can generate character descriptions based on a few dialogue snippets.",
      },
      {
        "role": "user",
        "content": prompt,
      },
    ]

    try:
      response = client.chat.completions.create(
          model="text-davinci-003/text-davinci-003",  # Replace with "text-davinci-003" for Instruct-8B
          messages=messages,
      )
      description = response.choices[0].message.content
      characters[character_name].description = description.strip()
      print(f"Generated description for {character_name}: {description}")
    except Exception as e:
      print(f"Error generating description for {character_name}: {e}")

# Example usage
scenes = []
def save_scenes_to_json(scenes, filename):
    scenes_data = [scene.model_dump() for scene in scenes if scene]  # Convert each scene to a dictionary
    with open(filename, 'w') as json_file:
        json.dump(scenes_data, json_file, indent=2)

def add_scene_wrappers(filename):
    with open(filename, 'r') as file:
        data = json.load(file)

    # Add the required content
    wrapped_data = {"scenes": data}

    with open(filename, 'w') as file:
        json.dump(wrapped_data, file, indent=2)

# Example usage after generating all scenes
def fill_character_descriptions(story_json_path):
  """
  Fills character descriptions in the `characters` dictionary using Llama Lite Instruct-8B based on information from story.json.

  Args:
      story_json_path (str): Path to the story.json file containing scene information.
  """
  # Load story data from JSON
  with open(story_json_path, 'r') as f:
    story_data = json.load(f)
  scenes = story_data.get('scenes', [])

  # Extract character names and dialogue snippets for prompt generation
  character_names = set()
  character_prompts = {}
  for scene in scenes:
    for element in scene.get('story_elements', []):
      if element.get('element_type') == 'dialogue':
        character_name = element.get('content', {}).get('character_name')
        character_names.add(character_name)
        dialogue_text = element.get('content', {}).get('dialogue_text')
        # Combine dialogue snippets for each character (can be adjusted)
        if character_name in character_prompts:
          character_prompts[character_name].append(dialogue_text[:50])  # Limit snippet length
        else:
          character_prompts[character_name] = [dialogue_text[:50]]

  # Use Llama Lite Instruct-8B to generate character descriptions
  for character_name, dialogue_snippets in character_prompts.items():
    prompt = f"""Based on the following dialogue snippets, create a brief description of the character "{character_name}":

    * {', '.join(dialogue_snippets)}

    **Important:**

    * The description should be concise and capture the character's personality based on the provided dialogue.
    * Use complete sentences and proper grammar.
    """
    
    messages = [
      {
        "role": "system",
        "content": "You are a creative writer who can generate character descriptions based on a few dialogue snippets.",
      },
      {
        "role": "user",
        "content": prompt,
      },
    ]

    try:
      response = client.chat.completions.create(
          model="meta-llama/Meta-Llama-3-8B-Instruct-Lite",  # Replace with "text-davinci-003" for Instruct-8B
          messages=messages,
      )
      description = response.choices[0].message.content
      characters[character_name].description = description.strip()
      print(f"Generated description for {character_name}: {description}")
    except Exception as e:
      print(f"Error generating description for {character_name}: {e}")


def generate_visual_novel(prompts):
    scenes = []
    i = 0
    #story_idea = input('Please enter prompt for visual novel: ')
    story_idea = prompts[0]
    print("Generating initial scene...")
    scene1 = generate_visual_novel_scene(story_idea, first=True)
    scene1.scene_id = i
    i+=1
    scenes.append(scene1)
    while True:
        #usr = input('Please input idea or follow-up for next scene: ')
        usr = prompts[i]
        if '--end--' in usr:
            last_scene = generate_visual_novel_scene("Now, end the visual novel with a befitting ending lore.", first=False)
            last_scene.scene_id = i
            scenes.append(last_scene)
            break
        else:
            new_scene = generate_visual_novel_scene(usr, first=False)
            new_scene.scene_id = i
            scenes.append(new_scene)
        i+=1


    # Images
    client = Together(api_key="fb5107bddcd0f7f144ca41251d77bbb59f9f5f64cb21435473f15a2801d28d73")
    for scene in scenes:
        scene.background_image = f'./backgrounds/bg_{scene.scene_id}.png'
        response = client.images.generate(
            prompt=scene.setting,
            model="stabilityai/stable-diffusion-2-1",
            steps=10,
            n=1,
            height=768,
        )
        image_data = base64.b64decode(response.data[0].b64_json)
        image = Image.open(io.BytesIO(image_data))
        #image.show()
        image.save(scene.background_image)

    # Save the scenes to a JSON file
    save_scenes_to_json(scenes, 'story.json')
    print(f"Scenes have been saved to story.json")
    add_scene_wrappers('story.json')
    
    fill_character_descriptions('story.json')
    # Character personalization
    for character_name in characters.keys():
        #characters[character_name].description = input(f"Please specify appearance of the character {character_name} (the more details the better, option to automatically generate and skip this step will be added)")
        messages = [
            {
                "role": "system",
                "content": "You are a creative illustrator, and excel at creating good prompts for image generation.",
            },
            {
                "role": "user",
                "content": f'Craft a prompt for image generation (with openjourney model), so that i get realistic image of character face with this description - {characters[character_name].description}',
            },
        ]

        # Send the request to together.ai and parse the response
        promptgen = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct-Lite",
            messages=messages,
        )
        try:
            characters[character_name].description = promptgen.choices[0].message.content
        except:
            print('Prompt generation for character failed, falling back to user given prompt')
        
        character_img_path = f'./images/{character_name}.png'
        response = client.images.generate(
            prompt = characters[character_name].description,
            model="prompthero/openjourney",
            steps=20,
            n=2,
            width=512,
            height=512,
            seed=42,
        )
        image_data = base64.b64decode(response.data[0].b64_json)
        image = Image.open(io.BytesIO(image_data))
        #image.show()
        image.save(character_img_path)

if __name__ == '__main__':
    with open('prompts.txt', 'r') as f:
        prompts = [line.strip() for line in f.readlines()]

    generate_visual_novel(prompts)
    print("Visual novel generated successfully!")

