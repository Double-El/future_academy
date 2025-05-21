from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Configure CORS to allow all origins
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/api/test-key', methods=['POST', 'OPTIONS'])
def test_key():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.json
        api_key = data.get('api_key')

        if not api_key:
            return jsonify({'error': 'API key is required'}), 400

        # Set the API key
        openai.api_key = api_key

        # Make a simple test call
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=5
            )
            return jsonify({'status': 'valid'})
        except openai.error.AuthenticationError:
            return jsonify({'error': 'Invalid API key'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.json
        logger.debug(f"Received request data: {data}")
        
        agent_data = data.get('agent')
        message = data.get('message')
        api_key = data.get('api_key')

        if not api_key:
            logger.error("No API key provided")
            return jsonify({'error': 'API key is required'}), 400

        if not agent_data:
            logger.error("No agent data provided")
            return jsonify({'error': 'Agent data is required'}), 400

        if not message:
            logger.error("No message provided")
            return jsonify({'error': 'Message is required'}), 400

        # Set the API key for this request
        openai.api_key = api_key

        # Create a prompt based on the agent's data and the user's message
        prompt = f"""You are a {agent_data['role']} in a banking decision system. 
        Your current opinion is {agent_data['finalOpinion']['type']} with {agent_data['finalOpinion']['confidence']} confidence.
        Your reasoning: {agent_data['finalOpinion']['reasoning']}
        
        Your decision factors:
        {', '.join([f"{f['name']} (weight: {f['weight']}, score: {f['score']})" for f in agent_data['factors']])}
        
        User message: {message}
        
        Please respond as the {agent_data['role']}, maintaining your character and perspective."""

        logger.debug(f"Generated prompt: {prompt}")

        # Call OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=150
            )
            logger.debug(f"OpenAI response: {response}")
            return jsonify({'response': response.choices[0].message.content})

        except openai.error.AuthenticationError as e:
            logger.error(f"OpenAI Authentication Error: {str(e)}")
            return jsonify({'error': 'Invalid API key'}), 401
        except openai.error.RateLimitError as e:
            logger.error(f"OpenAI Rate Limit Error: {str(e)}")
            return jsonify({'error': 'Rate limit exceeded'}), 429
        except openai.error.APIError as e:
            logger.error(f"OpenAI API Error: {str(e)}")
            return jsonify({'error': 'OpenAI API error'}), 500

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/')
def serve_visualization():
    return send_from_directory('.', 'visualize.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0') 