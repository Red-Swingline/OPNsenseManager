use tauri::State;
use serde_json::Value;
use crate::db::Database;
use crate::http_client::make_http_request;

fn build_api_url(api_info: &crate::db::ApiInfo, endpoint: &str) -> String {
    format!("{}:{}{}", api_info.api_url, api_info.port, endpoint)
}

#[tauri::command]
pub async fn get_devices(database: State<'_, Database>) -> Result<Value, String> {
    let api_info = database.get_api_info()
        .map_err(|e| format!("Failed to get API info: {}", e))?
        .ok_or_else(|| "API info not found".to_string())?;

    let url = build_api_url(&api_info, "/api/diagnostics/interface/getArp");

    let response = make_http_request(
        "GET",
        &url,
        None,
        None,
        Some(30),
        Some(&api_info.api_key),
        Some(&api_info.api_secret),
    )
    .await?;

    response.json::<Value>().await
        .map_err(|e| format!("Failed to parse response: {}", e))
}

#[tauri::command]
pub async fn flush_arp_table(database: State<'_, Database>) -> Result<Value, String> {
    let api_info = database.get_api_info()
        .map_err(|e| format!("Failed to get API info: {}", e))?
        .ok_or_else(|| "API info not found".to_string())?;

    let url = build_api_url(&api_info, "/api/diagnostics/interface/flushArp");

    let response = make_http_request(
        "POST",
        &url,
        None,
        None,
        Some(30),
        Some(&api_info.api_key),
        Some(&api_info.api_secret),
    )
    .await?;

    response.json::<Value>().await
        .map_err(|e| format!("Failed to parse response: {}", e))
}