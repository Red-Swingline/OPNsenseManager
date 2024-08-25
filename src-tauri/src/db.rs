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

pub struct Database {
    conn: Arc<Mutex<Connection>>,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct ApiInfo {
    pub api_key: String,
    pub api_secret: String,
    pub api_url: String,
    pub port: u16,
    pub password_hash: String,
}

impl Database {
    pub fn new(app_handle: &tauri::AppHandle) -> Result<Self> {
        let app_dir = app_handle.path().app_local_data_dir().expect("Failed to get app local data dir");
        let db_path = app_dir.join("app.db");
        
        let conn = Connection::open(db_path)?;
        
        // Create the first_run table if it doesn't exist
        conn.execute(
            "CREATE TABLE IF NOT EXISTS first_run (
                id INTEGER PRIMARY KEY,
                has_run BOOLEAN NOT NULL DEFAULT 0
            )",
            [],
        )?;

        // Create the api_info table if it doesn't exist
        conn.execute(
            "CREATE TABLE IF NOT EXISTS api_info (
                id INTEGER PRIMARY KEY,
                api_key TEXT NOT NULL,
                api_secret TEXT NOT NULL,
                api_url TEXT NOT NULL,
                port INTEGER NOT NULL,
                password_hash TEXT NOT NULL
            )",
            [],
        )?;

        Ok(Database { conn: Arc::new(Mutex::new(conn)) })
    }

    pub fn is_first_run(&self) -> Result<bool> {
        let conn = self.conn.lock().unwrap();
        let count: i64 = conn.query_row("SELECT COUNT(*) FROM first_run", [], |row| row.get(0))?;
        Ok(count == 0)
    }

    pub fn set_has_run(&self) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute("INSERT INTO first_run (has_run) VALUES (1)", [])?;
        Ok(())
    }

    pub fn save_api_info(&self, api_info: &ApiInfo) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "INSERT OR REPLACE INTO api_info (id, api_key, api_secret, api_url, port, password_hash) 
             VALUES (1, ?1, ?2, ?3, ?4, ?5)",
            params![api_info.api_key, api_info.api_secret, api_info.api_url, api_info.port, api_info.password_hash],
        )?;
        Ok(())
    }

    pub fn get_api_info(&self) -> Result<Option<ApiInfo>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare("SELECT api_key, api_secret, api_url, port, password_hash FROM api_info WHERE id = 1")?;
        let api_info = stmt.query_row([], |row| {
            Ok(ApiInfo {
                api_key: row.get(0)?,
                api_secret: row.get(1)?,
                api_url: row.get(2)?,
                port: row.get(3)?,
                password_hash: row.get(4)?,
            })
        });

        match api_info {
            Ok(info) => Ok(Some(info)),
            Err(rusqlite::Error::QueryReturnedNoRows) => Ok(None),
            Err(e) => Err(e),
        }
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
            "SELECT password_hash FROM api_info WHERE id = 1",
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
            "UPDATE api_info SET password_hash = ?1 WHERE id = 1",
            params![new_hash],
        )?;
        Ok(())
    }
}