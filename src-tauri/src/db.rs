use rusqlite::{Connection, Result, params, types::Type};
use tauri::Manager;
use argon2::{
    password_hash::{
        rand_core::OsRng,
        PasswordHash, PasswordHasher, PasswordVerifier, SaltString
    },
    Argon2
};
use std::sync::{Arc, Mutex};
use serde::{Serialize, Deserialize};
use log::{info,error};

pub struct Database {
    conn: Arc<Mutex<Connection>>,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct ApiInfo {
    pub id: i64,
    pub profile_name: String,
    pub api_key: String,
    pub api_secret: String,
    pub api_url: String,
    pub port: u16,
    pub is_default: bool,
}

impl Database {
    pub fn new(app_handle: &tauri::AppHandle) -> Result<Self> {
        let app_dir = app_handle.path().app_local_data_dir().expect("Failed to get app local data dir");
        let db_path = app_dir.join("app.db");
        
        let conn = Connection::open(db_path)?;
        
        let db = Database { conn: Arc::new(Mutex::new(conn)) };
        db.initialize_tables()?;
        db.migrate_data()?;

        Ok(db)
    }

    fn initialize_tables(&self) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        
        conn.execute(
            "CREATE TABLE IF NOT EXISTS first_run (
                id INTEGER PRIMARY KEY,
                has_run BOOLEAN NOT NULL DEFAULT 0
            )",
            [],
        )?;

        conn.execute(
            "CREATE TABLE IF NOT EXISTS api_info (
                id INTEGER PRIMARY KEY,
                profile_name TEXT NOT NULL UNIQUE,
                api_key TEXT NOT NULL,
                api_secret TEXT NOT NULL,
                api_url TEXT NOT NULL,
                port INTEGER NOT NULL,
                is_default BOOLEAN NOT NULL DEFAULT 0
            )",
            [],
        )?;

        conn.execute(
            "CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY,
                password_hash TEXT NOT NULL
            )",
            [],
        )?;

        Ok(())
    }

    fn migrate_data(&self) -> Result<()> {
        let conn = self.conn.lock().unwrap();

        let table_exists: bool = conn.query_row(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='api_info'",
            [],
            |row| row.get(0),
        )?;

        if table_exists {
            let has_profile_name: bool = conn.query_row(
                "SELECT COUNT(*) FROM pragma_table_info('api_info') WHERE name='profile_name'",
                [],
                |row| row.get(0),
            )?;

            if !has_profile_name {
                conn.execute("ALTER TABLE api_info ADD COLUMN profile_name TEXT NOT NULL DEFAULT 'Default'", [])?;
            }

            let has_is_default: bool = conn.query_row(
                "SELECT COUNT(*) FROM pragma_table_info('api_info') WHERE name='is_default'",
                [],
                |row| row.get(0),
            )?;

            if !has_is_default {
                conn.execute("ALTER TABLE api_info ADD COLUMN is_default BOOLEAN NOT NULL DEFAULT 0", [])?;
                conn.execute("UPDATE api_info SET is_default = 1 WHERE id = (SELECT MIN(id) FROM api_info)", [])?;
            }

            let has_password_hash: bool = conn.query_row(
                "SELECT COUNT(*) FROM pragma_table_info('api_info') WHERE name='password_hash'",
                [],
                |row| row.get(0),
            )?;

            if has_password_hash {
                conn.execute(
                    "INSERT OR REPLACE INTO app_settings (id, password_hash)
                     SELECT 1, password_hash FROM api_info WHERE id = 1",
                    [],
                )?;

                conn.execute("ALTER TABLE api_info DROP COLUMN password_hash", [])?;
            }
        } else {
            conn.execute(
                "CREATE TABLE api_info (
                    id INTEGER PRIMARY KEY,
                    profile_name TEXT NOT NULL UNIQUE,
                    api_key TEXT NOT NULL,
                    api_secret TEXT NOT NULL,
                    api_url TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    is_default BOOLEAN NOT NULL DEFAULT 0
                )",
                [],
            )?;
        }

        Ok(())
    }

    pub fn is_first_run(&self) -> Result<bool> {
        let conn = self.conn.lock().unwrap();
        let count: i64 = conn.query_row("SELECT COUNT(*) FROM first_run", [], |row| row.get(0))?;
        Ok(count == 0)
    }

    pub fn set_has_run(&self) -> Result<()> {
        info!("Entering set_has_run");
        let conn = self.conn.lock().unwrap();
        match conn.execute("INSERT OR REPLACE INTO first_run (id, has_run) VALUES (1, 1)", []) {
            Ok(rows) => {
                info!("Inserted/Updated {} row(s) in first_run table", rows);
                Ok(())
            },
            Err(e) => {
                error!("Failed to insert/update first_run table: {}", e);
                Err(e)
            }
        }
    }
    pub fn save_api_info(&self, api_info: &ApiInfo) -> Result<()> {
        info!("Entering save_api_info for profile: {}", api_info.profile_name);
        let conn = self.conn.lock().unwrap();
        
        let is_first_profile: bool = conn.query_row(
            "SELECT COUNT(*) = 0 FROM api_info",
            [],
            |row| row.get(0)
        )?;
    
        info!("Is first profile: {}", is_first_profile);
    
        let (query, params) = if is_first_profile {
            (
                "INSERT INTO api_info (profile_name, api_key, api_secret, api_url, port, is_default) 
                 VALUES (?1, ?2, ?3, ?4, ?5, 1)",
                params![api_info.profile_name, api_info.api_key, api_info.api_secret, api_info.api_url, api_info.port]
            )
        } else {
            (
                "INSERT OR REPLACE INTO api_info (profile_name, api_key, api_secret, api_url, port, is_default) 
                 VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
                params![api_info.profile_name, api_info.api_key, api_info.api_secret, api_info.api_url, api_info.port, api_info.is_default]
            )
        };
    
        info!("Executing {} query", if is_first_profile { "INSERT" } else { "INSERT OR REPLACE" });
        match conn.execute(query, params) {
            Ok(rows) => info!("Inserted/Updated {} row(s)", rows),
            Err(e) => {
                error!("Failed to execute query: {}", e);
                return Err(e.into());
            }
        }
    
        info!("save_api_info completed successfully");
        Ok(())
    }
    
    pub fn set_default_profile(&self, profile_name: &str) -> Result<()> {
        info!("Entering set_default_profile for profile: {}", profile_name);
        let mut conn = self.conn.lock().unwrap();
    
        let tx = conn.transaction()?;
    
        info!("Resetting all profiles to non-default");
        tx.execute("UPDATE api_info SET is_default = 0", [])?;
    
        info!("Setting new default profile");
        let rows_affected = tx.execute(
            "UPDATE api_info SET is_default = 1 WHERE profile_name = ?1",
            params![profile_name],
        )?;
    
        if rows_affected == 0 {
            tx.rollback()?;
            return Err(rusqlite::Error::QueryReturnedNoRows.into());
        }
    
        tx.commit()?;
    
        info!("set_default_profile completed successfully");
        Ok(())
    }

    pub fn get_api_info(&self, profile_name: Option<&str>) -> Result<Option<ApiInfo>> {
        let conn = self.conn.lock().unwrap();
        let query = match profile_name {
            Some(_name) => "SELECT id, profile_name, api_key, api_secret, api_url, port, is_default FROM api_info WHERE profile_name = ?1",
            None => "SELECT id, profile_name, api_key, api_secret, api_url, port, is_default FROM api_info WHERE is_default = 1",
        };

        let mut stmt = conn.prepare(query)?;
        let api_info = if let Some(name) = profile_name {
            stmt.query_row(params![name], |row| self.row_to_api_info(row))
        } else {
            stmt.query_row([], |row| self.row_to_api_info(row))
        };

        match api_info {
            Ok(info) => Ok(Some(info)),
            Err(rusqlite::Error::QueryReturnedNoRows) => Ok(None),
            Err(e) => Err(e),
        }
    }

    pub fn get_default_api_info(&self) -> Result<Option<ApiInfo>> {
        self.get_api_info(None)
    }

    fn row_to_api_info(&self, row: &rusqlite::Row) -> rusqlite::Result<ApiInfo> {
        Ok(ApiInfo {
            id: row.get(0)?,
            profile_name: row.get(1)?,
            api_key: row.get(2)?,
            api_secret: row.get(3)?,
            api_url: row.get(4)?,
            port: row.get(5)?,
            is_default: row.get(6)?,
        })
    }

    pub fn list_api_profiles(&self) -> Result<Vec<ApiInfo>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare("SELECT id, profile_name, api_key, api_secret, api_url, port, is_default FROM api_info ORDER BY profile_name")?;
        let profiles = stmt.query_map([], |row| self.row_to_api_info(row))?
            .collect::<Result<Vec<ApiInfo>, _>>()?;
        Ok(profiles)
    }

    pub fn delete_api_profile(&self, profile_name: &str) -> Result<()> {
        let mut conn = self.conn.lock().unwrap();
        let tx = conn.transaction()?;
    
        tx.execute("DELETE FROM api_info WHERE profile_name = ?1", params![profile_name])?;
        
        // Check if the deleted profile was the default
        let was_default: bool = tx.query_row(
            "SELECT COUNT(*) = 0 FROM api_info WHERE is_default = 1",
            [],
            |row| row.get(0)
        )?;
    
        if was_default {
            // Set a new default profile
            tx.execute(
                "UPDATE api_info SET is_default = 1 WHERE id = (SELECT MIN(id) FROM api_info)",
                [],
            )?;
        }
    
        tx.commit()?;
        Ok(())
    }

    fn ensure_default_profile(&self) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        let default_exists: bool = conn.query_row("SELECT EXISTS(SELECT 1 FROM api_info WHERE is_default = 1)", [], |row| row.get(0))?;
        
        if !default_exists {
            conn.execute("UPDATE api_info SET is_default = 1 WHERE id = (SELECT MIN(id) FROM api_info)", [])?;
        }
        
        Ok(())
    }

    pub fn hash_password(password: &str) -> Result<String, argon2::password_hash::Error> {
        let salt = SaltString::generate(&mut OsRng);
        let argon2 = Argon2::default();
        let password_hash = argon2.hash_password(password.as_bytes(), &salt)?.to_string();
        Ok(password_hash)
    }

    pub fn verify_password(hash: &str, password: &str) -> Result<bool, argon2::password_hash::Error> {
        let parsed_hash = PasswordHash::new(hash)?;
        Ok(Argon2::default().verify_password(password.as_bytes(), &parsed_hash).is_ok())
    }

    pub fn verify_pin(&self, pin: &str) -> Result<bool> {
        let conn = self.conn.lock().unwrap();
        let password_hash: String = conn.query_row(
            "SELECT password_hash FROM app_settings WHERE id = 1",
            [],
            |row| row.get(0)
        )?;

        Self::verify_password(&password_hash, pin)
            .map_err(|e| rusqlite::Error::FromSqlConversionFailure(
                0,
                Type::Text,
                Box::new(std::io::Error::new(std::io::ErrorKind::Other, e.to_string()))
            ))
    }

    pub fn update_password_hash(&self, new_hash: &str) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "INSERT OR REPLACE INTO app_settings (id, password_hash) VALUES (1, ?1)",
            params![new_hash],
        )?;
        Ok(())
    }
}