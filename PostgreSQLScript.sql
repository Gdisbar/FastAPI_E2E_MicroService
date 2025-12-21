DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id SERIAL,
  email varchar(200) DEFAULT NULL,
  username varchar(45) DEFAULT NULL,
  first_name varchar(45) DEFAULT NULL,
  last_name varchar(45) DEFAULT NULL,
  hashed_password varchar(200) DEFAULT NULL,
  is_active boolean DEFAULT NULL,
  role varchar(45) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

DROP TABLE IF EXISTS todos;

CREATE TABLE todos (
  id SERIAL,
  title varchar(200) DEFAULT NULL,
  description varchar(200) DEFAULT NULL,
  priority integer  DEFAULT NULL,
  complete boolean  DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  owner_id integer  DEFAULT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (owner_id) REFERENCES users(id)
);


-- Create a function to update the updated_at timestamp
-- CREATE OR REPLACE FUNCTION update_updated_at_column()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     NEW.updated_at = CURRENT_TIMESTAMP;
--     RETURN NEW;
-- END;
-- $$ language 'plpgsql';

-- -- Create a trigger that calls the function
-- CREATE TRIGGER update_users_updated_at 
-- BEFORE UPDATE ON users 
-- FOR EACH ROW 
-- EXECUTE FUNCTION update_updated_at_column();

SELECT * FROM users;
SELECT * FROM todos;
















