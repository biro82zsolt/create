from flask import flash, redirect, url_for, request
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink

from .auth import is_admin

from .models import (
    db,
    Team,
    Player,
    Coach,
    AssessmentPeriod,
    Assessment,
)

class ProtectedAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(
            url_for("admin_login", next=request.path)
        )


class ProtectedModelView(ModelView):
    def is_accessible(self):
        return is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(
            url_for("admin_login", next=request.path)
        )


class TeamAdmin(ProtectedModelView):
    column_list = (
        "id",
        "name",
        "created_at",
    )

    column_searchable_list = (
        "name",
    )


class PlayerAdmin(ProtectedModelView):

    form_args = {
        "team": {
            "allow_blank": True,
        },
    }

    column_list = (
        "id",
        "player_code",
        "last_name",
        "first_name",
        "birth_date",
        "team",
        "roster_teams",
        "active",
    )

    column_searchable_list = (
        "player_code",
        "last_name",
        "first_name",
    )

    column_sortable_list = (
        "id",
        "player_code",
        "last_name",
        "first_name",
        "birth_date",
        ("team", "team.name"),
        "active",
    )

    column_filters = (
        "team",
        "roster_teams",
        "active",
    )

    column_labels = {
        "id": "ID",
        "player_code": "Játékoskód",
        "last_name": "Vezetéknév",
        "first_name": "Keresztnév",
        "birth_date": "Születési dátum",
        "team": "Elsődleges csapat",
        "roster_teams": "Csapatkapcsolatok",
        "active": "Aktív",
    }

    def delete_model(self, model):

        if model.assessments:

            flash(
                f"{model.full_name} nem törölhető, "
                f"mert {len(model.assessments)} értékeléssel rendelkezik. "
                f"Előbb inaktiváld vagy vond össze a rekordot.",
                "error",
            )

            return False

        try:

            self.session.delete(model)
            self.session.commit()

            flash(
                f"{model.full_name} sikeresen törölve.",
                "success",
            )

            return True

        except Exception as exc:

            self.session.rollback()

            flash(
                f"A játékos törlése sikertelen: {exc}",
                "error",
            )

            return False

    column_formatters = {
        "roster_teams": lambda view, context, model, name: (
            ", ".join(
                team.name
                for team in model.roster_teams
            )
        ),
    }

class CoachAdmin(ProtectedModelView):
    column_list = (
        "id",
        "name",
        "email",
        "created_at",
    )

    column_searchable_list = (
        "name",
        "email",
    )


class AssessmentPeriodAdmin(ProtectedModelView):
    column_list = (
        "id",
        "name",
        "start_date",
        "end_date",
        "created_at",
    )

    column_searchable_list = (
        "name",
    )


class AssessmentAdmin(ProtectedModelView):
    column_list = (
        "id",
        "player",
        "coach",
        "period",
        "completed_at",
    )

    column_filters = (
        "team",
        "coach",
        "period",
    )

    column_default_sort = (
        "completed_at",
        True,
    )
class ExcelImportView(BaseView):

    @expose("/", methods=("GET", "POST"))
    def index(self):

        if not is_admin():
            return redirect(
                url_for("admin_login", next=request.path)
            )

        if request.method == "GET":
            return self.render(
                "performance/admin_import.html"
            )

        uploaded = request.files.get("file")

        if not uploaded or not uploaded.filename:
            flash("Válassz ki egy Excel fájlt.", "error")
            return redirect(url_for(".index"))

        if not uploaded.filename.lower().endswith(".xlsx"):
            flash("Csak .xlsx fájl tölthető fel.", "error")
            return redirect(url_for(".index"))

        try:
            from .import_service import import_backup_excel

            result = import_backup_excel(uploaded)

            flash(
                f"Import kész. Új értékelések: {result['imported']}, "
                f"kihagyva: {result['skipped']}.",
                "success"
            )

        except Exception as exc:
            db.session.rollback()
            flash(f"Az import sikertelen: {exc}", "error")

        return redirect(url_for(".index"))


def init_admin(app):
    admin = Admin(
        app,
        name="Performance Admin",
        template_mode="bootstrap4",
        url="/performance/admin",
        index_view=ProtectedAdminIndexView(),
    )

    admin.add_link(
        MenuLink(
            name="Kijelentkezés",
            url="/performance/admin/logout",
        )
    )

    admin.add_link(
        MenuLink(
            name="Értékelések exportálása",
            url="/performance/admin/export/assessments",
        )
    )

    admin.add_link(
        MenuLink(
            name="Teljes biztonsági mentés",
            url="/performance/admin/export/backup",
        )
    )

    admin.add_view(
        TeamAdmin(
            Team,
            db.session,
            name="Teams",
            category="Performance",
        )
    )

    admin.add_view(
        PlayerAdmin(
            Player,
            db.session,
            name="Players",
            category="Performance",
        )
    )

    admin.add_view(
        CoachAdmin(
            Coach,
            db.session,
            name="Coaches",
            category="Performance",
        )
    )

    admin.add_view(
        AssessmentPeriodAdmin(
            AssessmentPeriod,
            db.session,
            name="Assessment Periods",
            category="Performance",
        )
    )

    admin.add_view(
        AssessmentAdmin(
            Assessment,
            db.session,
            name="Assessments",
            category="Performance",
        )
    )

    admin.add_view(
        ExcelImportView(
            name="Excel import",
            endpoint="excel_import",
            category="Performance"
        )
    )

    return admin