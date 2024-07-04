#  pgvector base

A clean template for me to develope app based on pgvector and control its migration. 


# Setup



1. Create `db.py`: The following scripts define base, engine, and sessions which will be used in connecting to DB. 

    ```python
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.orm import declarative_base

    Base = declarative_base()

    # The url of a DB
    ASYNC_DB_URL = "postgresql+asyncpg://postgres:postgres@db/pqvector_db"


    # Create a engine to the DB
    async_engine = create_async_engine(ASYNC_DB_URL)
    async_session = sessionmaker(
        autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
    )


    # Session for the access to the DB
    async def get_db():
        async with async_session() as session:
            yield session

    ```


2. Create `models.py`: The following code defines table we want to migrate. 

    ```python

    from pgvector.sqlalchemy import Vector
    from sqlalchemy import Column, Integer, String
    from db import Base


    # Create a table Model which inherit from Base
    class AnkiNoteModel(Base):
        """Create a table based on the specified model as follows:"""

        __tablename__ = "vector_table_1"

        product_id = Column(Integer, primary_key=True)
        product_name = Column(String, nullable=False)
        description = Column(String, nullable=False)
        vector = Column(Vector(dim=1536))

    ```


3. Execute `alembic init migrations`. This will create a folder named `migrations` and a file called `alembic.ini` in the root directory. 

4. Edit `sqlalchemy.url` in `alembic.ini` like: 
    ```sh
    sqlalchemy.url = postgresql+asyncpg://postgres:postgres@db/pgvector_db
    ```



4. Modify `env.py`: 

    `env.py` serves as a template to produce the code for migration. However, when migrating the model defined in sqlalchemy to PostgreSQL, it lacks the definition of vector column which causes errors during the migration. As a result we have to add extra functions to fix it. 

    first of all, import the table definition as follows: 

    ```python
    target_metadata = Base.metadata
    ```

    Add the functions under it: 
    ```python
    def create_vector_extension(connection) -> None:
        try:
            with Session(connection) as session:  # type: ignore[arg-type]
                # The advisor lock fixes issue arising from concurrent
                # creation of the vector extension.
                # https://github.com/langchain-ai/langchain/issues/12933
                # For more information see:
                # https://www.postgresql.org/docs/16/explicit-locking.html#ADVISORY-LOCKS
                statement = sqlalchemy.text(
                    "BEGIN;" "CREATE EXTENSION IF NOT EXISTS vector;" "COMMIT;"
                )
                session.execute(statement)
                session.commit()
        except Exception as e:
            raise Exception(f"Failed to create vector extension: {e}") from e


    def do_run_migrations(connection) -> None:
        # Need to hack the "vector" type into postgres dialect schema types.
        # Otherwise, `alembic check` does not recognize the type

        # This line of code registers the custom vector type with SQLAlchemy so that SQLAlchemy knows how to
        # handle this custom type when interacting with the database schema.
        # It tells SQLAlchemy that the vector type in PostgreSQL should be mapped
        # to the pgvector.sqlalchemy.Vector type in Python.
        # ref: https://github.com/sqlalchemy/alembic/discussions/1324
        connection.dialect.ischema_names["vector"] = pgvector.sqlalchemy.Vector

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()
    ```

5. Build the docker container: Launch the db container after building.

    The `docker-compose.yaml` is as follows: 
    ```docker
    version: '3.8'
    services:
    db:
        image: ankane/pgvector
        environment:
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: postgres
        POSTGRES_DB: pgvector_db
        ports:
        - "5432:5432"
        volumes:
        - pgdata:/var/lib/postgresql/data
        deploy:
        resources:
            limits:
            cpus: '0.50'
            memory: '512M'
            reservations:
            cpus: '0.25'
            memory: '256M'
    volumes:
        pgdata:
    ```


    ```sh
    docker-compose up --build
    ```

6. Apply the migration: 





    ```sh
    docker-compose exec db psql -U postgres -d pgvector_db

    ```


