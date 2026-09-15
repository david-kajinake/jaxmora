from django.conf import settings
from django.db.models import Q
from .models import Movie, Music, Comedy, VisualImage, Serie
from .serializers import (
    MovieSerializer,
    MusicSerializer,
    ComedySerializer,
    VisualImageSerializer,
    SerieSerializer,
)

class BaseSearchStrategy():
    """Base search for all search implementations"""
    def search(self, query: str, request):
        raise NotImplementedError("Search strategies must implement the search method.")


class ORMSearchStrategy(BaseSearchStrategy):
    """Approach 1: Django ORM icontains query across all content models."""
    def search(self, query: str, request):
        context = {'request': request}

        movies = Movie.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | 
            Q(category__icontains=query) | Q(production_studio__icontains=query) | 
            Q(owner__first_name__icontains=query) | Q(owner__other_name__icontains=query) | 
            Q(owner__username__icontains=query)
        ).select_related('owner')

        music = Music.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | 
            Q(category__icontains=query) | Q(owner__first_name__icontains=query) | 
            Q(owner__other_name__icontains=query) | Q(owner__username__icontains=query)
        ).select_related('owner')

        comedies = Comedy.objects.filter(
            Q(title__icontains=query) | Q(owner__first_name__icontains=query) | 
            Q(owner__other_name__icontains=query) | Q(owner__username__icontains=query)
        ).select_related('owner')

        visual_images = VisualImage.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | 
            Q(category__icontains=query) | Q(owner__first_name__icontains=query) | 
            Q(owner__other_name__icontains=query) | Q(owner__username__icontains=query)
        ).select_related('owner')

        series = Serie.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | 
            Q(category__icontains=query) | Q(owner__first_name__icontains=query) | 
            Q(owner__other_name__icontains=query) | Q(owner__username__icontains=query)
        ).select_related('owner')

        return{
            'movies': MovieSerializer( movies, many= True, context=context ).data,
            'music': MusicSerializer(music, many=True, context=context).data,
            'comedies': ComedySerializer(comedies, many=True, context=context).data,
            'visual_images': VisualImageSerializer(visual_images, many=True, context=context).data
        }



SEARCH_STRATEGIES = {
    'orm': ORMSearchStrategy
}


def get_search_strategy() -> BaseSearchStrategy:
    """Instantiates the search strategy configured in Django settings."""
    strategy_name = getattr(settings, 'SEARCH_STRATEGY', 'orm')
    strategy_class = SEARCH_STRATEGIES.get(strategy_name, ORMSearchStrategy)
    return strategy_class()