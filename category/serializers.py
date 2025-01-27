from rest_framework import serializers
from .models import Category
from user.models import CustomUser
from rest_framework.exceptions import NotFound


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "is_default", "user", "is_deleted")
        extra_kwargs = {
            "is_default": {"read_only": True},
            "is_deleted": {"read_only": True},
        }

    def get_category(self, id, user):
        """Helper method to fetch a category by ID, ensuring user permissions."""
        try:
            if user.is_staff:
                return Category.objects.get(id=id, is_deleted=False)
            return Category.objects.get(id=id, user=user, is_deleted=False)
        except Category.DoesNotExist:
            raise NotFound("Category not found.")

    def validate_user(self, value):
        """Validate that the user field is valid and can only be set by staff users during creation."""
        request = self.context.get("request")
        if not request.user.is_staff:
            raise serializers.ValidationError("Only staff users can set the user field.")
        if not value:
            raise serializers.ValidationError("The user field cannot be blank.")
        return value

    def validate_name(self, value):
        """Validate that the category name is unique for the determined user."""
        request = self.context.get("request")
        user = None

        if request.user.is_staff:
            # Staff user can specify a different user or default to their own ID
            user_id = self.initial_data.get("user")
            if user_id:
                try:
                    user = CustomUser.objects.get(id=user_id)
                except CustomUser.DoesNotExist:
                    raise serializers.ValidationError("The specified user does not exist.")
            else:
                # Default to the staff user's own ID
                user = request.user
        else:
            # For non-staff users, use their own ID
            user = request.user
            print(user)

        # Check if a category with the same name exists for the determined user
        if Category.objects.filter(name__iexact=value, user=user, is_deleted=False).exists() | Category.objects.filter(name__iexact=value,  is_deleted=False, is_default=True).exists():
            raise serializers.ValidationError(
                f"A category with the name '{value}' already exists for the user or predifined."
            )

        # Save the determined user in the serializer context for later use
        # self.context["determined_user"] = user

        return value



    def validate(self, data):
        """Ensure the user field is handled correctly during creation and updates."""
        request = self.context.get("request")
        user = request.user

        # For creation
        if self.instance is None:
            # If the user is not staff, force the user field to be the authenticated user
            if not user.is_staff:
                data["user"] = user
                data["is_default"] = False  # Normal users cannot create default categories

            # If the user is staff
            if user.is_staff:
                # If no user is provided, default to the authenticated user and set is_default=True
                if "user" not in data:
                    data["user"] = user
                    data["is_default"] = True
                # If a user is provided, set is_default=False
                else:
                    data["is_default"] = False

        # For updates
        else:
            # Prevent staff users from updating the user field
            if "user" in data:
                raise serializers.ValidationError("The user field cannot be updated.")

        return data

    def create(self, validated_data):
        """Ensure the user and is_default fields are always set correctly before creating the category."""
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Ensure the user field is not updated and other fields are updated correctly."""
        return super().update(instance, validated_data)