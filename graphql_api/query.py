import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

from charities.models import Benefactor, Charity, Task


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "first_naem", "last_name")


class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        fields = "__all__"


class BenefactorType(DjangoObjectType):
    class Meta:
        model = Benefactor
        fields = "__all__"

    tasks = graphene.List(of_type=graphene.NonNull(TaskType), required=True)

    def resolve_tasks(self, info):
        return self.tasks.all()


class CharityType(DjangoObjectType):
    class Meta:
        model = Charity
        fields = "__all__"
    
    tasks = graphene.List(of_type=graphene.NonNull(TaskType), required=True)

    def resolve_tasks(self, info):
        return self.tasks.all()


class BenefactorQuery:
    benefactor = graphene.Field(
        BenefactorType, id=graphene.Argument(graphene.ID, required=True)
    )

    def resolve_benefactor(self, info, **kwargs):
        benefactor_id = kwargs.get("id")

        try:
            return Benefactor.objects.get(id=benefactor_id)
        except:
            return None


class CharityQuery:
    charity = graphene.Field(
        CharityType, id=graphene.Argument(graphene.ID, required=True)
    )

    def resolve_charity(self, info, **kwargs):
        charity_id = kwargs.get("id")

        try:
            return Charity.objects.get(id=charity_id)
        except:
            return None
