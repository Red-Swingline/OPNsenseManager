mod db;
mod commands;
mod http_client;
mod devices;
mod alias;
mod dashboard;
mod firewall;
mod power;

use db::Database;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let db = Database::new(app.handle()).expect("Failed to initialize database");
            app.manage(db);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::check_first_run, 
            commands::save_initial_config, 
            commands::verify_pin, 
            commands::get_api_info, 
            commands::update_api_info,
            commands::update_pin,
            devices::get_devices,
            devices::flush_arp_table,
            commands::get_vendor_info,
            alias::list_network_aliases,
            alias::remove_ip_from_alias,
            alias::add_ip_to_alias,
            alias::get_alias,
            alias::search_alias_items,
            dashboard::get_gateway_status,  
            dashboard::get_services,    
            dashboard::restart_service,
            firewall::get_firewall_rules,
            firewall::toggle_firewall_rule,  
            firewall::apply_firewall_changes,
            power::reboot_firewall,

            ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}