"""View module for handling requests about game types"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Event, Game, Gamer
from rest_framework.decorators import action
from levelupapi.models import EventGamer

class EventView(ViewSet):
    """Level up game types view"""

    def retrieve(self, request, pk):
      event = Event.objects.get(pk=pk)
      serializer = EventSerializer(event)
      return Response(serializer.data)

    def list(self, request):
      events = Event.objects.all()
      uid = request.META['HTTP_AUTHORIZATION']
      gamer = Gamer.objects.get(uid=uid)
      
      for event in events:
        # Check to see if there is a row in the Event Games table that has the passed in gamer and event
        event.joined = len(EventGamer.objects.filter(
        gamer=gamer, event=event)) > 0
      serializer = EventSerializer(events, many=True)

      return Response(serializer.data)
    
    def create(self, request):
      game = Game.objects.get(pk=request.data["game"])
      organizer = Gamer.objects.get(uid=request.data["userId"])

      event = Event.objects.create(
          game=game,
          description=request.data["description"],
          date=request.data["date"],
          time=request.data["time"],
          organizer=organizer,
      )
      serializer = EventSerializer(event)
      return Response(serializer.data)
    
    def update(self, request, pk):
      event = Event.objects.get(pk=pk)
      event.description = request.data["description"]
      event.date = request.data["date"]
      event.time = request.data["time"]

      game = Game.objects.get(pk=request.data["gameId"])
      event.game = game
      event.save()

      return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, pk):
      event = Event.objects.get(pk=pk)
      event.delete()
      return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['post'], detail=True)
    def signup(self, request, pk):
        """Post request for a user to sign up for an event"""

        gamer = Gamer.objects.get(uid=request.META['HTTP_AUTHORIZATION'])
        event = Event.objects.get(pk=pk)
        attendee = EventGamer.objects.create(
            gamer=gamer,
            event=event
        )
        return Response({'message': 'Gamer added'}, status=status.HTTP_201_CREATED)
    
    @action(methods=['delete'], detail=True)
    def leave(self, request, pk):
        """Delete request for a user to sign up for an event"""

        gamer = Gamer.objects.get(uid=request.META['HTTP_AUTHORIZATION'])
        event = Event.objects.get(pk=pk)
        attendee = EventGamer.objects.get(
            gamer=gamer,
            event=event
        )
        attendee.delete()
        return Response({'message': 'Gamer left'}, status=status.HTTP_204_NO_CONTENT)
      
class EventSerializer(serializers.ModelSerializer):
    class Meta:
      model = Event
      fields = ('id', 'game', 'description', 'date', 'time', 'organizer', 'joined')
