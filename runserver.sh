uwsgi -s ./backend/backend.sock --manage-script-name --mount /api=backend:app --virtualenv ../.env --plugin python3
