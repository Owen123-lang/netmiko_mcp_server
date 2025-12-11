# Netmiko MCP Server

MCP (Model Context Protocol) Server untuk automasi jaringan Cisco menggunakan Netmiko. Server ini mengekspos tools untuk berinteraksi dengan perangkat Cisco melalui SSH, dan dapat diakses oleh LLM clients seperti Claude Desktop.


## Yang baru dibuat

- **Get Interfaces**: Ambil daftar semua interface dan statusnya
- **Get Device Status**: Ambil informasi device (version, uptime, dll)
- **Get Running Config**: Ambil konfigurasi yang sedang berjalan
- **Interface Details**: Ambil detail spesifik untuk interface tertentu
- **Resource Monitoring**: Monitor CPU dan memory usage
- **sambungin ke claude desktop**: Komunikasi dengan router menggunakan bahasa natural melalui Claude Desktop

## harus punya....

- Python 3.8 atau lebih baru
- Akses ke Cisco DevNet Sandbox (gratis) atau perangkat Cisco lainnya
- Koneksi internet untuk DevNet Sandbox
- Claude Desktop (untuk LLM integration)

## instalasi

### 1. navigasi ke folder projek

```bash
cd netmiko_mcp_server
```

### 2. Buat virtual environment (optional)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. install requriements

```bash
pip install -r requirements.txt
```

## Konfigurasi utama untuk device 

### Menggunakan Cisco DevNet Sandbox - Catalyst 8000 Always-On

File [`config.py`](config.py) perlu dikonfigurasi dengan kredensial dari DevNet Sandbox:

1. **Login ke DevNet Sandbox**: https://devnetsandbox.cisco.com/
2. **Pilih "Catalyst 8000 Always-On Sandbox"**
3. **Launch sandbox** untuk mendapatkan kredensial unik
4. **Copy kredensial** dari Quick Access Tab
5. **Update [`config.py`](config.py)**:

```python
DEVNET_DEVICE = {
    "device_type": "cisco_ios",
    "host": "devnetsandboxiosxec8k.cisco.com",
    "port": 22,
    "username": "your_username",      # Dari DevNet Sandbox
    "password": "your_password",       # Dari DevNet Sandbox
    "secret": "your_password",
    "timeout": 30,
}
```

**Penting**: 
- Setiap user mendapat kredensial unik
- Password case-sensitive (perhatikan angka 0 vs huruf O)
- Sandbox ini VPN-less (tidak perlu VPN)

### Menggunakan Device Sendiri

Edit [`config.py`](config.py) dan ganti dengan kredensial device fisiknya nanti:

```python
DEVNET_DEVICE = {
    "device_type": "cisco_ios",  # atau cisco_xe, cisco_xr, dll
    "host": "192.168.1.1",       # IP router/switch Anda
    "port": 22,
    "username": "admin",
    "password": "your_password",
    "secret": "your_enable_password",
    "timeout": 30,
}
```

## Cara Pake

### Testing Individual Tools

Setiap tool bisa ditest secara sendiri/individu:

```bash
# Test get interfaces
python tools/get_interfaces.py

# Test device status
python tools/get_device_status.py

# Test running config
python tools/get_running_config.py
```

### Menjalankan MCP Server

```bash
python mcp_server.py
```

Server akan berjalan dan menunggu koneksi dari MCP client (seperti Claude Desktop).

## Tools yang Tersedia

### 1. `get_interfaces`
Mendapatkan daftar semua interface dari device.


### 2. `get_interface_detail`
Mendapatkan detail spesifik untuk satu interface.

**Parameters**:
- `interface_name` (required): Nama interface (contoh: "GigabitEthernet1")

**Output**: `show interface <name>`

### 3. `get_device_status`
Mendapatkan informasi umum device (version, model, uptime).

**Output**: `show version` dan hostname

### 4. `get_device_uptime`
Mendapatkan informasi uptime device.

**Output**: Uptime dari `show version`

### 5. `get_resource_usage`
Mendapatkan informasi CPU dan memory usage.

**Output**: CPU dan memory statistics

### 6. `get_running_config`
Mendapatkan running configuration.

**Parameters**:
- `filter_keyword` (optional): Filter konfigurasi (contoh: "interface", "ip")

**Output**: `show running-config` (filtered atau full)

### 7. `get_interface_config`
Mendapatkan konfigurasi untuk interface spesifik.

**Parameters**:
- `interface_name` (required): Nama interface

**Output**: `show running-config interface <name>`

### 8. `get_startup_config`
Mendapatkan startup configuration (saved config).

**Output**: `show startup-config`

## Testing

### Test Koneksi ke DevNet Sandbox

Jalankan script test yang sudah disediakan:

```bash
python test_connection.py
```


## Hasil Testing (progress day week 1)

### Test 1: Connection Test 

command: `python test_connection.py`

untuk test koneksi dasar ke cisco device, verifikasi kredensial, dan informasi umum seperti version, hostname, dan interfaces.

output:





### Test 2: Get Interfaces 

command: `python tools/get_interfaces.py`


deskripsi: Test tool untuk mendapatkan daftar semua interface dan statusnya (output dari show ip interface brief).



### Test 3: Get Device Status 

command: `python tools/get_device_status.py`

deskripsi:  Test tool untuk mendapatkan informasi device (IOS version, hostname, uptime, CPU/memory).

### Test 4: Get Running Config

command: `python tools/get_running_config.py`

deskripsi:Test tool untuk mendapatkan running configuration. Script ini akan menjalankan 2 test:

Test 1: Filtered config dengan keyword "interface"
Test 2: Config untuk specific interface (GigabitEthernet1) 

**Test 4a: Filtered Config (interface)**
command: `python test_connection.py`



### Test 5: MCP Server  

**Command**: `python mcp_server.py`

deskripsi: Menjalankan MCP server yang akan menunggu koneksi dari Claude Desktop.

## Setting buat Claude Desktop

### 1. Lokasi File Konfigurasi Claude Desktop

**Windows**:
```
%APPDATA%\Claude\claude_desktop_config.json
```
**Linux**:
```
~/.config/Claude/claude_desktop_config.json
```

### 2. Edit Konfigurasi

Tambahkan MCP server Anda ke dalam file konfigurasi:

```json
{
  "mcpServers": {
    "netmiko-cisco": {
      "command": "python",
      "args": [
        "C:\\Life\\kuliah\\RISET_ASET\\netmiko_mcp_server\\mcp_server.py"
      ],
      "env": {}
    }
  }
}
```

### 3. Restart Claude Desktop

### 4. Verifikasi

Di Claude Desktop, coba perintah seperti:

```
Get the list of interfaces from the Cisco router
```

atau

```
What is the hostname and version of the Cisco device?
```

Claude akan menggunakan tools MCP untuk mengeksekusi perintah di router.


<a href="https://ibb.co.com/HDdLrKVx"><img src="https://i.ibb.co.com/HDdLrKVx/screenshot-claude2.png" alt="screenshot-claude2" border="0"></a> 

<a href="https://ibb.co.com/DsHtBbc"><img src="https://i.ibb.co.com/DsHtBbc/screenshot-claude1.png" alt="screenshot-claude1" border="0"></a>
