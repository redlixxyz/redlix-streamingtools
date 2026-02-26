from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from threading import Thread
import queue
import io
import os
import tempfile

# DP3MEDIA Streaming Tools
### This File is Part of StreamingTools Beta v.2.0. 
# TTS Module from 30.10.2025

class TTSManager:
    def __init__(self):
        self.tts_queue = queue.Queue()
        self.running = False
        self.worker_thread = None
        self.default_language = 'fr'  # Default language fallback
        self.tld = 'fr'  # French accent, ui ui Baguette Paris Croissant
        self._start_worker()
    
    def _start_worker(self):
        """Start the worker thread for processing TTS queue"""
        self.running = True
        self.worker_thread = Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
    
    def _process_queue(self):
        """Process TTS requests from the queue"""
        while self.running:
            try:
                # Get text from queue with timeout
                text = self.tts_queue.get(timeout=1)
                if text:
                    self._speak(text)
                self.tts_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing TTS queue: {e}")
    
    def _detect_language(self, text):
        """Detect the language of the text"""
        try:
            from langdetect import detect
            detected_lang = detect(text)
            return detected_lang
        except:
            # Fall back to default language if detection fails
            return self.default_language
    
    def _speak(self, text):
        """Actually speak the text using Google TTS"""
        try:
            # Clean the text
            cleaned_text = self._clean_text(text)
            if not cleaned_text:
                return
            
            # Detect language automatically
            detected_lang = self._detect_language(cleaned_text)
            
            # Generate speech using gTTS with detected language and French accent
            tts = gTTS(text=cleaned_text, lang=detected_lang, tld=self.tld, slow=False)
            
            # Save to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
                tts.save(temp_file)
            
            # Load and play the audio
            audio = AudioSegment.from_mp3(temp_file)
            play(audio)
            
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except:
                pass
                
        except Exception as e:
            print(f"Error speaking text: {e}")
    
    def _clean_text(self, text):
        """Clean text by removing emojis and special characters"""
        import re
        # Remove emoji patterns
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        cleaned = emoji_pattern.sub('', text)
        # Remove multiple spaces
        cleaned = ' '.join(cleaned.split())
        return cleaned.strip()
    
    def speak_async(self, text):
        """Add text to the TTS queue for async speaking"""
        if text and text.strip():
            self.tts_queue.put(text)
    
    def set_language(self, lang='de', tld='fr'):
        """
        Set the default fallback language and accent for TTS
        Note: Language will be auto-detected per text, this sets the fallback
        Accent is always French (tld='fr')
        """
        self.default_language = lang
        self.tld = tld
    
    def stop(self):
        """Stop the TTS manager"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2)

# Global TTS manager instance
tts_manager = TTSManager()

def speak(text):
    """Convenience function to speak text"""
    tts_manager.speak_async(text)

def set_voice(language='fr', accent='fr'):
    """Convenience function to change default fallback language (accent is always French)"""
    tts_manager.set_language(language, accent)