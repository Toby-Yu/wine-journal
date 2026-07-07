from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE journal_entry ADD COLUMN tasting_notes TEXT"))
            conn.commit()
        print("✅ tasting_notes column added successfully.")
    except Exception as e:
        # If column already exists, ignore error
        if "duplicate column name" in str(e).lower():
            print("Column already exists, nothing to do.")
        else:
            print(f"Error: {e}")