"""
LLM Provider Abstraction Layer
Supports multiple LLM providers: Groq (default/free), Gemini, OpenAI
"""

import os
from typing import Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import logging

logger = logging.getLogger(__name__)

ProviderType = Literal["groq", "gemini", "openai"]

# Provider configurations
PROVIDER_CONFIGS = {
    "groq": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.0,
        "description": "Groq (Free Tier - Fast)",
        "free": True
    },
    "gemini": {
        "model": "gemini-2.0-flash-exp",
        "temperature": 0.0,
        "description": "Google Gemini (Free Tier)",
        "free": True
    },
    "openai": {
        "model": "gpt-4o",
        "temperature": 0.0,
        "description": "OpenAI GPT-4o (Paid)",
        "free": False
    }
}


def get_llm(provider: Optional[str] = None, temperature: Optional[float] = None):
    """
    Get LLM instance based on provider selection.
    
    Args:
        provider: LLM provider ("groq", "gemini", "openai"). 
                 If None, uses LLM_PROVIDER from env (defaults to "groq")
        temperature: Override default temperature
    
    Returns:
        LLM instance ready for use
    
    Raises:
        ValueError: If provider is invalid or API key missing
    """
    # Determine provider
    if provider is None:
        provider = os.getenv("LLM_PROVIDER", "groq").lower()
    
    provider = provider.lower()
    
    if provider not in PROVIDER_CONFIGS:
        raise ValueError(f"Invalid provider: {provider}. Must be one of: {list(PROVIDER_CONFIGS.keys())}")
    
    # Initialize callback handler for forensic logging
    from utils.observability import LoggingCallbackHandler
    
    config = PROVIDER_CONFIGS[provider]
    temp = temperature if temperature is not None else config["temperature"]
    
    callbacks = [LoggingCallbackHandler(provider=provider, model=config["model"])]
    
    logger.info(f"Initializing LLM provider: {provider} (model: {config['model']})")
    
    try:
        if provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment")
            
            return ChatGroq(
                model=config["model"],
                temperature=temp,
                groq_api_key=api_key,
                callbacks=callbacks
            )
        
        elif provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            
            return ChatGoogleGenerativeAI(
                model=config["model"],
                temperature=temp,
                google_api_key=api_key,
                callbacks=callbacks
            )
        
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            
            return ChatOpenAI(
                model=config["model"],
                temperature=temp,
                api_key=api_key,
                callbacks=callbacks
            )
    
    except Exception as e:
        logger.error(f"Failed to initialize {provider}: {e}")
        raise


def get_llm_with_fallback(preferred_provider: Optional[str] = None, temperature: Optional[float] = None):
    """
    Get LLM with automatic fallback to other providers.
    Tries: preferred → groq → gemini → openai
    
    Args:
        preferred_provider: Preferred provider to try first
        temperature: Temperature setting
    
    Returns:
        Tuple of (llm_instance, provider_used)
    """
    # Check if fallback is enabled
    enable_fallback = os.getenv("ENABLE_FALLBACK", "true").lower() == "true"
    
    if not enable_fallback:
        # No fallback - just return preferred provider
        provider = preferred_provider or os.getenv("LLM_PROVIDER", "groq")
        llm = get_llm(provider, temperature)
        return llm, provider
    
    # Fallback chain: preferred → groq → gemini → openai
    fallback_chain = []
    
    if preferred_provider:
        fallback_chain.append(preferred_provider)
    
    # Add remaining providers in order
    for p in ["groq", "gemini", "openai"]:
        if p not in fallback_chain:
            fallback_chain.append(p)
    
    # Try each provider
    last_error = None
    for provider in fallback_chain:
        try:
            llm = get_llm(provider, temperature)
            if provider != (preferred_provider or os.getenv("LLM_PROVIDER", "groq")):
                logger.warning(f"Fell back to provider: {provider}")
            return llm, provider
        except Exception as e:
            logger.warning(f"Provider {provider} failed: {e}")
            last_error = e
            continue
    
    # All providers failed
    raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")


def get_available_providers():
    """
    Get list of available providers based on API keys in environment.
    
    Returns:
        List of tuples: (provider_name, config_dict)
    """
    available = []
    
    for provider, config in PROVIDER_CONFIGS.items():
        # Check if API key exists
        key_var = f"{provider.upper()}_API_KEY"
        if os.getenv(key_var):
            available.append((provider, config))
    
    return available


def get_provider_info(provider: str):
    """Get configuration info for a provider."""
    return PROVIDER_CONFIGS.get(provider.lower())
