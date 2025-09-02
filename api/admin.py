from django.contrib import admin

# API models are typically used for serialization and don't need
# admin registration as they usually don't have database models.
# The api app primarily contains serializers, views, and URL configurations.

# If you have any concrete models specific to the API, register them here.
# Example:
# @admin.register(YourAPIModel)
# class YourAPIModelAdmin(admin.ModelAdmin):
#     pass
