# database for dummies
## How to Deal with Our Setup in 4 Steps 
1. Go to neon.com  
2. Setup account and create a new project
3. get the connection string and update your .env file with it. You will find an example in the .env.example file in the root directory
   - " important note: we built an async engine so make sure to change 'postgresql://' to 'postgresql+asyncpg://' in your connection string"
4. Inside the console of neon run 'CREATE EXTENSION IF NOT EXISTS vector;' to enable vector extension
