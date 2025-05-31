from rest_framework import serializers
from .models import CustomUser, Position, PartyList, Election
from PIL import Image
import io

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    photo_url = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = ('student_id', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'photo_url')

    def validate_photo_url(self, value):
        if value:
            if value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError("Image size should not exceed 2MB.")
            if value.content_type not in ['image/jpeg', 'image/png', 'image/webp']:
                raise serializers.ValidationError("Only JPEG, PNG, and WebP images are allowed.")
            # Optional: Crop to 1:1 aspect ratio
            try:
                img = Image.open(value)
                min_side = min(img.size)
                left = (img.width - min_side) // 2
                top = (img.height - min_side) // 2
                right = left + min_side
                bottom = top + min_side
                img = img.crop((left, top, right, bottom))
                # Save cropped image back to InMemoryUploadedFile
                img_io = io.BytesIO()
                img_format = img.format if img.format else 'PNG'
                img.save(img_io, format=img_format)
                value.file = img_io
                value.size = img_io.tell()
                img_io.seek(0)
            except Exception as exc:
                raise serializers.ValidationError("Invalid image file.") from exc
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        photo = validated_data.pop('photo_url', None)
        user = CustomUser.objects.create_user(
            student_id=validated_data['student_id'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data['student_id'],
        )
        if photo:
            user.photo_url = photo
            user.save()
        return user

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

class PartyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartyList
        fields = '__all__'

class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = '__all__'
