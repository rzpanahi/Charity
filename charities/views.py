from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, CreateAPIView

from accounts.permissions import IsCharityOwner, IsBenefactor
from charities.models import Task, Benefactor, Charity
from charities.serializers import (
    TaskSerializer,
    CharitySerializer,
    BenefactorSerializer,
)


class BenefactorRegistration(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BenefactorSerializer

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=request.user)

        return Response(status=status.HTTP_201_CREATED)


class CharityRegistration(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CharitySerializer

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=request.user)

        return Response(status=status.HTTP_201_CREATED)


class Tasks(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all_related_tasks_to_user(self.request.user)

    def post(self, request, *args, **kwargs):
        data = {**request.data, "charity_id": request.user.charity.id}
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            self.permission_classes = [
                IsAuthenticated,
            ]
        else:
            self.permission_classes = [
                IsCharityOwner,
            ]

        return [permission() for permission in self.permission_classes]

    def filter_queryset(self, queryset):
        filter_lookups = {}
        for name, value in Task.filtering_lookups:
            param = self.request.GET.get(value)
            if param:
                filter_lookups[name] = param
        exclude_lookups = {}
        for name, value in Task.excluding_lookups:
            param = self.request.GET.get(value)
            if param:
                exclude_lookups[name] = param

        return queryset.filter(**filter_lookups).exclude(**exclude_lookups)


class TaskRequest(RetrieveAPIView):
    permission_classes = [
        IsBenefactor,
    ]
    queryset = Task.objects.all()

    def retrieve(self, request: Request, task_id: int):
        task = self.get_object()

        if not task.state == "P":
            return Response(
                data={"detail": "This task is not pending."},
                status=status.HTTP_404_NOT_FOUND,
            )

        benefactor = Benefactor.objects.get(user=request.user)
        task.assign_to_benefactor(benefactor=benefactor)

        return Response(data={"detail": "Request sent."}, status=status.HTTP_200_OK)

    def get_object(self):
        return get_object_or_404(Task.objects.all(), id=self.kwargs["task_id"])


class TaskResponse(APIView):
    permission_classes = [
        IsCharityOwner,
    ]

    def post(self, request: Request, task_id: int):
        task: Task = get_object_or_404(Task, id=task_id)

        charity = Charity.objects.get(user=request.user)

        response = request.data["response"]

        if response not in ["A", "R"]:
            return Response(
                data={"detail": 'Required field ("A" for accepted / "R" for rejected)'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not task.state == "W":
            return Response(
                data={"detail": "This task is not waiting."},
                status=status.HTTP_404_NOT_FOUND,
            )

        task.response_to_benefactor_request(response=response)

        return Response(data={"detail": "Response sent."}, status=status.HTTP_200_OK)


class DoneTask(APIView):
    permission_classes = [
        IsCharityOwner,
    ]

    def post(self, request: Request, task_id: int):
        task: Task = get_object_or_404(Task, id=task_id)

        if task.state != Task.TaskStatus.ASSIGNED:
            return Response(data={'detail': 'Task is not assigned yet.'}, status=status.HTTP_404_NOT_FOUND)

        task.done()


        return Response(data={'detail': 'Task has been done successfully.'}, status=status.HTTP_200_OK)