## How to Deal with Our Setup in 5 Steps 

1. Go to neon.com  
2. Setup an account and create a new project.
3. Get the connection string and update your `.env` file with it. You will find an example in the `.env.example` file in the root directory  
   - **Important note:** we built an **async engine**, so make sure to change  
     `postgresql://` → `postgresql+asyncpg://` in your connection string for the app.
4. Inside the SQL console of Neon run:

   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
    ```

to enable the `vector` extension.

5. Run the Alembic migrations (so your tables actually exist):

   * We use **ONLY ONE MAGICAL URL AS ITS IN .ENV.EXAMPLE**:

     * `DATABASE_URL` → used by the app (FastAPI, async SQLAlchemy)
       Example:
       `postgresql+asyncpg://user:pass@host/db`
     

   * In your `.env`:

     ```env
     DATABASE_URL=postgresql+asyncpg://user:pass@host/db
     
     ```

   * In `app/core/db.py` we use `DATABASE_URL` to build the async engine via the .env for sure.

 

   * In `app/db/migrations/env.py` make sure Alembic sees our models:

     ```python
     from kalamna.db.base import Base
     from kalamna.apps.auth.models import Business  # and any other models, so they are imported

     target_metadata = Base.metadata
     ```

   * Now, from the project root, generate and run migrations:

     ```bash
     # 1) create migration file based on current models
     alembic revision --autogenerate -m "init db"

     # 2) apply it to Neon (this actually creates the tables)
     alembic upgrade head
     ```

   * Any time you change or add models:

     ```bash
     alembic revision --autogenerate -m "describe your change"
     alembic upgrade head
     ```

