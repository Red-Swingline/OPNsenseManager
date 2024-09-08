use serde::{Deserialize, Serialize};
use tauri::State;
use crate::db::Database;
use crate::http_client::make_http_request;
use std::time::Duration;
use tokio::time::sleep;

#[derive(Serialize, Deserialize, Debug)]
pub struct UpdateStatus {
    status: String,
    log: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct FirmwareStatus {
    api_version: String,
    connection: String,
    download_size: String,
    last_check: String,
    needs_reboot: String,
    os_version: String,
    product_id: String,
    product_target: String,
    product_version: String,
    product_abi: String,
    repository: String,
    upgrade_major_message: String,
    upgrade_major_version: String,
    upgrade_needs_reboot: String,
    product: ProductInfo,
    status_msg: String,
    status: String,
    #[serde(default)]
    downgrade_packages: Vec<String>,
    #[serde(default)]
    new_packages: Vec<String>,
    #[serde(default)]
    reinstall_packages: Vec<String>,
    #[serde(default)]
    remove_packages: Vec<String>,
    #[serde(default)]
    upgrade_packages: Vec<String>,
    #[serde(default)]
    upgrade_sets: Vec<String>,
    #[serde(default)]
    all_packages: Vec<String>,
    #[serde(default)]
    all_sets: Vec<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ProductInfo {
    product_abi: String,
    product_arch: String,
    product_copyright_owner: String,
    product_copyright_url: String,
    product_copyright_years: String,
    product_email: String,
    product_hash: String,
    product_id: String,
    product_latest: String,
    product_name: String,
    product_nickname: String,
    product_repos: String,
    product_series: String,
    product_tier: String,
    product_time: String,
    product_version: String,
    product_website: String,
    #[serde(default)]
    product_license: Vec<String>,
    product_log: u8,
    product_mirror: String,
}

fn build_api_url(api_info: &crate::db::ApiInfo, endpoint: &str) -> String {
    format!("{}:{}{}", api_info.api_url, api_info.port, endpoint)
}

#[tauri::command]
pub async fn check_for_updates(database: State<'_, Database>) -> Result<FirmwareStatus, String> {
    let api_info = database.get_default_api_info()
        .map_err(|e| format!("Failed to get API info: {}", e))?
        .ok_or_else(|| "API info not found".to_string())?;

    // Initiate the update check
    let check_url = build_api_url(&api_info, "/api/core/firmware/check");
    let _ = make_http_request(
        "POST",
        &check_url,
        Some(serde_json::json!({})),
        None,
        Some(30),
        Some(&api_info.api_key),
        Some(&api_info.api_secret),
    )
    .await?;

    // Poll for status
    let status_url = build_api_url(&api_info, "/api/core/firmware/upgradestatus");
    loop {
        let response = make_http_request(
            "GET",
            &status_url,
            None,
            None,
            Some(30),
            Some(&api_info.api_key),
            Some(&api_info.api_secret),
        )
        .await?;

        let update_status: UpdateStatus = response.json().await
            .map_err(|e| format!("Failed to parse update status: {}", e))?;

        if update_status.status == "done" {
            break;
        }

        sleep(Duration::from_secs(2)).await;
    }

    // Get final firmware status
    let firmware_status_url = build_api_url(&api_info, "/api/core/firmware/status");
    let response = make_http_request(
        "GET",
        &firmware_status_url,
        None,
        None,
        Some(30),
        Some(&api_info.api_key),
        Some(&api_info.api_secret),
    )
    .await?;

    response.json::<FirmwareStatus>().await
        .map_err(|e| format!("Failed to parse firmware status: {}", e))
}

#[tauri::command]
pub async fn get_current_firmware_status(database: State<'_, Database>) -> Result<FirmwareStatus, String> {
    let api_info = database.get_default_api_info()
        .map_err(|e| format!("Failed to get API info: {}", e))?
        .ok_or_else(|| "API info not found".to_string())?;

    let firmware_status_url = build_api_url(&api_info, "/api/core/firmware/status");
    let response = make_http_request(
        "GET",
        &firmware_status_url,
        None,
        None,
        Some(30),
        Some(&api_info.api_key),
        Some(&api_info.api_secret),
    )
    .await?;

    response.json::<FirmwareStatus>().await
        .map_err(|e| format!("Failed to parse firmware status: {}", e))
}