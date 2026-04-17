# ⛰️ TrailShare — GPX Sharing Platform

A Django web app for uploading, visualising, and sharing GPX tracks in groups.
Styled with **Bootstrap 5.3** (dark theme). Maps powered by **gpx.studio** embed.

---

## Quick Start

```bash
# 1. Create & activate venv
python3 -m venv venv
source venv/bin/activate       # Linux / Mac
venv\Scripts\activate          # Windows

# 2. Install
pip install -r requirements.txt

# 3. Migrate
python manage.py migrate

# 4. (Optional) create admin user
python manage.py createsuperuser

# 5. Run
python manage.py runserver
```

Visit **http://127.0.0.1:8000**

---

## Features

| Feature | Details |
|---|---|
| Auth | Register · Login · Logout |
| Groups | Create public/private groups with colour themes |
| Invite links | Unique UUID link per group; creator can reset/revoke |
| GPX upload | Drag & drop; auto-parsed distance, elevation, duration |
| Map viewer | gpx.studio iframe embed (`/embed?options=…`) |
| Explore | Search all public groups |
| Dashboard | Your groups + recent activity feed |

---

## gpx.studio Embed

The URL is built server-side in `tracks/views.py`:

```python
options = json.dumps({"files": [file_url], "basemap": "openStreetMap"})
gpxstudio_url = f"https://gpx.studio/embed?options={urllib.parse.quote(options)}"
```

gpx.studio fetches the GPX file by URL, so **the server must be publicly reachable**.

For local development, tunnel with:

```bash
pip install ngrok
ngrok http 8000
# Use the https://xxxx.ngrok-free.app URL as your Django ALLOWED_HOSTS / SERVER
```

Or set `USE_X_FORWARDED_HOST = True` and run behind a reverse proxy.

---

## Invite Links (Private Groups)

- Every `Group` has an `invite_token` UUID field (auto-generated, unique).
- The invite URL is: `https://yoursite.com/invite/<uuid>/`
- Visiting the link adds the logged-in user to the group.
- If not logged in, they are redirected to login and then back to the invite URL.
- **Group creator** can click **Reset** in the group sidebar to generate a new token — the old link immediately stops working.

---

## Project Structure

```
gpxshare/
├── accounts/            # register · login · logout
├── tracks/              # groups · tracks · maps · invites
│   └── migrations/      # includes invite_token field
├── templates/
│   ├── base.html        # Bootstrap 5.3 dark navbar + alerts
│   ├── accounts/        # login.html · register.html
│   └── tracks/          # home · dashboard · explore
│                          group_detail · create_group
│                          upload_track · track_detail
│                          confirm_delete
├── static/
├── media/               # uploaded GPX files
├── manage.py
└── requirements.txt
```

---

## Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Set a strong `SECRET_KEY`
- [ ] Add your domain to `ALLOWED_HOSTS`
- [ ] Switch to PostgreSQL (`psycopg2`)
- [ ] Store media on S3 (`django-storages`)
- [ ] Run `python manage.py collectstatic`
- [ ] Serve behind nginx + gunicorn
