use tauri::State;
use serde_json::Value;
use crate::db::Database;
use crate::http_client::make_http_request;
use serde_json::json;

fn build_api_url(api_info: &crate::db::ApiInfo, endpoint: &str) -> String {
    format!("{}:{}{}", api_info.api_url, api_info.port, endpoint)
}

#[tauri::command]
pub async fn list_network_aliases(database: State<'_, Database>) -> Result<Value, String> {
    let api_info = database.get_default_api_info()
        .map_err(|e| format!("Failed to get API info: {}", e))?
        .ok_or_else(|| "API info not found".to_string())?;

    let url = build_api_url(&api_info, "/api/firewall/alias/listNetworkAliases");

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
pub async fn get_alias(database: State<'_, Database>, alias_name: String) -> Result<Value, String> {
    let aliases = list_network_aliases(database).await?;
    
    let alias = aliases.as_object()
        .and_then(|obj| obj.get(&alias_name))
        .ok_or_else(|| format!("Alias '{}' not found", alias_name))?;

    Ok(alias.clone())
}

#[tauri::command]
pub async fn add_ip_to_alias(database: State<'_, Database>, uuid: String, current_content: String, new_ip: String) -> Result<(), String> {
    let api_info = database.get_default_api_info()
        .map_err(|e| format!("Failed to get API info: {}", e))?
        .ok_or_else(|| "API info not found".to_string())?;

    let url = build_api_url(&api_info, &format!("/api/firewall/alias/setItem/{}", uuid));

    // Combine current content with new IP
    let updated_content = if current_content.is_empty() {
        new_ip
    } else {
        format!("{}\n{}", current_content.replace(",", "\n"), new_ip)
    };

    // Get the alias name
    let alias_info = get_alias_info(&api_info, &uuid).await?;
    let alias_name = alias_info["alias"]["name"].as_str().unwrap_or("");

    let payload = json!({
        "alias": {
            "name": alias_name,
            "content": updated_content,
        }
    });

    let response = make_http_request(
        "POST",
        &url,
        Some(payload),
        None,
        Some(30),
        Some(&api_info.api_key),
        Some(&api_info.api_secret),
    )
    .await?;

    if response.status().is_success() {
        Ok(())
    } else {
        Err(format!("Failed to add IP to alias: {}", response.status()))
    }
}

#[tauri::command]
pub async fn remove_ip_from_alias(database: State<'_, Database>, uuid: String, current_content: String) -> Result<(), String> {
    let api_info = database.get_default_api_info()
        .map_err(|e| format!("Failed to get API info: {}", e))?
        .ok_or_else(|| "API info not found".to_string())?;

    let url = build_api_url(&api_info, &format!("/api/firewall/alias/setItem/{}", uuid));

    // Get the alias name
    let alias_info = get_alias_info(&api_info, &uuid).await?;
    let alias_name = alias_info["alias"]["name"].as_str().unwrap_or("");

    let payload = json!({
        "alias": {
            "name": alias_name,
            "content": current_content,
        }
    });

    let response = make_http_request(
        "POST",
        &url,
        Some(payload),
        None,
        Some(30),
        Some(&api_info.api_key),
        Some(&api_info.api_secret),
    )
    .await?;

    if response.status().is_success() {
        Ok(())
    } else {
        Err(format!("Failed to remove IP from alias: {}", response.status()))
    }
}

async fn get_alias_info(api_info: &crate::db::ApiInfo, uuid: &str) -> Result<Value, String> {
    let url = build_api_url(api_info, &format!("/api/firewall/alias/getItem/{}", uuid));

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
pub async fn search_alias_items(database: State<'_, Database>) -> Result<Value, String> {
    let api_info = database.get_default_api_info()
        .map_err(|e| format!("Failed to get API info: {}", e))?
        .ok_or_else(|| "API info not found".to_string())?;

    let url = build_api_url(&api_info, "/api/firewall/alias/searchItem");

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