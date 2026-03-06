from django.urls import path

from . import views

app_name = "staffpanel"

urlpatterns = [
    path("login/", views.StaffLoginView.as_view(), name="login"),
    path("logout/", views.staff_logout, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("bot-content/", views.bot_content, name="bot_content"),
    path("bot-content/load-defaults/", views.bot_load_defaults, name="bot_load_defaults"),
    path("bot-content/new/", views.bot_entry_create, name="bot_entry_create"),
    path("bot-content/<int:entry_id>/edit/", views.bot_entry_edit, name="bot_entry_edit"),
    path("bot-content/<int:entry_id>/toggle/", views.bot_entry_toggle, name="bot_entry_toggle"),
    path("bot-content/<int:entry_id>/delete/", views.bot_entry_delete, name="bot_entry_delete"),
    path("collected/", views.collected, name="collected"),
    path("collected/<int:item_id>/add-to-intent/", views.collected_add_to_intent, name="collected_add_to_intent"),
    path("collected/<int:item_id>/add-new/", views.collected_mark_new, name="collected_mark_new"),
    path("collected/<int:item_id>/remove/", views.collected_remove, name="collected_remove"),
    path("reports/", views.reports, name="reports"),
    path("settings/", views.settings_page, name="settings"),
]
