from rest_framework.fields import CharField, ChoiceField
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from MHacks.models import Event as EventModel, Location as LocationModel
from serializers import UnixEpochDateField, GenericListCreateModel, GenericUpdateDestroyModel, DurationInSecondsField


class EventSerializer(ModelSerializer):
    id = CharField(read_only=True)
    start = UnixEpochDateField()
    locations = PrimaryKeyRelatedField(many=True, pk_field=CharField(),
                                       queryset=LocationModel.objects.all().filter(deleted=False))
    duration = DurationInSecondsField()
    category = ChoiceField(choices=EventModel.CATEGORIES)

    class Meta:
        model = EventModel
        fields = ('id', 'name', 'info', 'start', 'duration', 'locations', 'category', 'approved')


class Events(GenericListCreateModel):
    """
    Events are the objects that show up on the calendar view and represent specific planned events at the hackathon.
    """
    serializer_class = EventSerializer
    query_set = EventModel.objects.none()

    def get_queryset(self):
        date_last_updated = super(Events, self).get_queryset()
        if date_last_updated:
            query_set = EventModel.objects.all().filter(last_updated__gte=date_last_updated)
        else:
            query_set = EventModel.objects.all().filter(deleted=False)
        if not self.request.user.has_perm('mhacks.change_event'):
            return query_set.filter(approved=True)
        return query_set


class Event(GenericUpdateDestroyModel):
    serializer_class = EventSerializer
    queryset = EventModel.objects.all()
