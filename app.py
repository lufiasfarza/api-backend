#!/usr/bin/env python3
"""
VPN Analytics API untuk Hybrid Approach
Track user behavior dan connection data
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import json
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

@app.route('/')
def home():
    return jsonify({
        "message": "VPN Analytics API",
        "version": "1.0.0",
        "status": "online"
    })

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

@app.route('/api/v1/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard data"""
    try:
        # Calculate average session duration
        if analytics_db["connections"]:
            avg_duration = sum(c["duration"] for c in analytics_db["connections"]) / len(analytics_db["connections"])
            avg_duration_minutes = round(avg_duration / 60000, 2)
        else:
            avg_duration_minutes = 0
        
        # Get recent connections
        recent_connections = sorted(
            analytics_db["connections"], 
            key=lambda x: x["timestamp"], 
            reverse=True
        )[:20]
        
        return jsonify({
            "success": True,
            "dashboard": {
                "total_connections": len(analytics_db["connections"]),
                "unique_users": len(analytics_db["users"]),
                "average_session_minutes": avg_duration_minutes,
                "top_countries": dict(sorted(
                    analytics_db["countries"].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5]),
                "recent_connections": recent_connections
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "connections_count": len(analytics_db["connections"])
    })

if __name__ == '__main__':
    print("🚀 Starting VPN Analytics API...")
    print("📊 Endpoints:")
    print("  POST /api/v1/track - Track connection")
    print("  GET  /api/v1/stats - Get statistics")
    print("  GET  /api/v1/dashboard - Get dashboard")
    print("  GET  /api/v1/health - Health check")
    print("")
    
    app.run(host='0.0.0.0', port=port, debug=True)