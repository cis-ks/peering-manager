import uuid

from django.contrib.auth.models import User

from utils.constants import OBJECT_CHANGE_ACTION_UPDATE
from utils.models import ObjectChange, Tag
from utils.testing import StandardTestCases


class ObjectChangeTestCase(StandardTestCases.Views):
    model = ObjectChange

    test_create_object = None
    test_edit_object = None
    test_delete_object = None
    test_bulk_edit_objects = None
    test_bulk_delete_objects = None

    @classmethod
    def setUpTestData(cls):
        tag = Tag(name="Tag 1", slug="tag-1")
        tag.save()

        user = User.objects.create_user(username="testuser2")
        for i in range(1, 4):
            tag.log_change(user, uuid.uuid4(), OBJECT_CHANGE_ACTION_UPDATE)


class TagTestCase(StandardTestCases.Views):
    model = Tag

    @classmethod
    def setUpTestData(cls):
        Tag.objects.bulk_create(
            (
                Tag(name="Tag 1", slug="tag-1"),
                Tag(name="Tag 2", slug="tag-2"),
                Tag(name="Tag 3", slug="tag-3"),
            )
        )

        cls.form_data = {
            "name": "Tag 4",
            "slug": "tag-4",
            "color": "c0c0c0",
            "comments": "Some comments",
        }

        cls.bulk_edit_data = {"color": "00ff00"}
