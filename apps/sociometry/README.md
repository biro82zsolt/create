# Sociometry app (HU/EN)

## Admin belépés beállítása (PyCharm)
Az admin belépés környezeti változókból jön:

- `SOCIOMETRY_ADMIN_EMAIL`
- `SOCIOMETRY_ADMIN_PASSWORD`

Ha ezek nincsenek megadva, az alapértékek:

- email: `admin@example.com`
- jelszó: `admin123`

### PyCharm lépések
1. **Run > Edit Configurations...**
2. Válaszd ki a Flask/Gunicorn konfigurációt.
3. Az **Environment variables** mezőbe add meg például:
   - `SOCIOMETRY_ADMIN_EMAIL=teadmin@email.hu`
   - `SOCIOMETRY_ADMIN_PASSWORD=Er0sJelszo!`
4. Mentsd és indítsd újra az appot.

## Nyelvváltás
A nyelvváltó az aktuális sociometry route-on marad (pl. `/sociometry/user/login?lang=en`).
