import os
import numpy as np
import random
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Generate and store an embedding for a random movie in the database"

    def handle(self, *args, **kwargs):
        # Load OpenAI API key
        load_dotenv('../openAI.env')
        client = OpenAI(api_key=os.environ.get('openai_apikey'))

        # Fetch all movies from the database
        movies = list(Movie.objects.all())  # Convert to list for random selection
        self.stdout.write(f"Found {len(movies)} movies in the database")

        if not movies:
            self.stdout.write(self.style.WARNING("No movies available to generate an embedding."))
            return

        # Function to get embedding
        def get_embedding(text):
            response = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            )
            return np.array(response.data[0].embedding, dtype=np.float32)

        # Try to generate an embedding for a random movie
        attempts = 0
        max_attempts = 10  # Limit the number of attempts to avoid infinite loops

        while attempts < max_attempts:
            random_movie = random.choice(movies)
            self.stdout.write(f"Trying to generate embedding for: {random_movie.title}")

            try:
                emb = get_embedding(random_movie.description)
                # Store embedding as binary in the database
                random_movie.emb = emb.tobytes()
                random_movie.save()
                self.stdout.write(self.style.SUCCESS(f"✅ Successfully stored embedding for: {random_movie.title}"))
                
                # Show the embedding result
                self.stdout.write(f"Embedding: {emb}")  # Display the embedding
                break  # Exit the loop if successful
            except Exception as e:
                self.stderr.write(f"❌ Failed to generate embedding for {random_movie.title}: {e}")
                attempts += 1

        if attempts == max_attempts:
            self.stdout.write(self.style.ERROR("Reached maximum attempts without success."))
        else:
            self.stdout.write(self.style.SUCCESS("🎯 Finished generating embedding for a random movie."))