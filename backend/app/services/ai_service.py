import google.generativeai as genai
from app.core.config import get_settings
from typing import Optional


class AIService:
    """Service for integrating with Google Gemini AI"""
    
    def __init__(self):
        settings = get_settings()
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    async def generate_lesson_summary(self, transcript: str) -> Optional[str]:
        """
        Generate a 3-sentence summary of a class transcript using Gemini AI.
        
        Args:
            transcript: The full transcript of the class session
            
        Returns:
            A 3-sentence summary or None if AI is not configured
        """
        if not self.model:
            return None
        
        try:
            prompt = f"""
            You are an educational assistant. Summarize the following class transcript 
            into exactly 3 clear and concise sentences that capture the main topics covered, 
            key learning objectives, and any important announcements or homework.
            
            Transcript:
            {transcript}
            
            Summary (3 sentences):
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        
        except Exception as e:
            print(f"Error generating AI summary: {e}")
            return None
    
    async def generate_session_notes(
        self, 
        teacher_name: str,
        duration_minutes: float,
        student_names: list[str],
        topics: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate structured session notes based on session metadata.
        
        Args:
            teacher_name: Name of the teacher
            duration_minutes: Duration of the session
            student_names: List of student names who attended
            topics: Optional topics covered
            
        Returns:
            Formatted session notes or None if AI is not configured
        """
        if not self.model:
            return None
        
        try:
            prompt = f"""
            Generate professional session notes for this tutoring session:
            
            Teacher: {teacher_name}
            Duration: {duration_minutes:.0f} minutes
            Students: {', '.join(student_names)}
            {f'Topics: {topics}' if topics else ''}
            
            Create a brief, professional summary suitable for academic records.
            Include attendance, duration, and if topics are provided, summarize the learning outcomes.
            Keep it to 2-3 sentences.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        
        except Exception as e:
            print(f"Error generating session notes: {e}")
            return None


# Singleton instance
ai_service = AIService()
