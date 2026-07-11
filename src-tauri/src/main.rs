#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;

use commands::backend::{start_backend, stop_backend, open_file, BackendState};
use std::sync::Mutex;
fn main() {
    tauri::Builder::default()
        .manage(BackendState {
            child: Mutex::new(None),
        })
        .invoke_handler(tauri::generate_handler![start_backend, stop_backend, open_file])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
