import graphene

from graphql_api.query import BenefactorQuery, CharityQuery

class Query(graphene.ObjectType, BenefactorQuery, CharityQuery):
    hello = graphene.String()

    def resolve_hello(self, info):
        return "This is a hello message"


schema = graphene.Schema(query=Query)
