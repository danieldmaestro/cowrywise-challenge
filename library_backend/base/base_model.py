from django.db import models
from django.utils import timezone
from django.forms.models import model_to_dict


class ValidObjectsManager(models.Manager):
    def get_queryset(self):
        return super(ValidObjectsManager, self).get_queryset().filter(is_deleted=False)


class DeletedObjectsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=True)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    valid_objects = ValidObjectsManager()
    deleted_objects = DeletedObjectsManager()
    objects = ValidObjectsManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        super(BaseModel, self).save(*args, **kwargs)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def delete(self, **kwargs):
        self.soft_delete()

    def force_delete(self):
        """
        Only perform permanent deletion if the object is already soft-deleted
        """
        if self.is_deleted:
            super().delete()
        else:
            raise ValueError(
                "Object must be soft-deleted first before performing permanent delete.")

    def destroy(self):
        """
        Override soft delete and destroy
        """
        super().delete()

    def to_dict(self):
        """
        Returns a dictionary representation of the object
        """
        return model_to_dict(self)

    class Meta:
        ordering = ('-created_at',)
        abstract = True
        permissions = []



