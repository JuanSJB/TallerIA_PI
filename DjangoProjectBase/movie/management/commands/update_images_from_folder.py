# your_app/management/commands/update_movies.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from movie.models import Movie

class Command(BaseCommand):
    help = 'Update movie images in a cyclic manner based on files in media/movie/images/'

    def handle(self, *args, **kwargs):
        images_dir = os.path.join(settings.MEDIA_ROOT, 'movie/images/')
        
        # Get a list of all image files in the directory
        image_files = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]
        
        # Sort the image files to maintain a consistent order
        image_files.sort()

        # Get all movies
        movies = list(Movie.objects.all())
        num_movies = len(movies)
        num_images = len(image_files)

        if num_movies == 0:
            self.stdout.write(self.style.WARNING('No movies found in the database.'))
            return

        if num_images == 0:
            self.stdout.write(self.style.WARNING('No images found in the specified directory.'))
            return

        # Update each movie with an image in a cyclic manner
        for i, movie in enumerate(movies):
            # Get the corresponding image file in a cyclic manner
            image_index = i % num_images
            movie.image = f'movie/images/{image_files[image_index]}'
            movie.save()
            self.stdout.write(self.style.SUCCESS(f'Updated image for movie: {movie.title} with {image_files[image_index]}'))