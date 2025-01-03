from flask import Flask, request, render_template, jsonify
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)

def generate_cocktail_recipe(ingredients, cocktail_type):
    prompt = f"""
    You are a mixologist. Based on the following ingredients: {', '.join(ingredients)},
    and the desired cocktail type: {cocktail_type}, generate a cocktail recipe.
    The output should include:
    1. The name of the cocktail.
    2. The full list of ingredients with measurements.
    3. A step-by-step guide to preparing the cocktail.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a knowledgeable mixologist."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    return response['choices'][0]['message']['content']

def parse_recipe_for_steps(recipe_text):
    steps = []
    lines = recipe_text.split("\n")
    for line in lines:
        if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
            steps.append(line.strip())
    return steps

def generate_step_image(step_description):
    prompt = f"Generate an illustration for the following cocktail preparation step: {step_description}"
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response['data'][0]['url']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    ingredients = data['ingredients'].split(",")
    cocktail_type = data['cocktail_type']

    # Generate recipe
    recipe = generate_cocktail_recipe(ingredients, cocktail_type)

    # Parse steps and generate images
    steps = parse_recipe_for_steps(recipe)
    images = [generate_step_image(step) for step in steps]

    return jsonify({
        "recipe": recipe,
        "steps": steps,
        "images": images
    })

if __name__ == '__main__':
    app.run(debug=True)