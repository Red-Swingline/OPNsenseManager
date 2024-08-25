use tauri::State;
use crate::db::{Database, ApiInfo};
use crate::http_client::make_http_request;


#[tauri::command]
pub async fn get_vendor_info(mac: String) -> Result<String, String> {
    let formatted_mac = mac.replace(":", "-");
    let url = format!("https://api.macvendors.com/{}", formatted_mac);

    match make_http_request("GET", &url, None, None, Some(30), None, None).await {
        Ok(response) => {
            if response.status().is_success() {
                Ok(response.text().await.unwrap_or_else(|_| "Unknown".to_string()))
            } else if response.status().as_u16() == 404 {
                Ok("Unknown".to_string())
            } else {
                Err(format!("Failed to get vendor info: {}", response.status()))
            }
        },
        Err(e) => Err(format!("Failed to get vendor info: {}", e))
    }
}

#[tauri::command]
pub fn check_first_run(database: State<Database>) -> Result<bool, String> {
    database.is_first_run()
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn save_initial_config(
    api_key: String,
    api_secret: String,
    api_url: String,
    port: u16,
    pin: String,
    database: State<Database>
) -> Result<(), String> {
    // Hash the PIN
    let password_hash = Database::hash_password(&pin)
        .map_err(|e| e.to_string())?;

    let api_info = ApiInfo {
        api_key,
        api_secret,
        api_url,
        port,
        password_hash,
    };

    database.save_api_info(&api_info)
        .map_err(|e| e.to_string())?;

    // Set that the app has run for the first time
    database.set_has_run()
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn verify_pin(pin: String, database: State<Database>) -> Result<bool, String> {
    database.verify_pin(&pin)
        .map_err(|e| format!("Failed to verify PIN: {}", e))
}

#[tauri::command]
pub fn get_api_info(database: State<Database>) -> Result<Option<ApiInfo>, String> {
    database.get_api_info()
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn update_api_info(
    api_key: String,
    api_secret: String,
    api_url: String,
    port: u16,
    database: State<Database>
) -> Result<(), String> {
    let mut api_info = database.get_api_info()
        .map_err(|e| e.to_string())?
        .ok_or_else(|| "API info not found".to_string())?;

    api_info.api_key = api_key;
    api_info.api_secret = api_secret;
    api_info.api_url = api_url;
    api_info.port = port;

    database.save_api_info(&api_info)
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn update_pin(current_pin: String, new_pin: String, confirm_new_pin: String, database: State<Database>) -> Result<(), String> {
    // Verify the current PIN
    if !database.verify_pin(&current_pin)
        .map_err(|e| format!("Failed to verify current PIN: {}", e))? {
        return Err("Current PIN is incorrect".to_string());
    }

    // Check if new PIN matches the confirmation
    if new_pin != confirm_new_pin {
        return Err("New PIN and confirmation do not match".to_string());
    }

    // Hash the new PIN
    let password_hash = Database::hash_password(&new_pin)
        .map_err(|e| e.to_string())?;

    database.update_password_hash(&password_hash)
        .map_err(|e| e.to_string())
}