CREATE TABLE IF NOT EXISTS categories(
	cat_id INTEGER PRIMARY KEY,
	name TEXT
);

CREATE TABLE IF NOT EXISTS sources(
	source_id INTEGER PRIMARY KEY,
	name TEXT,
	url URL
);

CREATE TABLE IF NOT EXISTS tasks(
  id INTEGER PRIMARY KEY,
  title TEXT,
  description TEXT,
  state StateHolder,
  difficulty INTEGER,
  category INTEGER,
  source INTEGER,
  due DDate,
  created DDate,
  planned_sch TimeSpan,
  real_sch TimeSpan,
  FOREIGN KEY(source) REFERENCES sources(source_id),
  FOREIGN KEY(category) REFERENCES categories(cat_id)
);
