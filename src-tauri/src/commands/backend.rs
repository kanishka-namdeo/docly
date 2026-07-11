use std::process::{Child, Command};
use std::sync::Mutex;

pub struct BackendState {
    pub child: Mutex<Option<Child>>,
}

#[tauri::command]
pub async fn start_backend(state: tauri::State<'_, BackendState>) -> Result<(), String> {
    let mut child_lock = state.child.lock().map_err(|e| e.to_string())?;

    if child_lock.is_some() {
        return Ok(()); // Already running
    }

    // Start the Python backend
    // In production, this would use the packaged sidecar binary
    // In development, we use the venv Python directly
    let child = Command::new("python")
        .args([
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ])
        .current_dir("../backend")
        .spawn()
        .map_err(|e| format!("Failed to start backend: {}", e))?;

    *child_lock = Some(child);

    Ok(())
}

#[tauri::command]
pub async fn stop_backend(state: tauri::State<'_, BackendState>) -> Result<(), String> {
    let mut child_lock = state.child.lock().map_err(|e| e.to_string())?;

    if let Some(mut child) = child_lock.take() {
        child
            .kill()
            .map_err(|e| format!("Failed to stop backend: {}", e))?;
    }

    Ok(())
}

#[tauri::command]
pub fn open_file(path: String) -> Result<(), String> {
    open::that(&path).map_err(|e| format!("Failed to open file: {}", e))
}
