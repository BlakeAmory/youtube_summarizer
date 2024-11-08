from django.core.management.base import BaseCommand
from django.conf import settings
from summarizer.utils import get_chat_model
import os


class Command(BaseCommand):
    help = "Test the Groq API connection"

    def handle(self, *args, **options):
        self.stdout.write(
            f"GROQ_API_KEY from settings: {settings.GROQ_API_KEY[:5]}...{settings.GROQ_API_KEY[-5:]}"
        )
        self.stdout.write(
            f"GROQ_API_KEY from environment: {os.environ.get('GROQ_API_KEY', 'Not set')[:5]}...{os.environ.get('GROQ_API_KEY', 'Not set')[-5:]}"
        )

        try:
            chat_model = get_chat_model()
            messages = [{"role": "user", "content": "Say hello!"}]
            response = chat_model.invoke(messages)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Groq API test successful. Response: {response.content}"
                )
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Groq API test failed. Error: {str(e)}")
            )
