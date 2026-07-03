from database import engine, Base
import models

print("Crestinng structures in MariaDB...")
Base.metadata.create_all(bind=engine)
print("Tables created succesfuly")