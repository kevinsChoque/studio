import re

from django.core.files.storage import default_storage
from django_filters.rest_framework import DjangoFilterBackend
from django_s3_storage.storage import S3Error
from le_utils.constants import exercises
from le_utils.constants import format_presets
from rest_framework.permissions import IsAuthenticated

from contentcuration.models import AssessmentItem
from contentcuration.models import ContentNode
from contentcuration.models import File
from contentcuration.models import generate_object_storage_name
from contentcuration.viewsets.base import BulkCreateMixin
from contentcuration.viewsets.base import BulkListSerializer
from contentcuration.viewsets.base import BulkModelSerializer
from contentcuration.viewsets.base import BulkUpdateMixin
from contentcuration.viewsets.base import RequiredFilterSet
from contentcuration.viewsets.base import ValuesViewset
from contentcuration.viewsets.common import NotNullArrayAgg
from contentcuration.viewsets.common import UserFilteredPrimaryKeyRelatedField
from contentcuration.viewsets.common import UUIDInFilter
from contentcuration.viewsets.common import UUIDRegexField


exercise_image_filename_regex = re.compile(
    r"\!\[[^]]*\]\(\${placeholder}/([a-f0-9]{{32}}\.[0-9a-z]+)\)".format(
        placeholder=exercises.IMG_PLACEHOLDER
    )
)


class AssessmentItemFilter(RequiredFilterSet):
    contentnode__in = UUIDInFilter(name="contentnode")

    class Meta:
        model = AssessmentItem
        fields = (
            "contentnode",
            "contentnode__in",
        )


def get_filenames_from_assessment(assessment_item):
    # Get unique checksums in the assessment item text fields markdown
    # Coerce to a string, for Python 2, as the stored data is in unicode, and otherwise
    # the unicode char in the placeholder will not match
    return set(
        exercise_image_filename_regex.findall(
            str(
                assessment_item.question
                + assessment_item.answers
                + assessment_item.hints
            )
        )
    )


class AssessmentListSerializer(BulkListSerializer):
    def set_files(self, all_objects):
        all_filenames = [get_filenames_from_assessment(obj) for obj in all_objects]
        files_to_delete = File.objects.none()
        files_to_create = []
        for aitem, filenames in zip(all_objects, all_filenames):
            checksums = [filename.split(".")[0] for filename in filenames]
            files_to_delete |= aitem.files.exclude(checksum__in=checksums)
            no_files = [
                filename
                for filename in filenames
                if filename.split(".")[0]
                in (checksums - set(aitem.files.values_list("checksum", flat=True)))
            ]
            for filename in no_files:
                checksum = filename.split(".")[0]
                file_path = generate_object_storage_name(checksum, filename)
                try:
                    file_object = default_storage.open(file_path)
                    # Only do this if the file already exists, otherwise, hope it comes into being later!
                    files_to_create.append(
                        File(
                            assessment_item=aitem,
                            checksum=checksum,
                            file_on_disk=file_object,
                            preset_id=format_presets.EXERCISE_IMAGE,
                        )
                    )
                except S3Error:
                    # File does not exist yet not much we can do about that here.
                    pass
        files_to_delete.delete()
        File.objects.bulk_create(files_to_create)

    def create(self, validated_data):
        all_objects = super(AssessmentListSerializer, self).create(validated_data)
        self.set_files(all_objects)
        return all_objects

    def update(self, queryset, all_validated_data):
        all_objects = super(AssessmentListSerializer, self).update(
            queryset, all_validated_data
        )
        self.set_files(all_objects)
        return all_objects


class AssessmentItemSerializer(BulkModelSerializer):
    # This is set as editable=False on the model so by default DRF does not allow us
    # to set it.
    assessment_id = UUIDRegexField()
    contentnode = UserFilteredPrimaryKeyRelatedField(
        queryset=ContentNode.objects.all(), required=False
    )

    class Meta:
        model = AssessmentItem
        fields = (
            "question",
            "type",
            "answers",
            "contentnode",
            "assessment_id",
            "hints",
            "raw_data",
            "order",
            "source_url",
            "randomize",
            "deleted",
        )
        list_serializer_class = AssessmentListSerializer
        # Use the contentnode and assessment_id as the lookup field for updates
        update_lookup_field = ("contentnode", "assessment_id")


# Apply mixin first to override ValuesViewset
class AssessmentItemViewSet(BulkCreateMixin, BulkUpdateMixin, ValuesViewset):
    queryset = AssessmentItem.objects.all()
    serializer_class = AssessmentItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filter_class = AssessmentItemFilter
    values = (
        "question",
        "type",
        "answers",
        "contentnode_id",
        "assessment_id",
        "hints",
        "raw_data",
        "order",
        "source_url",
        "randomize",
        "deleted",
    )

    field_map = {
        "contentnode": "contentnode_id",
    }

    def annotate_queryset(self, queryset):
        queryset = queryset.annotate(file_ids=NotNullArrayAgg("files__id"))
        return queryset
