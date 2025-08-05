#!/usr/bin/env python3
"""
Hybrid VPN API Backend
API untuk aplikasi SecureVPN dengan server loading dan WireGuard configuration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import json
import os
import secrets
import base64
from collections import defaultdict

app = Flask(__name__)
CORS(app)

# Simple in-memory storage (dalam production, use database)
analytics_db = {
    "connections": [],
    "servers": defaultdict(int),
    "users": defaultdict(int),
    "countries": defaultdict(int)
}

# Mock database untuk servers (akan diganti dengan Mullvad API)
SERVERS_DB = {
    "japan-tokyo-1": {
        "id": "japan-tokyo-1",
        "name": "Tokyo 1",
        "country": "Japan",
        "city": "Tokyo",
        "flag": "🇯🇵",
        "ip": "103.21.244.1",
        "port": 51820,
        "protocol": "wireguard",
        "load": 45,
        "latency": 23,
        "isPremium": False,
        "features": ["streaming", "gaming"],
        "publicKey": "YFQoWc0bj/me5oKh1Dq70E6SEcicw6+DAjVGeDi3XbQ="
    },
    "us-newyork-1": {
        "id": "us-newyork-1", 
        "name": "New York 1",
        "country": "United States",
        "city": "New York",
        "flag": "🇺🇸",
        "ip": "104.16.124.96",
        "port": 51820,
        "protocol": "wireguard",
        "load": 67,
        "latency": 45,
        "isPremium": True,
        "features": ["streaming", "gaming", "p2p"],
        "publicKey": "YFQoWc0bj/me5oKh1Dq70E6SEcicw6+DAjVGeDi3XbQ="
    },
    "uk-london-1": {
        "id": "uk-london-1",
        "name": "London 1", 
        "country": "United Kingdom",
        "city": "London",
        "flag": "🇬🇧",
        "ip": "151.101.1.69",
        "port": 51820,
        "protocol": "wireguard",
        "load": 34,
        "latency": 67,
        "isPremium": True,
        "features": ["streaming", "gaming"],
        "publicKey": "YFQoWc0bj/me5oKh1Dq70E6SEcicw6+DAjVGeDi3XbQ="
    }
}

# Mock database untuk locations
LOCATIONS_DB = {
    "JP": {
        "code": "JP",
        "name": "Japan",
        "flag": "🇯🇵", 
        "serverCount": 3,
        "isPremium": False
    },
    "US": {
        "code": "US",
        "name": "United States",
        "flag": "🇺🇸",
        "serverCount": 5,
        "isPremium": True
    },
    "UK": {
        "code": "UK", 
        "name": "United Kingdom",
        "flag": "🇬🇧",
        "serverCount": 2,
        "isPremium": True
    }
}

@app.route('/')
def home():
    return jsonify({
        "message": "Hybrid VPN API",
        "version": "1.0.0",
        "status": "online"
    })

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "connections_count": len(analytics_db["connections"])
    })

# Hybrid VPN API Endpoints
@app.route('/api/v1/servers', methods=['GET'])
def get_servers():
    """Get list of servers untuk Hybrid VPN"""
    try:
        location = request.args.get('location')
        
        if location:
            # Filter servers by location
            filtered_servers = [
                server for server in SERVERS_DB.values()
                if server['country'].lower() == location.lower()
            ]
        else:
            # Return all servers
            filtered_servers = list(SERVERS_DB.values())
        
        return jsonify({
            "success": True,
            "servers": filtered_servers
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/v1/locations', methods=['GET'])
def get_locations():
    """Get list of locations untuk Hybrid VPN"""
    try:
        return jsonify({
            "success": True,
            "locations": list(LOCATIONS_DB.values())
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/v1/config', methods=['GET'])
def get_vpn_config():
    """Get VPN configuration untuk specific server"""
    try:
        server_id = request.args.get('server_id')
        protocol = request.args.get('protocol', 'wireguard')
        
        if not server_id or server_id not in SERVERS_DB:
            return jsonify({"success": False, "message": "Invalid server ID"}), 400
        
        server = SERVERS_DB[server_id]
        
        # Generate WireGuard config
        if protocol == 'wireguard':
            config = generate_wireguard_config(server)
        else:
            return jsonify({"success": False, "message": "Unsupported protocol"}), 400
        
        # Config expires in 1 hour
        expires_at = datetime.datetime.now() + datetime.timedelta(hours=1)
        
        return jsonify({
            "success": True,
            "config": {
                "serverId": server_id,
                "protocol": protocol,
                "config": config,
                "expiresAt": int(expires_at.timestamp() * 1000),
                "dns": ["1.1.1.1", "8.8.8.8"]
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

def generate_wireguard_config(server):
    """Generate WireGuard configuration"""
    # Generate random keys (dalam production, use proper key management)
    private_key = base64.b64encode(secrets.token_bytes(32)).decode()
    
    config = f"""[Interface]
PrivateKey = {private_key}
Address = 10.0.0.2/24
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = {server['publicKey']}
Endpoint = {server['ip']}:{server['port']}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
    return config

@app.route('/api/v1/track', methods=['POST'])
def track_connection():
    """Track VPN connection data"""
    try:
        data = request.json
        
        connection_data = {
            "server_id": data.get("server_id"),
            "server_name": data.get("server_name"),
            "country": data.get("country"),
            "duration": data.get("duration", 0),
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": data.get("user_id", "anonymous"),
            "protocol": data.get("protocol", "wireguard")
        }
        
        # Store connection
        analytics_db["connections"].append(connection_data)
        
        # Update counters
        analytics_db["servers"][connection_data["server_id"]] += 1
        analytics_db["users"][connection_data["user_id"]] += 1
        analytics_db["countries"][connection_data["country"]] += 1
        
        return jsonify({"success": True, "message": "Connection tracked"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    """Get analytics statistics"""
    try:
        total_connections = len(analytics_db["connections"])
        total_users = len(analytics_db["users"])
        total_duration = sum(c["duration"] for c in analytics_db["connections"])
        
        # Popular servers
        popular_servers = sorted(
            analytics_db["servers"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Popular countries
        popular_countries = sorted(
            analytics_db["countries"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return jsonify({
            "success": True,
            "stats": {
                "total_connections": total_connections,
                "total_users": total_users,
                "total_duration_hours": round(total_duration / 3600000, 2),
                "popular_servers": popular_servers,
                "popular_countries": popular_countries,
                "last_updated": datetime.datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == '__main__':
    print("🚀 Starting Hybrid VPN API...")
    print("📊 Endpoints:")
    print("  GET  /api/v1/health - Health check")
    print("  GET  /api/v1/servers - Get server list")
    print("  GET  /api/v1/locations - Get location list")
    print("  GET  /api/v1/config - Get VPN config")
    print("  POST /api/v1/track - Track connection")
    print("  GET  /api/v1/stats - Get statistics")
    print("")
    
    # Get port from environment variable (Railway) or use default
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug) 