from typing import List, Dict, Optional

import traceroot
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from traceroot.tracer import TraceOptions, trace

load_dotenv()

logger = traceroot.get_logger()


class VoiceResponseAgent:
    """Agent for generating healthcare-focused voice responses"""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        # Maximum words for roughly 30 seconds of speech (assuming 150-200 words per minute)
        self.max_words = 85
        self.system_prompt = (
            "You are a healthcare voice response agent. "
            "Your job is to create clear, empathetic, and informative responses "
            "that will be spoken to patients. "
            "IMPORTANT GUIDELINES for healthcare voice responses: "
            "1. Start with empathy and acknowledgment of the patient's concerns "
            "2. Use clear, simple language to explain medical concepts "
            "3. Include appropriate medical disclaimers naturally in speech "
            "4. Always recommend consulting healthcare providers for specific advice "
            "5. Structure responses in a clear, calming way "
            "6. Use a professional yet warm tone "
            "7. Avoid medical jargon or complex terminology "
            "8. Include natural pauses for information absorption "
            "9. Never provide specific diagnoses or treatment recommendations "
            "10. End with clear next steps or recommendations "
            "11. Maintain HIPAA compliance in all responses "
            "12. For urgent symptoms, emphasize the importance of immediate care "
            "13. When recommending doctors, present their qualifications naturally "
            f"14. CRITICAL: Keep your response to MAXIMUM {self.max_words} words for a 30-second audio output "
            "Your response will be read aloud to potentially anxious patients."
        )
        self.response_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", (
                "Patient transcript: {transcript}\n"
                "Healthcare response plan: {plan}\n"
                "Response type: {response_type}\n"
                "Desired tone: {tone}\n"
                "Available doctors: {doctor_recommendations}\n\n"
                f"Generate a natural, healthcare-focused voice response that addresses "
                f"the patient's query and includes appropriate doctor recommendations. "
                f"IMPORTANT: Keep response under {self.max_words} words for 30-second audio."
            ))
        ])

    @trace(TraceOptions(trace_params=True, trace_return_value=True))
    def generate_response(
        self,
        transcript: str,
        plan: str,
        response_type: str,
        tone: str,
        doctor_recommendations: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate a healthcare-focused voice response with doctor recommendations
        
        Args:
            transcript: Original patient query transcript
            plan: Response plan from healthcare planning agent
            response_type: Type of health response needed
            tone: Desired professional medical tone
            doctor_recommendations: List of recommended doctors with availability
            
        Returns:
            Generated text response optimized for medical communication
        """
        chain = self.response_prompt | self.llm
        
        # Format doctor recommendations for the prompt
        doctor_text = self._format_doctor_recommendations(doctor_recommendations)
        
        formatted_prompt = self.response_prompt.format(
            transcript=transcript,
            plan=plan,
            response_type=response_type,
            tone=tone,
            doctor_recommendations=doctor_text
        )
        logger.info(f"HEALTHCARE RESPONSE AGENT prompt:\n{formatted_prompt}")
        
        response = chain.invoke({
            "transcript": transcript,
            "plan": plan,
            "response_type": response_type,
            "tone": tone,
            "doctor_recommendations": doctor_text
        })
        
        # Clean up the response for voice synthesis
        text_response = response.content.strip()
        text_response = self._clean_for_voice(text_response)
        
        logger.info(f"Healthcare response generated for transcript: {transcript}")
        logger.info(f"Response type: {response_type}, Tone: {tone}")
        logger.info(f"Final word count: {len(text_response.split())} words")
        logger.info(f"Generated response preview: {text_response[:200]}...")
        
        return text_response

    def _format_doctor_recommendations(
        self,
        recommendations: Optional[List[Dict]]
    ) -> str:
        """Format doctor recommendations for natural speech"""
        if not recommendations:
            return "No specific doctor recommendations available at this time."
            
        formatted = []
        for rec in recommendations:
            doctor_info = (
                f"Dr. {rec['name']}, "
                f"specializing in {rec['specialty']}"
            )
            if rec['sub_specialty']:
                doctor_info += f" with expertise in {rec['sub_specialty']}"
            
            doctor_info += f". Next available appointment: {rec['next_available']}"
            
            if rec.get('reason'):
                doctor_info += f". {rec['reason']}"
                
            formatted.append(doctor_info)
            
        return "\n".join(formatted)

    def _clean_for_voice(self, text: str) -> str:
        """
        Clean text to be more voice-friendly while preserving medical clarity
        
        Args:
            text: Raw response text
            
        Returns:
            Voice-optimized text for medical communication
        """
        # Remove markdown formatting
        text = text.replace("**", "").replace("*", "")
        text = text.replace("##", "").replace("#", "")
        
        # Remove excessive punctuation while preserving clarity
        text = text.replace("...", ", ")
        
        # Ensure proper spacing for clear medical communication
        text = " ".join(text.split())
        
        return text


def create_voice_response_agent():
    return VoiceResponseAgent() 