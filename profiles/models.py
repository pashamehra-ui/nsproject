from django.db import models

class Friendship(models.Model):
    """
    A directed edge (from_ens -> to_ens) representing a 'friend' relation.
    For undirected semantics, we can enforce ordering later; for now we store exactly what the user adds.
    """
    from_ens = models.CharField(max_length=255, db_index=True)
    to_ens   = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["from_ens", "to_ens"], name="unique_friendship")
        ]

    def __str__(self):
        return f"{self.from_ens} -> {self.to_ens}"
