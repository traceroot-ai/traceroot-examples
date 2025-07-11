# Healthcare Voice Agent System

A multi-agent voice processing system designed for healthcare communication. This system converts patient voice queries to text, processes them with AI agents, and generates empathetic, informative voice responses with doctor recommendations.

## Features

- 🎤 Speech-to-Text conversion using OpenAI Whisper
- 🧠 Intelligent healthcare response planning
- 👩‍⚕️ Doctor recommendation and scheduling
- 💬 Natural language response generation
- 🔊 High-quality text-to-speech synthesis
- 📊 Visual workflow graph generation

## Architecture

The system follows a healthcare-focused workflow:

```
Input Audio → STT Agent → Healthcare Plan Agent → Doctor Search → Medical Response Agent → TTS Agent → Output Audio
```

# Setup

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=your_api_key_here
```

# Run

```bash
cd ../../
python examples/healthcare_voice_agent/create_input_audio.py  # Generate test input
python examples/healthcare_voice_agent/main.py  # Run the system
```

## Components

- `main.py`: Core system orchestration
- `stt_agent.py`: Speech-to-Text conversion
- `plan_agent.py`: Healthcare response planning
- `scheduling_agent.py`: Doctor recommendations
- `response_agent.py`: Medical response generation
- `tts_agent.py`: Text-to-Speech synthesis
- `data/doctors.json`: Doctor database

## Example Input

The system comes with a sample healthcare query:
```
"Hi, I've been experiencing some concerning symptoms lately. For the past two weeks, 
I've been getting dizzy spells, especially when standing up quickly. I also notice 
I'm more tired than usual, and sometimes my heart feels like it's racing. I've been 
trying to stay hydrated, but I'm not sure if I should be worried about these symptoms. 
What should I do?"
```

## Output

The system generates:
1. A workflow visualization (`healthcare_voice_agent_graph.png`)
2. A voice response (`output_audio.wav`) containing:
   - Medical guidance
   - Doctor recommendations
   - Available appointment times
   - Next steps

## Dependencies

See `requirements.txt` for full list of dependencies:
- langchain & langgraph: Agent orchestration
- openai: GPT-4 for response generation
- whisper: Speech recognition
- coqui-tts: Text-to-speech synthesis

## Important Notes

- This system is designed for general health information only
- Not a replacement for professional medical advice
- Always directs users to appropriate healthcare providers
- Maintains HIPAA compliance in all interactions
- Includes appropriate medical disclaimers 