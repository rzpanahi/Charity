from graphene_django.views import GraphQLView
from .schema import schema



class GraphQLView(GraphQLView):
    schema = schema