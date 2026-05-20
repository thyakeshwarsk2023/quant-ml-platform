from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE metrics ADD COLUMN IF NOT EXISTS ml_score FLOAT DEFAULT 0"))
    conn.commit()
    result = conn.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='metrics' ORDER BY ordinal_position"
    ))
    cols = [r[0] for r in result]
    print("Columns in metrics table:", cols)
    if "ml_score" in cols:
        print("SUCCESS: ml_score column exists")
    else:
        print("FAILED: ml_score column still missing")
