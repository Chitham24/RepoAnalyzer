"""
Unified LLM client for RepoAnalyzer.
Provides a single interface for multiple LLM providers.
"""
from typing import Optional
import time
from config.settings import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    GROQ_API_KEY,
    GEMINI_API_KEY,
    LLM_MODEL_NAME,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
)


class LLMClient:
    """Unified interface for multiple LLM providers."""
    
    def __init__(self):
        self.provider = LLM_PROVIDER
        self.model_name = LLM_MODEL_NAME
        self.max_tokens = LLM_MAX_TOKENS
        self.temperature = LLM_TEMPERATURE
        
        # Initialize the appropriate provider client
        if self.provider == "openai":
            self._client = self._init_openai()
        elif self.provider == "groq":
            self._client = self._init_groq()
        elif self.provider == "gemini":
            self._client = self._init_gemini()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        # Set default model if not specified
        if not self.model_name:
            self.model_name = "gpt-4o-mini"
        
        return OpenAI(api_key=OPENAI_API_KEY)
    
    def _init_groq(self):
        """Initialize Groq client."""
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("Groq package not installed. Run: pip install groq")
        
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in environment")
        
        # Set default model if not specified
        if not self.model_name:
            self.model_name = "llama-3.3-70b-versatile"
        
        return Groq(api_key=GROQ_API_KEY)
    
    def _init_gemini(self):
        """Initialize Gemini client."""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("Google Generative AI package not installed. Run: pip install google-generativeai")
        
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in environment")
        
        # Set default model if not specified
        if not self.model_name:
            self.model_name = "gemini-2.5-flash"
        
        genai.configure(api_key=GEMINI_API_KEY)
        return genai.GenerativeModel(self.model_name)
    
    def _generate_openai(self, prompt: str) -> str:
        """Generate using OpenAI API."""
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=30,
            )
            
            content = response.choices[0].message.content
            if not content or not content.strip():
                raise ValueError("Empty response from OpenAI")
            
            return content.strip()
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _generate_groq(self, prompt: str) -> str:
        """Generate using Groq API."""
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=30,
            )
            
            content = response.choices[0].message.content
            if not content or not content.strip():
                raise ValueError("Empty response from Groq")
            
            return content.strip()
            
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def _generate_gemini(self, prompt: str) -> str:
        """Generate using Gemini API."""
        try:
            generation_config = {
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            }
            
            response = self._client.generate_content(
                prompt,
                generation_config=generation_config,
            )
            
            if not response.text or not response.text.strip():
                raise ValueError("Empty response from Gemini")
            
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def generate(self, prompt: str) -> str:
        """
        Generate text using the configured LLM provider.
        
        Args:
            prompt: Input prompt for the LLM
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If API call fails or returns empty response
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # Route to the appropriate provider
        if self.provider == "openai":
            return self._generate_openai(prompt)
        elif self.provider == "groq":
            return self._generate_groq(prompt)
        elif self.provider == "gemini":
            return self._generate_gemini(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")