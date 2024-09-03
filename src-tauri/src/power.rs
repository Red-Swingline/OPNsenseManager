use tauri::State;
use serde::{Serialize, Deserialize};
use crate::db::Database;
use crate::http_client::make_http_request;

#[derive(Serialize, Deserialize, Debug)]
pub struct RebootResponse {
    status: String,
}

fn build_api_url(api_info: &crate::db::ApiInfo, endpoint: &str) -> String {
    format!("{}:{}{}", api_info.api_url, api_info.port, endpoint)
}

#[tauri::command]
pub async fn reboot_firewall(database: State<'_, Database>) -> Result<RebootResponse, String> {
    let api_info = database.get_default_api_info()
        .map_err(|e| format!("Failed to get API info: {}", e))?
        .ok_or_else(|| "API info not found".to_string())?;

    let url = build_api_url(&api_info, "/api/core/system/reboot");

    let response = make_http_request(
        "POST",
        &url,
        Some(serde_json::json!({})),
        None,
        Some(30),
        Some(&api_info.api_key),
        Some(&api_info.api_secret),
    )
    .await?;

    response.json::<RebootResponse>().await
        .map_err(|e| format!("Failed to parse response: {}", e))
}