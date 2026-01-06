# 📦 Easy Backup Tool
*A fast, safe, incremental backup utility for Windows*

Easy Backup Tool is a lightweight, user‑friendly application designed to protect your important files on external drives. It combines a clean PyQt6 interface with smart incremental syncing, space validation, and built‑in safety mechanisms to prevent accidental data loss.

---

## 🚀 Features v1.0.1

### 🔄 Smart Incremental Sync
- Tracks file modification times using a `manifest.json`
- Copies only new or updated files
- Saves time and reduces unnecessary disk writes

### 🛡️ Deep System Protection
- Automatically applies Windows *System* and *Read‑Only* attributes to the backup repository  
- Prevents accidental deletion or modification of backed‑up files  
- Includes a built‑in **Unlock Repository** tool for safe manual edits

### 📏 Intelligent Space Validation
- Scans all selected source folders  
- Calculates required space before copying  
- Prevents mid‑transfer failures due to insufficient disk space

### ⚔️ Conflict Resolution Engine
When a file already exists in the backup:
- **Replace**  
- **Keep Both** (adds timestamp)  
- **Skip**

### 🗂️ Repository Explorer
- Displays backed‑up folders in a tree view  
- Shows last synchronization timestamps  
- Helps you verify what’s already protected

### 🖥️ Modern PyQt6 Interface
- Clean, responsive UI  
- Custom icons and branding  
- Clear status logs during backup operations  

---

## 🧰 How to Use

1. **Select External HDD**  
   Choose the root of your backup drive. The tool automatically detects existing repositories.

2. **Add Source Folders**  
   Select one or multiple folders you want to protect.

3. **Analyze Changes (Optional)**  
   Preview how many files will be copied and how much space is required.

4. **Start Backup**  
   Runs a final space check and begins incremental syncing.

5. **Monitor Progress**  
   Watch real‑time logs at the bottom of the window.

6. **Manage Repository**  
   Use **Unlock Repository** before manually editing files.  
   Always **Lock Repository** afterward.

---

## 📁 Project Structure

