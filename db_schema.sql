CREATE TABLE IF NOT EXISTS "categories"(
	"cat_id" INTEGER PRIMARY KEY,
	"name" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "sources"(
	"source_id" INTEGER PRIMARY KEY,
	"name" TEXT NOT NULL,
	"url" URL
);

CREATE TABLE IF NOT EXISTS "tasks"(
  "task_id" INTEGER PRIMARY KEY,
  "title" TEXT NOT NULL,
  "description" TEXT NOT NULL,
  "state" StateHolder NOT NULL,
  "difficulty" INTEGER NOT NULL,
  "category" INTEGER,
  "source" INTEGER,
  "due" DDate,
  "created" DDate NOT NULL,
  "planned_sch" TimeSpan,
  "real_sch" TimeSpan,
  FOREIGN KEY("source") REFERENCES "sources"("source_id") ON DELETE SET NULL,
  FOREIGN KEY("category") REFERENCES "categories"("cat_id") ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS "appointments"(
    "apmt_id" INTEGER PRIMARY KEY NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT,
    "schedule" TimeSpan NOT NULL,
    "created" DDate NOT NULL
);


CREATE TABLE IF NOT EXISTS "task_cache"(
  "cache_id" INTEGER PRIMARY KEY,
  "task_id" INTEGER NOT NULL,
  FOREIGN KEY("task_id") REFERENCES "tasks"("task_id") ON DELETE CASCADE
);
