from django.conf import settings
from django.db.models import Q, CharField
from django.db.models.functions import Cast
from .models import Movie, Music, Comedy, VisualImage, Serie
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
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


"""Approach 1: Django ORM icontains query across all content models."""
class ORMSearchStrategy(BaseSearchStrategy):
    def search(self, query: str, request):
        context = {'request': request}

        movies = Movie.objects.annotate(
            year_str= Cast('year_released', output_field= CharField())
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query) | 
            Q(category__icontains=query) | Q(production_studio__icontains=query) | 
            Q(year_str__icontains=query)| Q(owner__first_name__icontains=query) | 
            Q(owner__other_name__icontains=query) | 
            Q(owner__username__icontains=query)
        ).select_related('owner')

        music = Music.objects.annotate(
            year_str= Cast('year_released', output_field= CharField())
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query) | 
            Q(category__icontains=query) | Q(owner__first_name__icontains=query) | 
            Q(year_str__icontains=query) | Q(owner__other_name__icontains=query) | 
            Q(owner__username__icontains=query)
        ).select_related('owner')

        comedies = Comedy.objects.annotate(
            year_str= Cast('year_released', output_field= CharField())
        ).filter(
            Q(title__icontains=query) | Q(owner__first_name__icontains=query) | 
            Q(owner__other_name__icontains=query) | Q(owner__username__icontains=query) |
            Q(year_str__icontains=query)
        ).select_related('owner')

        visual_images = VisualImage.objects.annotate(
            year_str= Cast('year_released', output_field= CharField())
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query) | 
            Q(category__icontains=query) | Q(owner__first_name__icontains=query) | 
            Q(owner__other_name__icontains=query) | Q(owner__username__icontains=query)|
            Q(year_str__icontains=query)
        ).select_related('owner')

        series = Serie.objects.annotate(
            year_str= Cast('year_released', output_field= CharField())
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query) | 
            Q(category__icontains=query) | Q(owner__first_name__icontains=query) | 
            Q(owner__other_name__icontains=query) | Q(owner__username__icontains=query) |
            Q(year_str__icontains=query)
        ).select_related('owner')

        return{
            'movies': MovieSerializer( movies, many= True, context=context ).data,
            'music': MusicSerializer(music, many=True, context=context).data,
            'comedies': ComedySerializer(comedies, many=True, context=context).data,
            'visual_images': VisualImageSerializer(visual_images, many=True, context=context).data,
            'series': SerieSerializer(series, many= True, context=context).data
       }
    

"""Approach 2: PostgresQL Full-text search with SearchVector / SearchRank"""
class PostgresSearchStrategy(BaseSearchStrategy):
    def _search_model(self, model_Class, serializer_class, query: str, request):
        context= {'request': request}

        #Assign weights: A 'Highest relevance' to title, B to category / owner, C to description
        vector = (
            SearchVector('title', weight = 'A')+
            SearchVector('category', weight = 'B')+
            SearchVector('owner__first_name', weight = 'B')+
            SearchVector('owner__other_name', weight = 'B')+
            SearchVector('owner__username', weight = 'B')+
            SearchVector('description', weight = 'C')
        )

        search_query = SearchQuery(query)

        #Build Base-annotated queryset
        qs = model_Class.objects.annotate(
            search = vector,
            rank = SearchRank(vector, search_query)
        )
        #filter by rank match
        filter_condition = Q(rank__gte=0.01)

        #include numeric year match if query is digits
        if hasattr(model_Class, 'year_released') and query.isdigit():
            filter_condition != Q(year_released = int(query))
        results = (
            qs.filter(filter_condition).select_related('owner').order_by('-rank')
        )

        return serializer_class(results, may= True, context= context ).data

    def search(self, query: str, request):
        return{
            'movies': self._search_model(Movie, MovieSerializer, query, request),
            'music': self._search_model(Music, MusicSerializer, query, request),
            'comedies': self._search_model(Comedy, ComedySerializer, query, request),
            'series': self._search_model(Serie, SerieSerializer, query, request),
            'visual_images': self._search_model(VisualImage, VisualImageSerializer, query, request),
        }



"""Approach 3: Reserved for Meilisearch / Elasticsearch integration"""
class ExternalEngineSearchStrategy(BaseSearchStrategy):
    def search(self, query: str, request):
        """Implementation goes here"""
        pass






SEARCH_STRATEGIES = {
    'orm': ORMSearchStrategy,
    'postgres': PostgresSearchStrategy
}




def get_search_strategy() -> BaseSearchStrategy:
    """Instantiates the search strategy configured in Django settings."""
    strategy_name = getattr(settings, 'SEARCH_STRATEGY', 'orm')
    strategy_class = SEARCH_STRATEGIES.get(strategy_name, ORMSearchStrategy)
    return strategy_class()